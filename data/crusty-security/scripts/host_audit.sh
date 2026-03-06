#!/usr/bin/env bash
set -euo pipefail

# host_audit.sh — Comprehensive host security audit
# Usage: host_audit.sh [--help] [--deep]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/dashboard.sh" 2>/dev/null || true

# Cross-platform millisecond timestamp (macOS date doesn't support %N)
get_ms() {
  if [[ "$OSTYPE" == darwin* ]]; then
    python3 -c "import time; print(int(time.time()*1000))"
  else
    date +%s%3N
  fi
}
AUDIT_START_MS=$(get_ms)

show_help() {
    cat <<'EOF'
Usage: host_audit.sh [OPTIONS]

Run a comprehensive host security audit.

Options:
  --deep        Enable deep scanning (slower, more thorough)
  --json        JSON output (default)
  -h, --help    Show this help

Checks performed:
  - Suspicious cron jobs
  - Unexpected listening ports
  - Recently modified system files
  - Unauthorized SSH keys
  - Sensitive file permissions
  - ClamAV signature freshness
  - openclaw security audit (if available)
EOF
    exit 0
}

DEEP=false
for arg in "$@"; do
    case "$arg" in
        --deep) DEEP=true ;;
        --json) ;;
        -h|--help) show_help ;;
    esac
done

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
FINDINGS="[]"
SCORE=100

# Helper to add a finding
add_finding() {
    local severity="$1" category="$2" message="$3" details="${4:-}"
    local deduction=0
    case "$severity" in
        critical) deduction=25 ;;
        high) deduction=15 ;;
        medium) deduction=10 ;;
        low) deduction=5 ;;
        info) deduction=0 ;;
    esac
    SCORE=$((SCORE - deduction))
    [[ $SCORE -lt 0 ]] && SCORE=0

    details_escaped=$(echo "$details" | head -20 | sed 's/\\/\\\\/g; s/"/\\"/g; s/	/\\t/g' | tr '\n' '|' | sed 's/|/\\n/g')
    FINDINGS=$(echo "$FINDINGS" | python3 -c "
import json, sys
f = json.load(sys.stdin)
f.append({'severity': '$severity', 'category': '$category', 'message': $(python3 -c "import json; print(json.dumps('$message'))"), 'details': '$details_escaped'})
json.dump(f, sys.stdout)
" 2>/dev/null || echo "$FINDINGS")
}

# Detect platform
IS_MACOS=false
[[ "$(uname)" == "Darwin" ]] && IS_MACOS=true

# 1. Suspicious cron jobs / launchd persistence
check_cron() {
    local suspicious=""

    if [[ "$IS_MACOS" == true ]]; then
        # macOS: check LaunchAgents/LaunchDaemons for suspicious plists
        local plist_dirs=(
            "$HOME/Library/LaunchAgents"
            "/Library/LaunchAgents"
            "/Library/LaunchDaemons"
        )
        for pdir in "${plist_dirs[@]}"; do
            [[ -d "$pdir" ]] || continue
            while IFS= read -r plist; do
                [[ -f "$plist" ]] || continue
                if grep -qiE '(wget|curl.*\|.*sh|base64.*decode|/dev/tcp|eval|nc\s+-|ncat|mkfifo|python.*-c|osascript.*-e)' "$plist" 2>/dev/null; then
                    suspicious+="$plist\n"
                fi
            done < <(find "$pdir" -name "*.plist" -type f 2>/dev/null || true)
        done

        # Also check for crontab entries (macOS supports them too)
        local user_crontab
        user_crontab=$(crontab -l 2>/dev/null || true)
        if [[ -n "$user_crontab" ]]; then
            while IFS= read -r line; do
                if echo "$line" | grep -qiE '(wget|curl.*\|.*sh|base64.*decode|/dev/tcp|eval|nc\s+-|ncat|mkfifo)' 2>/dev/null; then
                    suspicious+="user crontab: $line\n"
                fi
            done <<< "$user_crontab"
        fi
    else
        # Linux: check crontab spool dirs
        while IFS= read -r user_cron; do
            [[ -f "$user_cron" ]] || continue
            while IFS= read -r line; do
                if echo "$line" | grep -qiE '(wget|curl.*\|.*sh|base64.*decode|/dev/tcp|eval|nc\s+-|ncat|mkfifo)' 2>/dev/null; then
                    suspicious+="$user_cron: $line\n"
                fi
            done < "$user_cron"
        done < <(find /var/spool/cron/crontabs /var/spool/cron -maxdepth 1 -type f 2>/dev/null || true)

        # Check system crontabs
        while IFS= read -r sys_cron; do
            [[ -f "$sys_cron" ]] || continue
            while IFS= read -r line; do
                if echo "$line" | grep -qiE '(wget|curl.*\|.*sh|base64.*decode|/dev/tcp|eval)' 2>/dev/null; then
                    suspicious+="$sys_cron: $line\n"
                fi
            done < "$sys_cron"
        done < <(find /etc/crontab /etc/cron.d -maxdepth 1 -type f 2>/dev/null || true)
    fi

    if [[ -n "$suspicious" ]]; then
        add_finding "high" "cron" "Suspicious scheduled jobs detected" "$suspicious"
    fi
}

