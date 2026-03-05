#!/usr/bin/env bash
# session-health-monitor: statusline.sh
# Reads Claude Code statusline JSON from stdin, outputs color-coded context health.
# Tracks compaction by detecting large drops in usage percentage.

set -euo pipefail

# Thresholds (configurable via env)
GREEN_MAX="${HEALTH_GREEN_MAX:-50}"
RED_MIN="${HEALTH_RED_MIN:-75}"
COMPACTION_DROP="${COMPACTION_DROP:-30}"

# ANSI colors
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
RESET='\033[0m'

# Read JSON from stdin
input=$(cat)

# Extract fields (fallback gracefully if jq missing or fields absent)
if command -v jq &>/dev/null; then
    used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty' 2>/dev/null) || true
    session_id=$(echo "$input" | jq -r '.session_id // "unknown"' 2>/dev/null) || true
else
    # Fallback: basic grep extraction
    used_pct=$(echo "$input" | grep -o '"used_percentage":[0-9.]*' | head -1 | cut -d: -f2) || true
    session_id=$(echo "$input" | grep -o '"session_id":"[^"]*"' | head -1 | cut -d'"' -f4) || true
fi

# If no data yet, show fallback
if [[ -z "$used_pct" ]]; then
    echo "Context Window"
    exit 0
fi

# Round to integer
used_pct=$(printf '%.0f' "$used_pct")

# Session state file (ephemeral, in /tmp)
session_id="${session_id:-unknown}"
state_file="/tmp/session-health-${session_id}.json"

# Load previous state
prev_pct=0
compactions=0
if [[ -f "$state_file" ]]; then
    if command -v jq &>/dev/null; then
        prev_pct=$(jq -r '.last_pct // 0' "$state_file" 2>/dev/null) || prev_pct=0
        compactions=$(jq -r '.compactions // 0' "$state_file" 2>/dev/null) || compactions=0
    else
        prev_pct=$(grep -o '"last_pct":[0-9]*' "$state_file" | cut -d: -f2) || prev_pct=0
        compactions=$(grep -o '"compactions":[0-9]*' "$state_file" | cut -d: -f2) || compactions=0
    fi
fi

# Detect compaction: usage dropped by more than COMPACTION_DROP points
if [[ "$prev_pct" -gt 0 ]] && [[ $((prev_pct - used_pct)) -ge "$COMPACTION_DROP" ]]; then
    compactions=$((compactions + 1))
fi

# Save state
cat > "$state_file" <<EOF
{"last_pct":${used_pct},"compactions":${compactions},"updated":"$(date -u +%Y-%m-%dT%H:%M:%SZ)"}
EOF

# Determine color
if [[ "$used_pct" -ge "$RED_MIN" ]] || [[ "$compactions" -ge 2 ]]; then
    color="$RED"
elif [[ "$used_pct" -ge "$GREEN_MAX" ]] || [[ "$compactions" -ge 1 ]]; then
    color="$YELLOW"
else
    color="$GREEN"
fi

# Output
echo -e "${color}${used_pct}% Context | ${compactions}x compact${RESET}"
