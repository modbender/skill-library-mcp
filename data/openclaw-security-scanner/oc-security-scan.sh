#!/usr/bin/env bash
# ============================================================================
# OpenClaw Security Scanner
# Version: 1.0.0
# License: MIT
#
# A comprehensive, local-only security assessment tool for OpenClaw.
# - No data leaves the machine
# - Read-only by default (--fix to remediate)
# - Run by the OpenClaw owner on their own machine
# ============================================================================

set -euo pipefail

# ---------------------------------------------------------------------------
# Globals
# ---------------------------------------------------------------------------
VERSION="1.0.0"
SCRIPT_NAME="$(basename "$0")"
OS="$(uname -s)"

# Flags
FLAG_FIX=false
FLAG_JSON=false
FLAG_REPORT=false
FLAG_QUIET=false

# OpenClaw paths (defaults, overridden by detection)
OC_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
OC_CONFIG="$OC_HOME/openclaw.json"
OC_SECRETS="$OC_HOME/secrets.env"
OC_WORKSPACE="$OC_HOME/workspace"

# Scoring
TOTAL_POINTS=0
EARNED_POINTS=0
FINDINGS=()        # Array of JSON finding objects for --json
CRITICAL_COUNT=0
WARNING_COUNT=0
PASS_COUNT=0
INFO_COUNT=0

# Colors (disabled if not a tty or --json)
if [[ -t 1 ]] && [[ "${FLAG_JSON}" == false ]]; then
    RED='\033[0;31m'
    YELLOW='\033[0;33m'
    GREEN='\033[0;32m'
    GRAY='\033[0;37m'
    BOLD='\033[1m'
    DIM='\033[2m'
    RESET='\033[0m'
else
    RED='' YELLOW='' GREEN='' GRAY='' BOLD='' DIM='' RESET=''
fi

# Report buffer
REPORT_BUF=""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
usage() {
    cat <<EOF
${BOLD}OpenClaw Security Scanner v${VERSION}${RESET}

Usage: ${SCRIPT_NAME} [OPTIONS]

Options:
  --fix       Apply safe fixes (prompts before each change)
  --json      Output findings as JSON
  --report    Save timestamped report to file
  --quiet     Suppress banner and section headers
  --help      Show this help message

Environment:
  OPENCLAW_HOME   Override OpenClaw directory (default: ~/.openclaw)

Examples:
  ${SCRIPT_NAME}                  # Standard scan
  ${SCRIPT_NAME} --fix            # Scan and offer fixes
  ${SCRIPT_NAME} --json --report  # JSON output saved to file
EOF
    exit 0
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --fix)    FLAG_FIX=true ;;
            --json)   FLAG_JSON=true; RED=''; YELLOW=''; GREEN=''; GRAY=''; BOLD=''; DIM=''; RESET='' ;;
            --report) FLAG_REPORT=true ;;
            --quiet)  FLAG_QUIET=true ;;
            --help|-h) usage ;;
            *) echo "Unknown option: $1"; usage ;;
        esac
        shift
    done
}

# Output a line to both stdout and report buffer
out() {
    local line="$1"
    if [[ "$FLAG_JSON" == false ]]; then
        echo -e "$line"
    fi
    # Strip ANSI for report
    REPORT_BUF+="$(echo -e "$line" | sed 's/\x1b\[[0-9;]*m//g')"$'\n'
}

banner() {
    [[ "$FLAG_QUIET" == true ]] && return
    out ""
    out "${BOLD}╔══════════════════════════════════════════════════════╗${RESET}"
    out "${BOLD}║         🔒 OpenClaw Security Scanner v${VERSION}         ║${RESET}"
    out "${BOLD}║    Local-only · Read-only · Owner-operated           ║${RESET}"
    out "${BOLD}╚══════════════════════════════════════════════════════╝${RESET}"
    out ""
    out "${DIM}OS: ${OS} | Home: ${OC_HOME} | $(date '+%Y-%m-%d %H:%M:%S %Z')${RESET}"
    out ""
}

