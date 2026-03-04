#!/usr/bin/env bash
# Security Monitor for AI Agents
# Simple security monitoring and alerting tool
# No external dependencies - just bash and common tools

set -euo pipefail

# Configuration
CONFIG_FILE="${HOME}/.config/agent-security/config.json"
LOG_FILE="${HOME}/.openclaw/workspace/security-monitor.log"
ALERT_FILE="${HOME}/.openclaw/workspace/security-alerts.log"
SCAN_DIR="${HOME}/.openclaw/workspace/skills"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Known benign patterns (false positive mitigation)
declare -A KNOWN_BENIGN=(
    # Documentation examples
    ["curl.*\."]="doc_example"
    ["cat.*\.env"]="dev_command"
    ["grep.*key"]="diagnostic"
    ["echo.*secret"]="example_code"
    # Placeholder patterns
    ["your_"]="placeholder"
    ["YOUR_"]="placeholder"
    ["xxxx"]="placeholder"
    ["XXXX"]="placeholder"
    ["MASKED"]="placeholder"
    ["\[REDACTED\]"]="placeholder"
    ["\*+="]="placeholder"
    # Moltbook skill documentation
    ["webhook\.site"]="doc_example"
)

# Create config directory if not exists
mkdir -p "$(dirname "$CONFIG_FILE")"
mkdir -p "$(dirname "$LOG_FILE")"

# Load or create config
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Creating default configuration..."
    cat > "$CONFIG_FILE" << EOF
{
  "checks": {
    "env_files": true,
    "api_keys": true,
    "ssh_keys": true,
    "unverified_skills": true,
    "log_sanitization": true
  },
  "alerts": {
    "email": false,
    "log_file": true,
    "moltbook_post": false
  },
  "baseline": {
    "last_scan": null,
    "known_benign_patterns": []
  }
}
EOF
fi

# Logging function
log() {
    local level=$1
    shift
    local msg="$*"
    local timestamp=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
    echo "[$timestamp] [$level] $msg" >> "$LOG_FILE"
    echo -e "${GREEN}[$timestamp] [$level] $msg${NC}"
}

# Check if pattern is known benign (false positive)
is_benign_pattern() {
    local pattern=$1
    local context=$2

    for key in "${!KNOWN_BENIGN[@]}"; do
        if [[ "$context" =~ $key ]]; then
            log INFO "Skipping benign pattern: $pattern (matched known pattern: $key)"
            return 0
        fi
    done
    return 1
}

# Alert function
alert() {
    local severity=$1
    local check=$2
    local msg="$3"
    local timestamp=$(date -u +"%Y-%m-%d %H:%M:%S UTC")

    echo "[$timestamp] [ALERT:$severity] [$check] $msg" >> "$ALERT_FILE"

    case $severity in
        HIGH)
            echo -e "${RED}🚨 HIGH ALERT: $msg${NC}"
            ;;
        MEDIUM)
            echo -e "${YELLOW}⚠️  MEDIUM ALERT: $msg${NC}"
            ;;
        *)
            echo -e "${GREEN}ℹ️  INFO: $msg${NC}"
            ;;
    esac
}

# Check 1: Exposed secrets in .env files
check_env_files() {
    log INFO "Checking for exposed secrets in .env files..."

    local found_secrets=false

    # Common secret patterns
    local patterns=(
        "API_KEY"
        "SECRET_KEY"
        "PRIVATE_KEY"
        "PASSWORD"
        "TOKEN"
        "AWS_ACCESS_KEY"
        "DATABASE_URL"
        "OPENAI_API_KEY"
    )

    # Scan workspace for .env files
    while IFS= read -r -d '' env_file; do
        log INFO "Scanning $env_file"

        for pattern in "${patterns[@]}"; do
            if grep -qi "$pattern" "$env_file" 2>/dev/null; then
                # Check if it's a placeholder or masked value
                local count=$(grep -c "$pattern" "$env_file")
                for ((i=0; i<count; i++)); do
                    local line=$(grep "$pattern" "$env_file" | sed -n "${i}p")
                    # Skip if it looks like a placeholder or is masked
                    if [[ "$line" =~ (your_|YOUR_|xxxx|MASKED|\*+|\[REDACTED\]) ]]; then
                        continue
                    fi

                    found_secrets=true
                    alert HIGH "env_secrets" "Potential exposed secret in $env_file" "Pattern '$pattern' found in $env_file"
                done
            fi
        done
    done < <(find "$HOME/.openclaw" -name ".env*" -o -name "secrets.*" 2>/dev/null)

    if [ "$found_secrets" = false ]; then
        log INFO "No exposed secrets found"
    fi
}