# User-defined port allowlist (comma-separated)
# e.g. CRUSTY_ALLOWED_PORTS=9090,4000
_port_allowed() {
    local p="$1"
    [[ -z "${CRUSTY_ALLOWED_PORTS:-}" ]] && return 1
    IFS=',' read -ra _allowed <<< "$CRUSTY_ALLOWED_PORTS"
    for _a in "${_allowed[@]}"; do
        [[ "$p" == "$_a" ]] && return 0
    done
    return 1
}

# 2. Unexpected listening ports
check_ports() {
    local suspicious=""

    if [[ "$IS_MACOS" == true ]]; then
        # macOS: use lsof which works reliably
        local ports=""
        ports=$(lsof -iTCP -sTCP:LISTEN -nP 2>/dev/null | tail -n +2 || true)
        if [[ -n "$ports" ]]; then
            while IFS= read -r line; do
                local port
                port=$(echo "$line" | awk '{print $9}' | grep -oE '[0-9]+$' || true)
                case "$port" in
                    22|80|443|8080|8443|3000|5432|3306|6379|53|25|587|993|995|8330|18789|3334|"") ;;
                    *)
                        if [[ -n "$port" ]] && ! _port_allowed "$port"; then
                            suspicious+="$line\n"
                        fi
                        ;;
                esac
            done <<< "$ports"
        fi
    else
        # Linux: use ss or netstat
        local ports=""
        if command -v ss &>/dev/null; then
            ports=$(ss -tlnp 2>/dev/null | tail -n +2 || true)
        elif command -v netstat &>/dev/null; then
            ports=$(netstat -tlnp 2>/dev/null | tail -n +3 || true)
        fi
        if [[ -n "$ports" ]]; then
            while IFS= read -r line; do
                local port
                port=$(echo "$line" | awk '{print $4}' | grep -oE '[0-9]+$' || true)
                case "$port" in
                    22|80|443|8080|8443|3000|5432|3306|6379|53|25|587|993|995|8330|18789|3334|"") ;;
                    *)
                        if [[ -n "$port" ]] && ! _port_allowed "$port"; then
                            suspicious+="$line\n"
                        fi
                        ;;
                esac
            done <<< "$ports"
        fi
    fi

    if [[ -n "$suspicious" ]]; then
        add_finding "medium" "ports" "Unexpected listening ports detected" "$suspicious"
    fi
}

# 3. Recently modified system files
check_system_files() {
    if [[ "$DEEP" != true ]]; then
        return
    fi
    local modified=""
    # Check files modified in last 24h in sensitive dirs
    for dir in /etc /usr/bin /usr/sbin /usr/local/bin; do
        if [[ -d "$dir" ]]; then
            modified+=$(find "$dir" -type f -mtime -1 2>/dev/null | head -20 || true)
            modified+="\n"
        fi
    done

    modified=$(echo -e "$modified" | grep -v '^$' | head -20 || true)
    if [[ -n "$modified" ]] && [[ $(echo "$modified" | wc -l) -gt 3 ]]; then
        add_finding "low" "system_files" "Recently modified system files (last 24h)" "$modified"
    fi
}