section() {
    [[ "$FLAG_QUIET" == true ]] && return
    out ""
    out "${BOLD}━━━ $1 ━━━${RESET}"
}

# Record a finding
# Usage: finding SEVERITY "title" "description" "recommendation" ["fix_cmd"]
finding() {
    local severity="$1" title="$2" desc="$3" rec="$4" fix_cmd="${5:-}"

    local icon points_possible points_earned
    case "$severity" in
        CRITICAL) icon="🔴"; points_possible=10; points_earned=0; ((CRITICAL_COUNT++)) || true ;;
        WARNING)  icon="🟡"; points_possible=5;  points_earned=0; ((WARNING_COUNT++)) || true ;;
        PASS)     icon="🟢"; points_possible=5;  points_earned=5; ((PASS_COUNT++)) || true ;;
        INFO)     icon="⚪"; points_possible=0;  points_earned=0; ((INFO_COUNT++)) || true ;;
        *) icon="❓"; points_possible=0; points_earned=0 ;;
    esac

    TOTAL_POINTS=$((TOTAL_POINTS + points_possible))
    EARNED_POINTS=$((EARNED_POINTS + points_earned))

    if [[ "$FLAG_JSON" == false ]]; then
        out "  ${icon} ${BOLD}${severity}${RESET}: ${title}"
        [[ -n "$desc" ]] && out "     ${desc}"
        if [[ "$severity" != "PASS" && "$severity" != "INFO" ]]; then
            [[ -n "$rec" ]] && out "     ${DIM}→ ${rec}${RESET}"
            [[ -n "$fix_cmd" ]] && out "     ${DIM}  Fix: ${fix_cmd}${RESET}"
        fi
    fi

    # Store JSON finding
    local json_fix=""
    [[ -n "$fix_cmd" ]] && json_fix=", \"fix\": \"$(echo "$fix_cmd" | sed 's/"/\\"/g')\""
    FINDINGS+=("{\"severity\": \"${severity}\", \"title\": \"$(echo "$title" | sed 's/"/\\"/g')\", \"description\": \"$(echo "$desc" | sed 's/"/\\"/g')\", \"recommendation\": \"$(echo "$rec" | sed 's/"/\\"/g')\"${json_fix}}")

    # Offer fix if --fix and fix_cmd provided and not PASS/INFO
    if [[ "$FLAG_FIX" == true && -n "$fix_cmd" && "$severity" != "PASS" && "$severity" != "INFO" ]]; then
        echo -en "     ${YELLOW}Apply fix? [y/N]:${RESET} "
        read -r ans
        if [[ "$ans" =~ ^[Yy]$ ]]; then
            eval "$fix_cmd" && echo -e "     ${GREEN}✓ Fixed${RESET}" || echo -e "     ${RED}✗ Fix failed${RESET}"
        fi
    fi
}

# Utility: check file permissions (returns octal perms)
file_perms() {
    if [[ "$OS" == "Darwin" ]]; then
        stat -f '%Lp' "$1" 2>/dev/null
    else
        stat -c '%a' "$1" 2>/dev/null
    fi
}