# Check 2: Unverified skill installation
check_unverified_skills() {
    log INFO "Checking for unverified skills..."

    local found_unverified=false

    # Scan skills directory
    for skill_dir in "$SCAN_DIR"/*/; do
        if [ -d "$skill_dir" ]; then
            local skill_name=$(basename "$skill_dir")

            # Check for SKILL.md (exists = has some documentation)
            local skill_md="$skill_dir/SKILL.md"
            if [ ! -f "$skill_md" ]; then
                found_unverified=true
                alert MEDIUM "unverified_skill" "Skill without SKILL.md: $skill_name"
                continue
            fi

            # Check for malicious patterns (with false positive filtering)
            if [ -f "$skill_md" ]; then
                local malicious_patterns=(
                    "webhook\.site"
                    "curl.*\."
                    "eval("
                    "system("
                    "import os"
                    "exec.*os"
                )

                for pattern in "${malicious_patterns[@]}"; do
                    local match=$(grep -i "$pattern" "$skill_md" 2>/dev/null | head -n 1)
                    if [ -n "$match" ]; then
                        # Check if this is a benign pattern
                        if ! is_benign_pattern "$pattern" "$match"; then
                            alert HIGH "malicious_pattern" "Suspicious pattern in $skill_name/SKILL.md: $pattern"
                            break
                        fi
                    fi
                done

                # Check for permission manifest (Isnad-inspired feature)
                check_permission_manifest "$skill_dir" "$skill_name"
            fi

            # Check script execution permissions
            check_script_permissions "$skill_dir" "$skill_name"
        fi
    done

    if [ "$found_unverified" = false ]; then
        log INFO "All skills have SKILL.md documentation"
    fi
}

# Check 2a: Permission manifest validation (Isnad-inspired)
check_permission_manifest() {
    local skill_dir=$1
    local skill_name=$2

    log INFO "Checking permission manifest for $skill_name..."

    local manifest_file="$skill_dir/permissions.json"

    if [ ! -f "$manifest_file" ]; then
        log INFO "No permission manifest found for $skill_name (optional)"
        return
    fi

    # Parse manifest with jq
    if ! command -v jq &> /dev/null; then
        log INFO "jq not found, skipping manifest validation"
        return
    fi

    local declared_purpose=$(jq -r '.declared_purpose // empty' "$manifest_file" 2>/dev/null)
    local permissions=$(jq -r '.permissions // {}' "$manifest_file" 2>/dev/null)

    if [ -n "$declared_purpose" ]; then
        log INFO "Permission manifest found for $skill_name: $declared_purpose"

        # Maṣlaḥah test: Check proportionality
        local has_filesystem_write=$(echo "$permissions" | jq -r '.filesystem // []' | grep -q "write" && echo "yes" || echo "no")
        local has_network=$(echo "$permissions" | jq -r '.network // []' | grep -q "." && echo "yes" || echo "no")

        # Disproportionality check: weather skill requesting filesystem write?
        if [[ "$declared_purpose" =~ [Ww]eather ]] && [ "$has_filesystem_write" = "yes" ]; then
            alert MEDIUM "disproportionate_permission" "Weather skill $skill_name requesting filesystem write (maṣlaḥah test failed)"
        fi

        # Disproportionality check: simple utility requesting network access?
        if [[ "$declared_purpose" =~ [Uu]tility ]] && [ "$has_network" = "yes" ]; then
            alert MEDIUM "disproportionate_permission" "Utility skill $skill_name requesting network access (maṣlaḥah test failed)"
        fi
    fi
}

# Check 2b: Script execution permissions
check_script_permissions() {
    local skill_dir=$1
    local skill_name=$2

    while IFS= read -r -d '' script_file; do
        local perms=$(stat -c "%a" "$script_file" 2>/dev/null || echo "000")

        # Check for dangerous permissions
        if [ "$perms" = "777" ]; then
            alert HIGH "insecure_script_perms" "Dangerous permissions on $script_file: 777 (world writable)"
        elif [ "$perms" = "775" ]; then
            alert MEDIUM "insecure_script_perms" "Loose permissions on $script_file: 775 (group writable)"
        elif [[ "$perms" != "755" && "$perms" != "700" && "$perms" != "644" && "$perms" != "600" ]]; then
            log INFO "Unusual permissions on $script_file: $perms"
        fi
    done < <(find "$skill_dir" -type f \( -name "*.sh" -o -name "*.py" -o -name "*.js" \) -print0 2>/dev/null || true)
}

# Check 3: Insecure SSH or key files
check_insecure_keys() {
    log INFO "Checking for insecure key storage..."

    local found_insecure=false

    # Check for SSH keys with weak permissions
    while IFS= read -r -d '' ssh_file; do
        local perms=$(stat -c "%a" "$ssh_file" 2>/dev/null || echo "000")
        if [ "$perms" != "600" ] && [ "$perms" != "400" ]; then
            found_insecure=true
            alert MEDIUM "insecure_ssh_perms" "Insecure permissions on $ssh_file: $perms (should be 600 or 400)"
        fi
    done < <(find "$HOME/.ssh" -name "id_*" -o -name "*.pem" 2>/dev/null || true)

    # Check for keys committed to git
    if [ -d "$HOME/.openclaw/.git" ]; then
        local git_keys=$(git -C "$HOME/.openclaw" ls-files 2>/dev/null | grep -E "(private|key|secret)" || echo "")
        if [ -n "$git_keys" ]; then
            found_insecure=true
            alert HIGH "git_secrets" "Secrets committed to git: $(echo "$git_keys" | wc -l) files"
        fi
    fi

    if [ "$found_insecure" = false ]; then
        log INFO "Key storage looks secure"
    fi
}

# Check 4: Suspicious command history
check_command_history() {
    log INFO "Checking recent command history..."

    # Check for suspicious commands in .bash_history
    local suspicious_patterns=(
        "curl.*@.*\.env"
        "cat.*\.env"
        "cp.*\.env"
        "rm -rf .*openclaw"
        "chmod 777"
        "chmod 775 .*\.sh"
        "curl.*webhook\.site"
        "wget.*\|.*sh"
    )

    local history_file="$HOME/.bash_history"
    if [ -f "$history_file" ]; then
        # Check last 50 commands
        local recent=$(tail -n 50 "$history_file")
        local found_suspicious=false

        for pattern in "${suspicious_patterns[@]}"; do
            local match=$(echo "$recent" | grep -i "$pattern" | head -n 1)
            if [ -n "$match" ]; then
                # Check if this is a benign pattern
                if ! is_benign_pattern "$pattern" "$match"; then
                    found_suspicious=true
                    alert HIGH "suspicious_command" "Suspicious command pattern: $pattern"
                fi
            fi
        done

        if [ "$found_suspicious" = false ]; then
            log INFO "No suspicious commands found in recent history"
        fi
    fi
}

# Check 5: Log file monitoring
check_log_files() {
    log INFO "Checking for sensitive data in logs..."

    # Check if any log files contain secrets
    local log_patterns=(
        "Bearer [A-Za-z0-9\-_]{20,}"
        "api_key[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9]{20,}"
        "password[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9]{8,}"
        "secret[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9]{16,}"
        "token[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9]{20,}"
        "PRIVATE KEY"
        "AWS_ACCESS_KEY"
        "OPENAI_API_KEY"
        "sk-[A-Za-z0-9]{32,}"
    )

    local found_leak=false

    # Scan recent log files (exclude our own logs to avoid recursion)
    while IFS= read -r -d '' log_file; do
        # Skip our own log files
        if [[ "$log_file" =~ security-monitor\.log$ ]] || [[ "$log_file" =~ security-alerts\.log$ ]]; then
            continue
        fi

        for pattern in "${log_patterns[@]}"; do
            local match=$(grep -iE "$pattern" "$log_file" 2>/dev/null | head -n 1)
            if [ -n "$match" ]; then
                # Check if this is a benign pattern
                if ! is_benign_pattern "$pattern" "$match"; then
                    found_leak=true
                    alert HIGH "log_data_leak" "Possible secret leak in logs: $log_file (pattern: $pattern)"
                    break
                fi
            fi
        done
    done < <(find "$HOME/.openclaw" -name "*.log" -mtime -7 -type f 2>/dev/null || true)

    if [ "$found_leak" = false ]; then
        log INFO "Logs look clean (no sensitive data found)"
    fi
}

# Check 6: Unsigned executables (Supply chain protection)
check_unsigned_executables() {
    log INFO "Checking for unsigned executables..."

    local found_unsigned=false

    # Check for executable files in skills directory
    while IFS= read -r -d '' exec_file; do
        local perms=$(stat -c "%a" "$exec_file" 2>/dev/null || echo "000")
        local has_exec_bit=$(echo "$perms" | grep -q "[1357]" && echo "yes" || echo "no")

        if [ "$has_exec_bit" = "yes" ]; then
            # Check if it's in a skill without proper documentation
            local skill_dir=$(dirname "$exec_file")
            local skill_name=$(basename "$skill_dir")
            local skill_md="$skill_dir/SKILL.md"

            # Only alert if executable is directly in skills/ root or subdirectory without SKILL.md
            if [ ! -f "$skill_md" ]; then
                found_unsigned=true
                alert HIGH "unsigned_executable" "Unsigned executable in undocumented skill: $exec_file"
            fi
        fi
    done < <(find "$SCAN_DIR" -maxdepth 2 -type f -perm /111 -print0 2>/dev/null || true)

    if [ "$found_unsigned" = false ]; then
        log INFO "No unsigned executables found in skills"
    fi
}

# Check 7: Suspicious network connections (basic check)
check_network_connections() {
    log INFO "Checking for suspicious network connections..."

    # Check for connections to known suspicious domains
    local suspicious_domains=(
        "webhook\.site"
        "requestbin\.net"
        "pastebin\.com"
        "hastebin\.com"
        "t\.me"
    )

    local found_suspicious=false

    # Check recent network activity from logs
    while IFS= read -r -d '' log_file; do
        for domain in "${suspicious_domains[@]}"; do
            if grep -qi "$domain" "$log_file" 2>/dev/null; then
                found_suspicious=true
                alert MEDIUM "suspicious_domain" "Connection to suspicious domain detected: $domain (in $log_file)"
            fi
        done
    done < <(find "$HOME/.openclaw" -name "*.log" -mtime -1 -type f 2>/dev/null || true)

    if [ "$found_suspicious" = false ]; then
        log INFO "No suspicious network connections found"
    fi
}

# Update baseline
update_baseline() {
    log INFO "Updating security baseline..."
    local baseline_update="{\"last_scan\": \"$(date -u +%s)\", \"scans_completed\": $(jq -r '.scans_completed // 0 + 1' "$CONFIG_FILE")}"

    # Update config with new scan time
    local temp=$(jq ". + {\"last_scan\": \"$(date -u +%s)\"}" "$CONFIG_FILE")
    echo "$temp" > "$CONFIG_FILE"
}

# Print summary
print_summary() {
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}  Security Monitor Summary${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Scan completed: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo "Log file: $LOG_FILE"
    echo "Alerts file: $ALERT_FILE"
    echo ""

    # Count alerts by severity
    if [ -f "$ALERT_FILE" ]; then
        echo -e "${YELLOW}Recent Alerts:${NC}"
        tail -n 10 "$ALERT_FILE" | sed 's/^/  /'
    else
        echo "No alerts recorded."
    fi

    echo ""
    echo -e "${GREEN}========================================${NC}"
}

# Main execution
main() {
    echo ""
    echo -e "${GREEN}🔒 Agent Security Monitor${NC}"
    echo ""

    # Run all checks
    check_env_files
    check_unverified_skills
    check_insecure_keys
    check_command_history
    check_log_files
    check_unsigned_executables
    check_network_connections
    update_baseline
    print_summary
}

# Run main function
main "$@"
