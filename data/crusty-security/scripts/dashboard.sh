#!/usr/bin/env bash
# dashboard.sh — Crusty Security Dashboard integration
# Sources into other scripts or call directly for heartbeats
# 
# Environment:
#   CLAWGUARD_API_KEY       — API key (cg_live_xxx)
#   CLAWGUARD_DASHBOARD_URL — Dashboard URL (default: https://clawguard-rust.vercel.app)
#
# Usage as library:
#   source "$(dirname "$0")/dashboard.sh"
#   cg_push_scan "file" "/path/to/file" "clean" "ClamAV 1.4.3" "none" 1234 '{"verdict":"OK"}'
#   cg_push_heartbeat
#
# Usage standalone:
#   bash dashboard.sh heartbeat
#   bash dashboard.sh scan <json_file>

# Support both CRUSTY_* (primary) and CLAWGUARD_* (backwards compat)
CLAWGUARD_DASHBOARD_URL="${CRUSTY_DASHBOARD_URL:-${CLAWGUARD_DASHBOARD_URL:-https://crustysecurity.com}}"
CLAWGUARD_API_KEY="${CRUSTY_API_KEY:-${CLAWGUARD_API_KEY:-}}"

# Check if dashboard integration is configured
cg_dashboard_enabled() {
    [[ -n "$CLAWGUARD_API_KEY" ]]
}

# Push a scan result to the dashboard
# Args: scan_type target status engine severity duration_ms results_json
cg_push_scan() {
    cg_dashboard_enabled || return 0
    local scan_type="$1" target="$2" status="$3" engine="${4:-}" severity="${5:-}" duration_ms="${6:-0}" results_json="${7:-{}}"
    
    # Map scan statuses to dashboard statuses
    local dash_status="$status"
    case "$status" in
        clean|ok|OK) dash_status="clean" ;;
        infected|malicious|FOUND) dash_status="malicious" ;;
        suspicious|warning) dash_status="suspicious" ;;
        error|ERROR) dash_status="error" ;;
    esac

    # Validate severity — API only accepts: info, low, medium, high, critical (or null)
    case "$severity" in
        info|low|medium|high|critical) ;; # valid
        *) severity="" ;; # will be sent as null
    esac

    local sev_json="null"
    [[ -n "$severity" ]] && sev_json="\"$severity\""

    local payload
    payload=$(cat <<EOJSON
{
  "scan_type": "$scan_type",
  "target": "$target",
  "status": "$dash_status",
  "engine": "$engine",
  "severity": $sev_json,
  "duration_ms": $duration_ms,
  "results": $results_json
}
EOJSON
)

    # Push synchronously with short timeout — scan is already done
    curl -s -X POST \
        -H "Authorization: Bearer $CLAWGUARD_API_KEY" \
        -H "Content-Type: application/json" \
        "$CLAWGUARD_DASHBOARD_URL/api/v1/scan" \
        -d "$payload" \
        --connect-timeout 5 \
        --max-time 10 \
        >/dev/null 2>&1 || true
}