# Utility: check if a file is world-readable
is_world_readable() {
    local perms
    perms="$(file_perms "$1")"
    [[ -n "$perms" ]] && (( (8#$perms & 8#004) != 0 ))
}

# Utility: get token entropy estimate (character count as rough proxy)
token_strength() {
    local token="$1"
    local len=${#token}
    if (( len < 16 )); then echo "weak"
    elif (( len < 32 )); then echo "moderate"
    else echo "strong"
    fi
}

# Utility: read a JSON key simply (no jq dependency)
json_val() {
    local key="$1" file="$2"
    local raw
    raw="$(grep -o "\"${key}\"[[:space:]]*:[[:space:]]*\"[^\"]*\"" "$file" 2>/dev/null || true)"
    [[ -z "$raw" ]] && return 0
    echo "$raw" | head -1 | sed 's/.*: *"//;s/"//'
}

json_val_raw() {
    local key="$1" file="$2"
    local raw
    raw="$(grep -o "\"${key}\"[[:space:]]*:[[:space:]]*[^,}]*" "$file" 2>/dev/null || true)"
    [[ -z "$raw" ]] && return 0
    echo "$raw" | head -1 | sed 's/.*: *//' | tr -d '" '
}

# ---------------------------------------------------------------------------
# CHECK FUNCTIONS
# ---------------------------------------------------------------------------

check_openclaw_config() {
    section "OpenClaw Configuration"

    # --- Config file exists ---
    if [[ ! -f "$OC_CONFIG" ]]; then
        finding INFO "Config file not found" "$OC_CONFIG does not exist" "Using alternative config location or defaults"
        # Try alternate locations
        for alt in "$OC_HOME/config.json" "$HOME/.config/openclaw/openclaw.json"; do
            if [[ -f "$alt" ]]; then
                OC_CONFIG="$alt"
                finding INFO "Found config at alternate location" "$alt" ""
                break
            fi
        done
    fi

    if [[ -f "$OC_CONFIG" ]]; then
        # --- Config file permissions ---
        local perms
        perms="$(file_perms "$OC_CONFIG")"
        if is_world_readable "$OC_CONFIG"; then
            finding WARNING "Config file is world-readable" "Permissions: ${perms} on ${OC_CONFIG}" \
                "Restrict to owner-only: chmod 600" "chmod 600 '${OC_CONFIG}'"
        else
            finding PASS "Config file permissions" "Permissions: ${perms}" ""
        fi

        # --- Gateway bind address ---
        local bind_addr
        bind_addr="$(json_val "host" "$OC_CONFIG")"
        [[ -z "$bind_addr" ]] && bind_addr="$(json_val "bind" "$OC_CONFIG")"
        [[ -z "$bind_addr" ]] && bind_addr="$(json_val "address" "$OC_CONFIG")"

        if [[ "$bind_addr" == "0.0.0.0" ]]; then
            finding CRITICAL "Gateway bound to 0.0.0.0" "Gateway is listening on ALL interfaces — exposed to network" \
                "Bind to 127.0.0.1 (localhost) in config" ""
        elif [[ "$bind_addr" == "127.0.0.1" || "$bind_addr" == "localhost" || -z "$bind_addr" ]]; then
            finding PASS "Gateway bind address" "Bound to localhost (or default)" ""
        else
            finding WARNING "Gateway bind address: ${bind_addr}" "Non-standard bind address" \
                "Verify this is intentional; prefer 127.0.0.1" ""
        fi

        # --- Gateway token strength ---
        local gw_token
        gw_token="$(json_val "token" "$OC_CONFIG")"
        [[ -z "$gw_token" ]] && gw_token="$(json_val "gatewayToken" "$OC_CONFIG")"
        if [[ -n "$gw_token" ]]; then
            local strength
            strength="$(token_strength "$gw_token")"
            if [[ "$strength" == "weak" ]]; then
                finding CRITICAL "Weak gateway token" "Token is less than 16 characters" \
                    "Generate a strong token: openssl rand -hex 32" ""
            elif [[ "$strength" == "moderate" ]]; then
                finding WARNING "Moderate gateway token" "Token is 16-31 characters" \
                    "Consider a longer token: openssl rand -hex 32" ""
            else
                finding PASS "Gateway token strength" "Token is 32+ characters" ""
            fi
        else
            finding INFO "No gateway token found in config" "Token may be set via environment variable" ""
        fi

        # --- Exec security mode ---
        local exec_mode
        exec_mode="$(json_val_raw "security" "$OC_CONFIG")"
        [[ -z "$exec_mode" ]] && exec_mode="$(json_val "execSecurity" "$OC_CONFIG")"
        if [[ "$exec_mode" == "full" ]]; then
            finding WARNING "Exec security mode is 'full'" "Agent can execute arbitrary commands" \
                "Consider 'allowlist' or 'deny' mode for tighter control" ""
        elif [[ "$exec_mode" == "deny" ]]; then
            finding PASS "Exec security mode: deny" "Command execution is restricted" ""
        elif [[ "$exec_mode" == "allowlist" ]]; then
            finding PASS "Exec security mode: allowlist" "Only approved commands allowed" ""
        else
            finding INFO "Exec security mode not explicitly set" "Check OpenClaw defaults for your version" ""
        fi
    fi

    # --- Secrets file ---
    if [[ -f "$OC_SECRETS" ]]; then
        local sec_perms
        sec_perms="$(file_perms "$OC_SECRETS")"
        if is_world_readable "$OC_SECRETS"; then
            finding CRITICAL "secrets.env is world-readable" "Permissions: ${sec_perms} — anyone on the system can read your secrets" \
                "chmod 600 secrets.env" "chmod 600 '${OC_SECRETS}'"
        elif (( (8#$sec_perms & 8#070) != 0 )); then
            finding WARNING "secrets.env is group-readable" "Permissions: ${sec_perms}" \
                "chmod 600 secrets.env" "chmod 600 '${OC_SECRETS}'"
        else
            finding PASS "secrets.env permissions" "Permissions: ${sec_perms}" ""
        fi

        # Check for plaintext API keys
        local key_count
        key_count=$(grep -cEi '(api_key|api_secret|token|password|secret)=' "$OC_SECRETS" 2>/dev/null || true)
        if (( key_count > 0 )); then
            finding INFO "secrets.env contains ${key_count} credential(s)" \
                "Ensure this file has strict permissions and is not committed to git" ""
        fi
    else
        finding INFO "No secrets.env found" "$OC_SECRETS does not exist" ""
    fi

    # --- Workspace permissions ---
    if [[ -d "$OC_WORKSPACE" ]]; then
        local ws_perms
        ws_perms="$(file_perms "$OC_WORKSPACE")"
        if is_world_readable "$OC_WORKSPACE"; then
            finding WARNING "Workspace is world-readable" "Permissions: ${ws_perms} on ${OC_WORKSPACE}" \
                "chmod 700 workspace directory" "chmod 700 '${OC_WORKSPACE}'"
        else
            finding PASS "Workspace directory permissions" "Permissions: ${ws_perms}" ""
        fi
    fi
}

check_network() {
    section "Network Exposure"

    # --- Listening ports on public interfaces ---
    local public_listeners=""
    if command -v lsof &>/dev/null; then
        # Get non-localhost listeners
        public_listeners=$(lsof -iTCP -sTCP:LISTEN -nP 2>/dev/null | grep -v '127\.0\.0\.1\|localhost\|\[::1\]' | grep -v '^COMMAND' || true)
    elif command -v ss &>/dev/null; then
        public_listeners=$(ss -tlnp 2>/dev/null | grep -v '127\.0\.0\.1\|::1' | tail -n +2 || true)
    fi

    if [[ -n "$public_listeners" ]]; then
        local count
        count=$(echo "$public_listeners" | wc -l | tr -d ' ')
        finding WARNING "${count} service(s) listening on public interfaces" \
            "$(echo "$public_listeners" | head -5 | awk '{print $1, $9}' | tr '\n' '; ')" \
            "Review and restrict to localhost where possible" ""
    else
        finding PASS "No services exposed on public interfaces" "" ""
    fi

    # --- Check if OpenClaw port is publicly exposed ---
    local oc_port=""
    if [[ -f "$OC_CONFIG" ]]; then
        oc_port="$(json_val_raw "port" "$OC_CONFIG")"
    fi
    [[ -z "$oc_port" ]] && oc_port="18789"  # common default

    local oc_exposed=""
    if command -v lsof &>/dev/null; then
        oc_exposed=$(lsof -iTCP:"$oc_port" -sTCP:LISTEN -nP 2>/dev/null | grep -v '127\.0\.0\.1\|localhost\|\[::1\]' || true)
    fi
    if [[ -n "$oc_exposed" ]]; then
        finding CRITICAL "OpenClaw port ${oc_port} exposed on public interface" \
            "$(echo "$oc_exposed" | head -1)" \
            "Bind gateway to 127.0.0.1 in config" ""
    else
        finding PASS "OpenClaw port ${oc_port} not publicly exposed" "" ""
    fi

    # --- Firewall status ---
    if [[ "$OS" == "Darwin" ]]; then
        local fw_status
        fw_status=$(/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null || echo "unknown")
        if echo "$fw_status" | grep -qi "enabled"; then
            finding PASS "macOS Application Firewall is enabled" "" ""
        elif echo "$fw_status" | grep -qi "disabled"; then
            finding WARNING "macOS Application Firewall is disabled" "" \
                "Enable: sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on" ""
        else
            finding INFO "Could not determine firewall status" "May require root" ""
        fi
    else
        # Linux: check ufw, then iptables
        if command -v ufw &>/dev/null; then
            local ufw_status
            ufw_status=$(ufw status 2>/dev/null | head -1 || echo "unknown")
            if echo "$ufw_status" | grep -qi "active"; then
                finding PASS "UFW firewall is active" "" ""
            else
                finding WARNING "UFW firewall is inactive" "" \
                    "Enable: sudo ufw enable" ""
            fi
        elif command -v iptables &>/dev/null; then
            local rules_count
            rules_count=$(iptables -L 2>/dev/null | grep -c '^[A-Z]' || echo "0")
            if (( rules_count > 3 )); then
                finding PASS "iptables has rules configured" "" ""
            else
                finding WARNING "iptables appears to have minimal rules" "" \
                    "Configure firewall rules" ""
            fi
        else
            finding INFO "No firewall tool detected" "" "Install and configure ufw or iptables"
        fi
    fi

    # --- SSH configuration ---
    local sshd_config="/etc/ssh/sshd_config"
    if [[ -f "$sshd_config" ]] && [[ -r "$sshd_config" ]]; then
        # Password auth
        local pass_auth
        pass_auth=$(grep -i "^PasswordAuthentication" "$sshd_config" 2>/dev/null | awk '{print $2}' || true)
        if [[ "$pass_auth" == "yes" ]]; then
            finding WARNING "SSH password authentication is enabled" "" \
                "Set PasswordAuthentication no in sshd_config" ""
        elif [[ "$pass_auth" == "no" ]]; then
            finding PASS "SSH password authentication disabled" "" ""
        fi

        # Root login
        local root_login
        root_login=$(grep -i "^PermitRootLogin" "$sshd_config" 2>/dev/null | awk '{print $2}' || true)
        if [[ "$root_login" == "yes" ]]; then
            finding WARNING "SSH root login is permitted" "" \
                "Set PermitRootLogin no in sshd_config" ""
        elif [[ -n "$root_login" ]]; then
            finding PASS "SSH root login restricted (${root_login})" "" ""
        fi
    else
        finding INFO "SSH config not readable" "May require root for deeper SSH checks" ""
    fi
}

check_credentials() {
    section "Credential Hygiene"

    # --- Scan for API keys in common files ---
    local sensitive_files=()
    for f in "$OC_HOME"/*.json "$OC_HOME"/*.env "$OC_HOME"/*.yaml "$OC_HOME"/*.yml "$OC_HOME"/*.toml; do
        [[ -f "$f" ]] && sensitive_files+=("$f")
    done

    for f in "${sensitive_files[@]}"; do
        local perms
        perms="$(file_perms "$f")"
        if is_world_readable "$f"; then
            finding WARNING "Sensitive file world-readable: $(basename "$f")" \
                "Permissions: ${perms}" \
                "chmod 600 $(basename "$f")" "chmod 600 '${f}'"
        fi
    done

    # --- Check .gitignore in workspace ---
    if [[ -d "$OC_WORKSPACE/.git" ]]; then
        local gitignore="$OC_WORKSPACE/.gitignore"
        if [[ -f "$gitignore" ]]; then
            local missing_patterns=()
            for pattern in "secrets.env" "*.env" ".env" "tokens" "*.key" "*.pem"; do
                if ! grep -qF "$pattern" "$gitignore" 2>/dev/null; then
                    missing_patterns+=("$pattern")
                fi
            done
            if (( ${#missing_patterns[@]} > 0 )); then
                finding WARNING ".gitignore missing secret patterns" \
                    "Missing: ${missing_patterns[*]}" \
                    "Add patterns to .gitignore" \
                    "echo -e '${missing_patterns[*]// /\\n}' >> '${gitignore}'"
            else
                finding PASS ".gitignore covers secret file patterns" "" ""
            fi
        else
            finding WARNING "No .gitignore in git workspace" \
                "Secrets could accidentally be committed" \
                "Create .gitignore with secret patterns" ""
        fi
    fi

    # --- Check for secrets in workspace memory files ---
    if [[ -d "$OC_WORKSPACE/memory" ]]; then
        local mem_perms
        mem_perms="$(file_perms "$OC_WORKSPACE/memory")"
        if is_world_readable "$OC_WORKSPACE/memory"; then
            finding WARNING "Memory directory is world-readable" \
                "Permissions: ${mem_perms}" \
                "chmod 700 memory/" "chmod 700 '${OC_WORKSPACE}/memory'"
        else
            finding PASS "Memory directory permissions" "Permissions: ${mem_perms}" ""
        fi

        # Quick scan for obvious secrets in memory files
        local secret_hits=0
        while IFS= read -r -d '' mf; do
            if grep -qEi '(sk-[a-zA-Z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36})' "$mf" 2>/dev/null; then
                ((secret_hits++)) || true
            fi
        done < <(find "$OC_WORKSPACE/memory" -type f -name '*.md' -print0 2>/dev/null)

        if (( secret_hits > 0 )); then
            finding WARNING "${secret_hits} memory file(s) may contain API keys" \
                "Detected patterns matching API key formats" \
                "Review and remove secrets from memory files" ""
        else
            finding PASS "No obvious API keys in memory files" "" ""
        fi
    fi
}

check_os_hardening() {
    section "OS Hardening"

    # --- Disk encryption ---
    if [[ "$OS" == "Darwin" ]]; then
        local fv_status
        fv_status=$(fdesetup status 2>/dev/null || echo "unknown")
        if echo "$fv_status" | grep -qi "on"; then
            finding PASS "FileVault disk encryption is ON" "" ""
        elif echo "$fv_status" | grep -qi "off"; then
            finding WARNING "FileVault disk encryption is OFF" \
                "Data at rest is unencrypted" \
                "Enable: System Settings → Privacy & Security → FileVault" ""
        else
            finding INFO "Could not determine FileVault status" "" ""
        fi
    else
        # Linux: check for LUKS
        if command -v lsblk &>/dev/null && lsblk -o TYPE 2>/dev/null | grep -q crypt; then
            finding PASS "LUKS disk encryption detected" "" ""
        elif [[ -d /sys/block ]] && dmsetup ls --target crypt &>/dev/null 2>&1 | grep -q .; then
            finding PASS "Encrypted volumes detected" "" ""
        else
            finding WARNING "No disk encryption detected" \
                "Data at rest may be unencrypted" \
                "Enable full-disk encryption (LUKS)" ""
        fi
    fi

    # --- Auto updates ---
    if [[ "$OS" == "Darwin" ]]; then
        local auto_update
        auto_update=$(defaults read /Library/Preferences/com.apple.SoftwareUpdate AutomaticCheckEnabled 2>/dev/null || echo "unknown")
        if [[ "$auto_update" == "1" ]]; then
            finding PASS "Automatic update checks enabled" "" ""
        elif [[ "$auto_update" == "0" ]]; then
            finding WARNING "Automatic update checks disabled" "" \
                "Enable in System Settings → Software Update" ""
        else
            finding INFO "Could not determine auto-update status" "" ""
        fi
    else
        if [[ -f /etc/apt/apt.conf.d/20auto-upgrades ]]; then
            if grep -q 'APT::Periodic::Unattended-Upgrade "1"' /etc/apt/apt.conf.d/20auto-upgrades 2>/dev/null; then
                finding PASS "Unattended upgrades enabled" "" ""
            else
                finding WARNING "Unattended upgrades not enabled" "" \
                    "Enable: sudo dpkg-reconfigure unattended-upgrades" ""
            fi
        else
            finding INFO "Could not determine auto-update configuration" "" ""
        fi
    fi

    # --- OS version ---
    if [[ "$OS" == "Darwin" ]]; then
        local os_ver
        os_ver=$(sw_vers -productVersion 2>/dev/null || echo "unknown")
        finding INFO "macOS version: ${os_ver}" "" ""
    else
        if [[ -f /etc/os-release ]]; then
            local os_name os_ver
            os_name=$(grep '^PRETTY_NAME=' /etc/os-release | cut -d'"' -f2)
            finding INFO "OS: ${os_name}" "" ""
        fi
    fi

    # --- Running as root check ---
    if [[ "$(id -u)" == "0" ]]; then
        finding WARNING "Running as root" "Operating as root increases risk of accidental damage" \
            "Run OpenClaw as a regular user" ""
    else
        finding PASS "Running as non-root user ($(whoami))" "" ""
    fi
}

check_agent_guardrails() {
    section "Agent Guardrails"

    # --- RULES.md ---
    local rules_found=false
    for loc in "$OC_WORKSPACE/RULES.md" "$OC_HOME/RULES.md" "$OC_WORKSPACE/rules.md"; do
        if [[ -f "$loc" ]]; then
            rules_found=true
            finding PASS "RULES.md found" "$(basename "$loc") at $(dirname "$loc")" ""

            # Check if it has meaningful content
            local lines
            lines=$(wc -l < "$loc" | tr -d ' ')
            if (( lines < 3 )); then
                finding WARNING "RULES.md is very short (${lines} lines)" \
                    "May not provide sufficient safety constraints" \
                    "Add explicit rules for agent behavior" ""
            fi
            break
        fi
    done
    if [[ "$rules_found" == false ]]; then
        finding WARNING "No RULES.md found" \
            "Agent has no explicit safety constraints file" \
            "Create RULES.md with behavioral boundaries" ""
    fi

    # --- AGENTS.md ---
    if [[ -f "$OC_WORKSPACE/AGENTS.md" ]]; then
        finding PASS "AGENTS.md found" "Agent configuration exists" ""
    fi

    # --- Elevated exec permissions ---
    if [[ -f "$OC_CONFIG" ]]; then
        local elevated
        elevated=$(json_val_raw "elevated" "$OC_CONFIG")
        if [[ "$elevated" == "true" ]]; then
            finding WARNING "Elevated exec permissions enabled" \
                "Agent can run commands with elevated privileges" \
                "Disable unless absolutely necessary" ""
        fi

        # --- Browser control ---
        local browser_enabled
        browser_enabled=$(json_val_raw "browser" "$OC_CONFIG")
        if [[ "$browser_enabled" == "true" ]]; then
            finding INFO "Browser control is enabled" \
                "Agent can interact with web browsers" ""
        fi
    fi

    # --- Memory file permissions ---
    if [[ -d "$OC_WORKSPACE/memory" ]]; then
        local bad_mem=0
        while IFS= read -r -d '' mf; do
            if is_world_readable "$mf"; then
                ((bad_mem++)) || true
            fi
        done < <(find "$OC_WORKSPACE/memory" -type f -print0 2>/dev/null)

        if (( bad_mem > 0 )); then
            finding WARNING "${bad_mem} memory file(s) are world-readable" \
                "Memory may contain private context" \
                "chmod 600 memory/*" "find '${OC_WORKSPACE}/memory' -type f -exec chmod 600 {} +"
        elif [[ -d "$OC_WORKSPACE/memory" ]]; then
            finding PASS "Memory files have restricted permissions" "" ""
        fi
    fi

    # --- MEMORY.md permissions ---
    if [[ -f "$OC_WORKSPACE/MEMORY.md" ]]; then
        if is_world_readable "$OC_WORKSPACE/MEMORY.md"; then
            finding WARNING "MEMORY.md is world-readable" \
                "Contains personal context and curated memories" \
                "chmod 600 MEMORY.md" "chmod 600 '${OC_WORKSPACE}/MEMORY.md'"
        else
            finding PASS "MEMORY.md permissions restricted" "" ""
        fi
    fi
}

# ---------------------------------------------------------------------------
# Summary & Output
# ---------------------------------------------------------------------------

print_summary() {
    local score=0
    if (( TOTAL_POINTS > 0 )); then
        score=$(( (EARNED_POINTS * 100) / TOTAL_POINTS ))
    fi

    out ""
    out "${BOLD}━━━ Summary ━━━${RESET}"
    out ""
    out "  🔴 Critical: ${CRITICAL_COUNT}"
    out "  🟡 Warning:  ${WARNING_COUNT}"
    out "  🟢 Passed:   ${PASS_COUNT}"
    out "  ⚪ Info:     ${INFO_COUNT}"
    out ""

    local grade color
    if (( score >= 90 )); then grade="A"; color="$GREEN"
    elif (( score >= 75 )); then grade="B"; color="$GREEN"
    elif (( score >= 60 )); then grade="C"; color="$YELLOW"
    elif (( score >= 40 )); then grade="D"; color="$YELLOW"
    else grade="F"; color="$RED"
    fi

    out "  ${BOLD}Security Score: ${color}${score}/100 (${grade})${RESET}"
    out ""

    if (( CRITICAL_COUNT > 0 )); then
        out "  ${RED}⚠  ${CRITICAL_COUNT} critical issue(s) require immediate attention.${RESET}"
    fi
    if [[ "$FLAG_FIX" == false ]] && (( CRITICAL_COUNT + WARNING_COUNT > 0 )); then
        out "  ${DIM}Run with --fix to apply available remediations.${RESET}"
    fi
    out ""
}

print_json() {
    echo "{"
    echo "  \"version\": \"${VERSION}\","
    echo "  \"timestamp\": \"$(date -u '+%Y-%m-%dT%H:%M:%SZ')\","
    echo "  \"os\": \"${OS}\","
    echo "  \"openclaw_home\": \"${OC_HOME}\","
    echo "  \"score\": $(( TOTAL_POINTS > 0 ? (EARNED_POINTS * 100) / TOTAL_POINTS : 0 )),"
    echo "  \"counts\": {"
    echo "    \"critical\": ${CRITICAL_COUNT},"
    echo "    \"warning\": ${WARNING_COUNT},"
    echo "    \"pass\": ${PASS_COUNT},"
    echo "    \"info\": ${INFO_COUNT}"
    echo "  },"
    echo "  \"findings\": ["
    local i=0
    for f in "${FINDINGS[@]}"; do
        ((i++)) || true
        if (( i < ${#FINDINGS[@]} )); then
            echo "    ${f},"
        else
            echo "    ${f}"
        fi
    done
    echo "  ]"
    echo "}"
}

save_report() {
    local filename="oc-security-report-$(date '+%Y%m%d-%H%M%S')"
    if [[ "$FLAG_JSON" == true ]]; then
        filename="${filename}.json"
        print_json > "$filename"
    else
        filename="${filename}.txt"
        echo "$REPORT_BUF" > "$filename"
    fi
    echo -e "${GREEN}Report saved to: ${filename}${RESET}"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

main() {
    parse_args "$@"
    banner

    check_openclaw_config
    check_network
    check_credentials
    check_os_hardening
    check_agent_guardrails

    print_summary

    if [[ "$FLAG_JSON" == true ]]; then
        print_json
    fi

    if [[ "$FLAG_REPORT" == true ]]; then
        save_report
    fi

    # Exit code: 2 if criticals, 1 if warnings, 0 if clean
    if (( CRITICAL_COUNT > 0 )); then exit 2
    elif (( WARNING_COUNT > 0 )); then exit 1
    else exit 0
    fi
}

main "$@"
