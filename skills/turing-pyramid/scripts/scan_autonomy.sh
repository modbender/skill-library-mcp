#!/bin/bash
# scan_autonomy.sh - Check for self-directed action
# Returns: 3=autonomous, 2=guided, 1=dependent, 0=blocked
# Event-sensitive: self-initiated actions, being blocked

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_scan_helper.sh"

NEED="autonomy"
# WORKSPACE validated by _scan_helper.sh
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

# Get time-based satisfaction
time_sat=$(calc_time_satisfaction "$NEED")

# Always check events — self-direction matters NOW
autonomous_signals=0
blocked_signals=0

# Scan memory for autonomy events (word count)
scan_autonomy_events() {
    local file="$1"
    [[ ! -f "$file" ]] && return
    
    # Positive: decided, chose, initiated, my idea, proactive, self-directed, on my own
    local pos=$(grep -oiE "(decided|chose|initiated|explored|my idea|self-directed|proactive|on my own|took initiative|my decision|independently|without asking)" "$file" 2>/dev/null | wc -l) || pos=0
    autonomous_signals=$((autonomous_signals + pos))
    
    # Negative: blocked, waiting for permission, can't without, need approval, dependent
    local neg=$(grep -oiE "(blocked|waiting for permission|can't without|need approval|dependent on|not allowed|restricted|forbidden|must ask first)" "$file" 2>/dev/null | wc -l) || neg=0
    blocked_signals=$((blocked_signals + neg))
}

scan_autonomy_events "$MEMORY_DIR/$TODAY.md"
scan_autonomy_events "$MEMORY_DIR/$YESTERDAY.md"

# Calculate net autonomy
net_autonomy=$((autonomous_signals - blocked_signals))

# Calculate event satisfaction
if [[ $blocked_signals -ge 3 ]]; then
    event_sat=0  # Blocked
elif [[ $net_autonomy -ge 3 ]]; then
    event_sat=3  # Autonomous
elif [[ $net_autonomy -ge 1 ]]; then
    event_sat=2  # Guided but some agency
elif [[ $autonomous_signals -eq 0 ]]; then
    event_sat=1  # Dependent, no self-direction
else
    event_sat=$time_sat  # Default to time-based
fi

smart_satisfaction "$NEED" "$event_sat"
