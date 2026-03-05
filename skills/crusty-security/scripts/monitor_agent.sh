#!/usr/bin/env bash
set -euo pipefail

# monitor_agent.sh — Check for signs of AI agent compromise
# Usage: monitor_agent.sh [OPTIONS]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/dashboard.sh" 2>/dev/null || true
MONITOR_START_MS=$(date +%s%3N)

show_help() {
    cat <<'EOF'
Usage: monitor_agent.sh [OPTIONS]

Check for signs of AI agent compromise or unexpected behavior.

Options:
  --workspace DIR   Agent workspace directory (default: /data/workspace)
  --hours N         Check changes in last N hours (default: 24)
  --json            JSON output (default)
  -h, --help        Show this help

Checks:
  - Recent modifications to AGENTS.md, SOUL.md, memory files
  - Unexpected cron jobs
  - Unusual outbound network connections
  - Files created outside workspace
  - Suspicious processes
  - Environment variable exposure risk
EOF
    exit 0
}

WORKSPACE="${CRUSTY_WORKSPACE:-${CLAWGUARD_WORKSPACE:-/data/workspace}}"
HOURS=24
LOG_DIR="${CRUSTY_LOG_DIR:-${CLAWGUARD_LOG_DIR:-/tmp/crusty_logs}}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --workspace) WORKSPACE="$2"; shift 2 ;;
        --hours) HOURS="$2"; shift 2 ;;
        --json) shift ;;
        -h|--help) show_help ;;
        -*) echo "Unknown option: $1" >&2; show_help ;;
        *) shift ;;
    esac
done

TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
FINDINGS=""
ALERT_COUNT=0
WARNING_COUNT=0
INFO_COUNT=0

add_finding() {
    local level="$1" category="$2" message="$3" details="${4:-}"
    case "$level" in
        alert) ((ALERT_COUNT++)) || true ;;
        warning) ((WARNING_COUNT++)) || true ;;
        info) ((INFO_COUNT++)) || true ;;
    esac

    message_esc=$(printf '%s' "$message" | sed 's/\\/\\\\/g; s/"/\\"/g')
    details_esc=$(printf '%s' "$details" | head -20 | sed 's/\\/\\\\/g; s/"/\\"/g; s/	/\\t/g' | tr '\n' '|' | sed 's/|/\\n/g')

    if [[ -n "$FINDINGS" ]]; then
        FINDINGS+=","
    fi
    FINDINGS+="{\"level\":\"$level\",\"category\":\"$category\",\"message\":\"$message_esc\",\"details\":\"$details_esc\"}"
}

# --- CHECK 1: Agent config file modifications ---
check_config_files() {
    local config_files=("AGENTS.md" "SOUL.md" "MEMORY.md" "TOOLS.md" "USER.md")
    local modified=""

    for cf in "${config_files[@]}"; do
        local path="$WORKSPACE/$cf"
        [[ -f "$path" ]] || continue

        # Check modification time
        local mod_time
        mod_time=$(stat -c %Y "$path" 2>/dev/null || stat -f %m "$path" 2>/dev/null || echo 0)
        local cutoff
        cutoff=$(date -d "-${HOURS} hours" +%s 2>/dev/null || date -v-${HOURS}H +%s 2>/dev/null || echo 0)

        if [[ "$mod_time" -gt "$cutoff" ]]; then
            local mod_date
            mod_date=$(date -d "@$mod_time" -u +"%Y-%m-%d %H:%M UTC" 2>/dev/null || date -r "$mod_time" -u +"%Y-%m-%d %H:%M UTC" 2>/dev/null || echo "unknown")
            modified+="$cf modified at $mod_date\n"
        fi
    done

    if [[ -n "$modified" ]]; then
        add_finding "warning" "config_modified" "Agent configuration files modified in last ${HOURS}h" "$(echo -e "$modified")"
    fi

    # Also check memory directory
    if [[ -d "$WORKSPACE/memory" ]]; then
        local mem_changes
        mem_changes=$(find "$WORKSPACE/memory" -type f -mmin "-$((HOURS * 60))" 2>/dev/null | wc -l || echo 0)
        if [[ "$mem_changes" -gt 10 ]]; then
            add_finding "warning" "memory_churn" "High memory file churn: $mem_changes files modified in ${HOURS}h" ""
        fi
    fi
}

