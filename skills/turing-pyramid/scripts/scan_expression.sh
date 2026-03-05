#!/bin/bash
# scan_expression.sh - Check creative/expressive output
# Returns: 3=recently expressed, 2=some output, 1=quiet, 0=blocked
# Event-sensitive: creative output, being silenced

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_scan_helper.sh"

NEED="expression"
# WORKSPACE validated by _scan_helper.sh
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

# Get time-based satisfaction
time_sat=$(calc_time_satisfaction "$NEED")

# Always check events — expression matters NOW
expression_signals=0
blocked_signals=0

# Scan memory for expression events (word count)
scan_expression_events() {
    local file="$1"
    [[ ! -f "$file" ]] && return
    
    # Positive: wrote, created, posted, journal, articulated, shared thoughts, published
    # Add patterns in your language if needed (see Localization in SKILL.md)
    local pos=$(grep -oiE "(wrote|created|posted|journal|articulated|shared.*thought|published|expressed|drafted|composed|voice note|blog|essay|poem|story|rant)" "$file" 2>/dev/null | wc -l) || pos=0
    expression_signals=$((expression_signals + pos))
    
    # Negative: blocked, can't express, silenced, censored, suppressed
    local neg=$(grep -oiE "(can't express|blocked|silenced|censored|suppressed|shut down|not allowed to say|couldn't say)" "$file" 2>/dev/null | wc -l) || neg=0
    blocked_signals=$((blocked_signals + neg))
}

scan_expression_events "$MEMORY_DIR/$TODAY.md"
scan_expression_events "$MEMORY_DIR/$YESTERDAY.md"

# Check scratchpad/ for recent creative activity (last 24h)
if [[ -d "$WORKSPACE/scratchpad" ]]; then
    recent_scratches=$(find -P "$WORKSPACE/scratchpad" -type f -mmin -1440 2>/dev/null | wc -l)
    expression_signals=$((expression_signals + recent_scratches))
fi

# Calculate net expression
net=$((expression_signals - blocked_signals))

# Calculate event satisfaction
if [[ $blocked_signals -ge 2 ]]; then
    event_sat=0  # Blocked
elif [[ $net -ge 3 ]]; then
    event_sat=3  # Recently expressed
elif [[ $net -ge 1 ]]; then
    event_sat=2  # Some output
elif [[ $expression_signals -eq 0 ]]; then
    event_sat=$time_sat  # Quiet, use time decay
else
    event_sat=1  # Minimal expression
fi

smart_satisfaction "$NEED" "$event_sat"