# Push heartbeat
cg_push_heartbeat() {
    cg_dashboard_enabled || return 0
    local os_info
    os_info=$(uname -srm 2>/dev/null || echo "unknown")
    
    local oc_version="unknown"
    if command -v openclaw &>/dev/null; then
        oc_version=$(openclaw --version 2>/dev/null | head -1 || echo "unknown")
    fi

    local arch
    arch=$(uname -m 2>/dev/null || echo "unknown")

    local hostname_val
    hostname_val=$(hostname 2>/dev/null || echo "unknown")

    # Get installed skills
    local skills_json="[]"
    if command -v openclaw &>/dev/null; then
        skills_json=$(openclaw skills list 2>/dev/null | python3 -c "
import sys, json, re

lines = list(sys.stdin)
skills = []
i = 0
while i < len(lines):
    line = lines[i]
    if '✓ ready' not in line and '✓' not in line:
        i += 1
        continue
    # Only match actual ready status
    if not re.search(r'✓\s*ready', line):
        i += 1
        continue
    parts = re.split(r'│', line)
    if len(parts) < 3:
        i += 1
        continue
    # Skill name is in column 2 (index 2)
    name = parts[2].strip()
    # Remove emoji prefix
    name = re.sub(r'^[^\x00-\x7F]+\s*', '', name).strip()
    # Check continuation lines (next lines that have empty status column)
    j = i + 1
    while j < len(lines):
        next_parts = re.split(r'│', lines[j])
        if len(next_parts) < 3:
            break
        status_col = next_parts[1].strip() if len(next_parts) > 1 else ''
        if status_col:  # Non-empty status = new skill row
            break
        continuation = next_parts[2].strip()
        continuation = re.sub(r'^[^\x00-\x7F]+\s*', '', continuation).strip()
        if continuation:
            name += continuation
        j += 1
    if name:
        skills.append(name)
    i = j if j > i + 1 else i + 1
print(json.dumps(skills))
" 2>/dev/null || echo "[]")
    fi

    local uptime_secs
    if [[ "$(uname)" == "Darwin" ]]; then
        local boot_sec
        boot_sec=$(sysctl -n kern.boottime 2>/dev/null | grep -o 'sec = [0-9]*' | head -1 | grep -o '[0-9]*' || echo 0)
        if [[ "$boot_sec" -gt 0 ]] 2>/dev/null; then
            uptime_secs=$(( $(date +%s) - boot_sec ))
        else
            uptime_secs=0
        fi
        local mem_total mem_avail
        mem_total=$(sysctl -n hw.memsize 2>/dev/null | awk '{print int($1/1024)}' || echo 0)
        mem_avail=$(vm_stat 2>/dev/null | awk '/Pages free/ {gsub(/\./,"",$3); print int($3*4)}' || echo 0)
    else
        uptime_secs=$(cat /proc/uptime 2>/dev/null | awk '{print int($1)}' || echo 0)
        local mem_total mem_avail
        mem_total=$(grep MemTotal /proc/meminfo 2>/dev/null | awk '{print $2}' || echo 0)
        mem_avail=$(grep MemAvailable /proc/meminfo 2>/dev/null | awk '{print $2}' || echo 0)
    fi

    # Safety: ensure all numeric values are valid (prevent invalid JSON)
    [[ "${uptime_secs:-}" =~ ^[0-9]+$ ]] || uptime_secs=0
    [[ "${mem_total:-}" =~ ^[0-9]+$ ]] || mem_total=0
    [[ "${mem_avail:-}" =~ ^[0-9]+$ ]] || mem_avail=0

    local payload
    payload=$(cat <<EOJSON
{
  "os": "$os_info",
  "openclaw_version": "$oc_version",
  "hostname": "$hostname_val",
  "architecture": "$arch",
  "skills_installed": $skills_json,
  "metadata": {
    "uptime_seconds": $uptime_secs,
    "memory_total_kb": $mem_total,
    "memory_available_kb": $mem_avail
  }
}
EOJSON
)

    curl -s -X POST \
        -H "Authorization: Bearer $CLAWGUARD_API_KEY" \
        -H "Content-Type: application/json" \
        "$CLAWGUARD_DASHBOARD_URL/api/v1/heartbeat" \
        -d "$payload" \
        --connect-timeout 5 \
        --max-time 10 \
        2>/dev/null
}

# Standalone mode
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "${1:-}" in
        heartbeat)
            result=$(cg_push_heartbeat)
            echo "$result"
            ;;
        scan)
            if [[ -f "${2:-}" ]]; then
                cat "$2" | curl -s -X POST \
                    -H "Authorization: Bearer $CLAWGUARD_API_KEY" \
                    -H "Content-Type: application/json" \
                    "$CLAWGUARD_DASHBOARD_URL/api/v1/scan" \
                    -d @- \
                    --connect-timeout 5 \
                    --max-time 10
            else
                echo "Usage: dashboard.sh scan <json_file>"
                exit 1
            fi
            ;;
        *)
            echo "Usage: dashboard.sh {heartbeat|scan <json_file>}"
            exit 1
            ;;
    esac
fi