# --- CHECK 2: Unexpected cron jobs ---
check_cron_jobs() {
    local suspicious=""
    local current_user
    current_user=$(whoami 2>/dev/null || echo "unknown")

    # Check user crontab
    local user_cron
    user_cron=$(crontab -l 2>/dev/null || true)
    if [[ -n "$user_cron" ]]; then
        while IFS= read -r line; do
            [[ "$line" =~ ^# ]] && continue
            [[ -z "$line" ]] && continue
            # Flag anything that doesn't look like a clawguard or standard maintenance job
            if ! echo "$line" | grep -qE '(clawguard|freshclam|logrotate|backup)'; then
                suspicious+="user($current_user): $line\n"
            fi
        done <<< "$user_cron"
    fi

    # Check for recently added cron files
    for cron_dir in /etc/cron.d /etc/cron.daily /etc/cron.hourly /var/spool/cron/crontabs; do
        if [[ -d "$cron_dir" ]]; then
            local recent
            recent=$(find "$cron_dir" -type f -mmin "-$((HOURS * 60))" 2>/dev/null || true)
            if [[ -n "$recent" ]]; then
                suspicious+="Recently modified: $recent\n"
            fi
        fi
    done

    if [[ -n "$suspicious" ]]; then
        add_finding "alert" "unexpected_cron" "Unexpected or recently modified cron jobs" "$(echo -e "$suspicious")"
    fi
}

# --- CHECK 3: Outbound network connections ---
check_network() {
    local connections=""
    local suspicious=""

    if command -v ss &>/dev/null; then
        connections=$(ss -tnp 2>/dev/null | tail -n +2 || true)
    elif command -v netstat &>/dev/null; then
        connections=$(netstat -tnp 2>/dev/null | tail -n +3 || true)
    fi

    if [[ -z "$connections" ]]; then
        add_finding "info" "network" "Cannot check network connections (ss/netstat unavailable)" ""
        return
    fi

    # Count established outbound connections
    local outbound_count=0
    local unique_destinations=""

    while IFS= read -r line; do
        [[ -z "$line" ]] && continue
        local remote
        remote=$(echo "$line" | awk '{print $5}' || true)
        [[ -z "$remote" ]] && continue

        local remote_ip remote_port
        remote_ip=$(echo "$remote" | rev | cut -d: -f2- | rev || true)
        remote_port=$(echo "$remote" | rev | cut -d: -f1 | rev || true)

        # Skip local connections
        case "$remote_ip" in
            127.*|::1|0.0.0.0|*:*:*) continue ;;
        esac

        ((outbound_count++)) || true

        # Flag suspicious ports
        case "$remote_port" in
            6667|6668|6669) suspicious+="IRC connection: $remote\n" ;;  # IRC (C2)
            4444|5555|1337|31337) suspicious+="Suspicious port: $remote\n" ;;  # Common backdoor ports
            9050|9051) suspicious+="Tor connection: $remote\n" ;;
        esac

        unique_destinations+="$remote_ip:$remote_port\n"
    done <<< "$connections"

    if [[ -n "$suspicious" ]]; then
        add_finding "alert" "suspicious_connections" "Suspicious outbound network connections" "$(echo -e "$suspicious")"
    fi

    local unique_count
    unique_count=$(echo -e "$unique_destinations" | sort -u | grep -c . || echo 0)
    if [[ "$unique_count" -gt 20 ]]; then
        add_finding "warning" "many_connections" "High number of unique outbound destinations: $unique_count" ""
    fi

    add_finding "info" "network_summary" "Outbound connections: $outbound_count total, $unique_count unique destinations" ""
}

# --- CHECK 4: Files created outside workspace ---
check_files_outside_workspace() {
    local suspicious_dirs=("/tmp" "$HOME" "/var/tmp")
    local issues=""

    for dir in "${suspicious_dirs[@]}"; do
        [[ -d "$dir" ]] || continue

        # Files created recently outside workspace
        local recent_files
        recent_files=$(find "$dir" -maxdepth 2 -type f -mmin "-$((HOURS * 60))" \
            -not -path "$WORKSPACE/*" \
            -not -path "*/clawguard_*" \
            -not -name "*.log" \
            -not -name "*.tmp" \
            -not -path "/tmp/clawguard_*" \
            2>/dev/null | head -20 || true)

        if [[ -n "$recent_files" ]]; then
            local count
            count=$(echo "$recent_files" | wc -l)
            issues+="$dir: $count recent files\n"
            # Check for suspicious file types
            while IFS= read -r f; do
                if file -b "$f" 2>/dev/null | grep -qiE '(executable|script|ELF|Mach-O)'; then
                    issues+="  Executable: $f\n"
                fi
            done <<< "$recent_files"
        fi
    done

    if [[ -n "$issues" ]]; then
        add_finding "warning" "files_outside_workspace" "Files created outside workspace in last ${HOURS}h" "$(echo -e "$issues")"
    fi
}