# 4. SSH key audit
check_ssh_keys() {
    local issues=""
    # Check authorized_keys for all users
    local home_dirs=(/root /home/*)
    [[ "$IS_MACOS" == true ]] && home_dirs=(/Users/*)
    for home in "${home_dirs[@]}"; do
        local ak="$home/.ssh/authorized_keys"
        if [[ -f "$ak" ]]; then
            local count
            count=$(grep -c "^ssh-" "$ak" 2>/dev/null || echo "0")
            if [[ "$count" -gt 5 ]]; then
                issues+="$ak has $count keys (unusually many)\n"
            fi
            # Check for keys with no comment (suspicious)
            local no_comment
            no_comment=$(grep "^ssh-" "$ak" 2>/dev/null | grep -cvE '\S+\s+\S+\s+\S' || echo "0")
            if [[ "$no_comment" -gt 0 ]]; then
                issues+="$ak has $no_comment keys without comments\n"
            fi
        fi
    done

    # Check if root login is allowed
    if [[ -f /etc/ssh/sshd_config ]]; then
        if grep -qE "^PermitRootLogin\s+yes" /etc/ssh/sshd_config 2>/dev/null; then
            issues+="Root SSH login is enabled\n"
            add_finding "medium" "ssh" "Root SSH login is enabled" ""
        fi
    fi

    if [[ -n "$issues" ]]; then
        add_finding "medium" "ssh" "SSH key concerns detected" "$issues"
    fi
}

# 5. File permissions
check_permissions() {
    local issues=""
    # World-writable sensitive files
    local sensitive_files=(/etc/passwd /etc/shadow /etc/sudoers /etc/ssh/sshd_config)
    # macOS doesn't use /etc/shadow — uses Directory Services
    [[ "$IS_MACOS" == true ]] && sensitive_files=(/etc/passwd /etc/sudoers /etc/ssh/sshd_config)
    for f in "${sensitive_files[@]}"; do
        if [[ -f "$f" ]]; then
            local perms
            perms=$(stat -c "%a" "$f" 2>/dev/null || stat -f "%Lp" "$f" 2>/dev/null || true)
            if [[ -n "$perms" ]]; then
                local other=$((perms % 10))
                # Write bit = 2. Check if bit 1 (write) is set: 2,3,6,7
                if (( other & 2 )); then
                    issues+="$f is world-writable (perms: $perms)\n"
                fi
            fi
        fi
    done

    # Check /tmp sticky bit
    if [[ -d /tmp ]]; then
        local tmp_perms
        tmp_perms=$(stat -c "%a" /tmp 2>/dev/null || stat -f "%Lp" /tmp 2>/dev/null || true)
        if [[ -n "$tmp_perms" && ! "$tmp_perms" =~ ^1 ]] && [[ ${#tmp_perms} -eq 4 ]]; then
            issues+="/tmp missing sticky bit\n"
        fi
    fi

    if [[ -n "$issues" ]]; then
        add_finding "high" "permissions" "Sensitive file permission issues" "$issues"
    fi
}

# 6. ClamAV signature freshness
check_clamav() {
    if ! command -v clamscan &>/dev/null; then
        add_finding "medium" "clamav" "ClamAV is not installed" ""
        return
    fi

    # Check signature age
    local db_dir="/var/lib/clamav"
    [[ -d "$db_dir" ]] || db_dir="/usr/local/var/lib/clamav"
    [[ -d "$db_dir" ]] || db_dir="/opt/homebrew/var/lib/clamav"

    if [[ -d "$db_dir" ]]; then
        local main_db="$db_dir/main.cvd"
        [[ -f "$main_db" ]] || main_db="$db_dir/main.cld"
        if [[ -f "$main_db" ]]; then
            local age_days
            age_days=$(( ($(date +%s) - $(stat -c %Y "$main_db" 2>/dev/null || stat -f %m "$main_db" 2>/dev/null || echo "0")) / 86400 ))
            if [[ "$age_days" -gt 7 ]]; then
                add_finding "medium" "clamav" "ClamAV signatures are ${age_days} days old (>7 days)" "Run: sudo freshclam"
            elif [[ "$age_days" -gt 1 ]]; then
                add_finding "low" "clamav" "ClamAV signatures are ${age_days} days old" ""
            fi
        else
            add_finding "high" "clamav" "ClamAV signature database not found" "Run: sudo freshclam"
        fi
    fi
}

# 7. macOS-specific security checks
check_macos_security() {
    [[ "$IS_MACOS" != true ]] && return

    # System Integrity Protection (SIP)
    local sip_status
    sip_status=$(csrutil status 2>/dev/null || true)
    if [[ -n "$sip_status" ]]; then
        if echo "$sip_status" | grep -qi "disabled"; then
            add_finding "critical" "macos_sip" "System Integrity Protection (SIP) is DISABLED" "SIP protects system files from modification. Re-enable: boot to Recovery, run csrutil enable"
        fi
    fi

    # Gatekeeper
    local gk_status
    gk_status=$(spctl --status 2>/dev/null || true)
    if [[ -n "$gk_status" ]]; then
        if echo "$gk_status" | grep -qi "disabled"; then
            add_finding "high" "macos_gatekeeper" "Gatekeeper is DISABLED" "Gatekeeper blocks unsigned/unnotarized apps. Re-enable: sudo spctl --master-enable"
        fi
    fi

    # FileVault (disk encryption)
    local fv_status
    fv_status=$(fdesetup status 2>/dev/null || true)
    if [[ -n "$fv_status" ]]; then
        if echo "$fv_status" | grep -qi "off"; then
            add_finding "high" "macos_filevault" "FileVault disk encryption is OFF" "Enable via System Settings > Privacy & Security > FileVault"
        fi
    fi

    # Application Firewall
    local fw_status
    fw_status=$(/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null || true)
    if [[ -n "$fw_status" ]]; then
        if echo "$fw_status" | grep -qi "disabled"; then
            add_finding "medium" "macos_firewall" "macOS Application Firewall is DISABLED" "Enable via System Settings > Network > Firewall, or: sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on"
        fi
    fi

    # Remote Login (SSH)
    local remote_login
    remote_login=$(systemsetup -getremotelogin 2>/dev/null || true)
    if echo "$remote_login" | grep -qi "on"; then
        add_finding "low" "macos_remote_login" "Remote Login (SSH) is enabled" "Disable if not needed: System Settings > General > Sharing > Remote Login"
    fi
}

# Run all checks
check_cron
check_ports
check_system_files
check_ssh_keys
check_permissions
check_clamav
check_macos_security

# Run openclaw security audit if available
OPENCLAW_AUDIT=""
if command -v openclaw &>/dev/null; then
    if [[ "$DEEP" == true ]]; then
        OPENCLAW_AUDIT=$(openclaw security audit --deep 2>/dev/null || echo "")
    else
        OPENCLAW_AUDIT=$(openclaw security audit 2>/dev/null || echo "")
    fi
fi

# Output
cat <<EOF
{
  "timestamp": "$TIMESTAMP",
  "posture_score": $SCORE,
  "findings_count": $(echo "$FINDINGS" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 0),
  "findings": $FINDINGS,
  "deep_scan": $DEEP,
  "openclaw_audit_available": $(command -v openclaw &>/dev/null && echo true || echo false)
}
EOF

# Push to dashboard
AUDIT_DURATION=$(($(get_ms) - ${AUDIT_START_MS:-0}))
[[ "$AUDIT_DURATION" =~ ^[0-9]+$ ]] || AUDIT_DURATION=0
AUDIT_STATUS="clean"
AUDIT_SEVERITY="none"
[[ $SCORE -lt 50 ]] && AUDIT_STATUS="suspicious" && AUDIT_SEVERITY="high"
[[ $SCORE -lt 75 && $SCORE -ge 50 ]] && AUDIT_SEVERITY="medium"

FINDINGS_COUNT=$(echo "$FINDINGS" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))" 2>/dev/null || echo 0)
AUDIT_RESULTS="{\"posture_score\":$SCORE,\"findings_count\":$FINDINGS_COUNT,\"deep_scan\":$DEEP}"
cg_push_scan "host_audit" "$(hostname 2>/dev/null || echo 'host')" "$AUDIT_STATUS" "Crusty Security Host Audit" "$AUDIT_SEVERITY" "$AUDIT_DURATION" "$AUDIT_RESULTS" 2>/dev/null || true

# Exit code based on score
# Exit 0 = script ran successfully (use JSON posture_score for severity)
# Exit 1 reserved for runtime/execution errors only
exit 0
