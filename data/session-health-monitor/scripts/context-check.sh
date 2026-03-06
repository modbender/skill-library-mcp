#!/usr/bin/env bash
# session-health-monitor: context-check.sh
# Health check for context window status.
# Exit codes: 0=GREEN, 1=YELLOW, 2=RED
# Reads JSON from stdin or uses current session state.

set -euo pipefail

# Thresholds
GREEN_MAX="${HEALTH_GREEN_MAX:-50}"
RED_MIN="${HEALTH_RED_MIN:-75}"
COMPACTION_DROP="${COMPACTION_DROP:-30}"

json_mode=false
for arg in "$@"; do
    case "$arg" in
        --json) json_mode=true ;;
    esac
done

# Read JSON from stdin if available, otherwise try to find state files
input=""
if [[ ! -t 0 ]]; then
    input=$(cat)
fi

used_pct=""
session_id="unknown"
compactions=0

if [[ -n "$input" ]]; then
    if command -v jq &>/dev/null; then
        used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty' 2>/dev/null) || true
        session_id=$(echo "$input" | jq -r '.session_id // "unknown"' 2>/dev/null) || true
    else
        used_pct=$(echo "$input" | grep -o '"used_percentage":[0-9.]*' | head -1 | cut -d: -f2) || true
        session_id=$(echo "$input" | grep -o '"session_id":"[^"]*"' | head -1 | cut -d'"' -f4) || true
    fi
fi

# If we have a session_id, check for compaction state
state_file="/tmp/session-health-${session_id}.json"
if [[ -f "$state_file" ]]; then
    if command -v jq &>/dev/null; then
        compactions=$(jq -r '.compactions // 0' "$state_file" 2>/dev/null) || compactions=0
        # If no stdin data, use stored percentage
        if [[ -z "$used_pct" ]]; then
            used_pct=$(jq -r '.last_pct // empty' "$state_file" 2>/dev/null) || true
        fi
    else
        compactions=$(grep -o '"compactions":[0-9]*' "$state_file" | cut -d: -f2) || compactions=0
        if [[ -z "$used_pct" ]]; then
            used_pct=$(grep -o '"last_pct":[0-9]*' "$state_file" | cut -d: -f2) || true
        fi
    fi
fi

# If still no data, report unknown
if [[ -z "$used_pct" ]]; then
    if $json_mode; then
        echo '{"status":"unknown","message":"No context data available"}'
    else
        echo "Unknown — no context data available"
    fi
    exit 0
fi

used_pct=$(printf '%.0f' "$used_pct")

# Determine status
if [[ "$used_pct" -ge "$RED_MIN" ]] || [[ "$compactions" -ge 2 ]]; then
    status="RED"
    exit_code=2
    message="CRITICAL: ${used_pct}% context used, ${compactions}x compacted — save facts NOW"
elif [[ "$used_pct" -ge "$GREEN_MAX" ]] || [[ "$compactions" -ge 1 ]]; then
    status="YELLOW"
    exit_code=1
    message="WARNING: ${used_pct}% context used, ${compactions}x compacted — consider saving facts"
else
    status="GREEN"
    exit_code=0
    message="OK: ${used_pct}% context used, ${compactions}x compacted"
fi

if $json_mode; then
    cat <<EOF
{"status":"${status}","used_percentage":${used_pct},"compactions":${compactions},"message":"${message}"}
EOF
else
    echo "$message"
fi

exit "$exit_code"