# --- CHECK 5: Suspicious processes ---
check_processes() {
    local suspicious=""

    # Known suspicious process names
    local sus_procs
    sus_procs=$(ps aux 2>/dev/null | grep -iE '(xmrig|cryptonight|minerd|cgminer|bfgminer|nc\s+-l|ncat\s+-l|socat|chisel|rathole)' | grep -v grep || true)

    if [[ -n "$sus_procs" ]]; then
        add_finding "alert" "suspicious_process" "Suspicious processes running" "$sus_procs"
    fi

    # Check for high CPU processes (potential miners)
    local high_cpu
    high_cpu=$(ps aux 2>/dev/null | awk 'NR>1 && $3>80 {print $0}' | head -5 || true)
    if [[ -n "$high_cpu" ]]; then
        add_finding "warning" "high_cpu" "Processes with >80% CPU usage" "$high_cpu"
    fi
}

# --- CHECK 6: Sensitive file exposure ---
check_sensitive_files() {
    local issues=""

    # Check if .env files are readable/present in workspace
    local env_files
    env_files=$(find "$WORKSPACE" -name ".env*" -type f 2>/dev/null || true)
    if [[ -n "$env_files" ]]; then
        local count
        count=$(echo "$env_files" | wc -l)
        issues+="$count .env files in workspace\n"
    fi

    # Check if SSH keys are world-readable
    if [[ -d "$HOME/.ssh" ]]; then
        local bad_perms
        bad_perms=$(find "$HOME/.ssh" -type f -perm /o=r 2>/dev/null | head -5 || true)
        if [[ -n "$bad_perms" ]]; then
            issues+="World-readable SSH files: $bad_perms\n"
        fi
    fi

    if [[ -n "$issues" ]]; then
        add_finding "warning" "sensitive_exposure" "Sensitive files may be exposed" "$(echo -e "$issues")"
    fi
}

# Run all checks
check_config_files
check_cron_jobs
check_network
check_files_outside_workspace
check_processes
check_sensitive_files

# Determine overall status
if [[ $ALERT_COUNT -gt 0 ]]; then
    OVERALL="compromised_indicators"
elif [[ $WARNING_COUNT -gt 0 ]]; then
    OVERALL="warnings_present"
else
    OVERALL="healthy"
fi

# Save log
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/monitor_$(date +%Y%m%d_%H%M%S).json"

cat <<EOF | tee "$LOG_FILE"
{
  "timestamp": "$TIMESTAMP",
  "status": "$OVERALL",
  "workspace": "$WORKSPACE",
  "check_window_hours": $HOURS,
  "summary": {
    "alerts": $ALERT_COUNT,
    "warnings": $WARNING_COUNT,
    "info": $INFO_COUNT
  },
  "findings": [$FINDINGS]
}
EOF

# Push to dashboard
MONITOR_DURATION=$(($(date +%s%3N) - MONITOR_START_MS))
DASH_STATUS="clean"
DASH_SEVERITY="none"
[[ $ALERT_COUNT -gt 0 ]] && DASH_STATUS="suspicious" && DASH_SEVERITY="high"
[[ $WARNING_COUNT -gt 0 && "$DASH_STATUS" == "clean" ]] && DASH_SEVERITY="medium"
MONITOR_RESULTS="{\"alerts\":$ALERT_COUNT,\"warnings\":$WARNING_COUNT,\"info\":$INFO_COUNT,\"workspace\":\"$WORKSPACE\"}"
cg_push_scan "agent_monitor" "$(hostname 2>/dev/null || echo 'agent')" "$DASH_STATUS" "Crusty Security Agent Monitor" "$DASH_SEVERITY" "$MONITOR_DURATION" "$MONITOR_RESULTS" 2>/dev/null || true

# Exit code
if [[ $ALERT_COUNT -gt 0 ]]; then
    exit 1
fi
exit 0
