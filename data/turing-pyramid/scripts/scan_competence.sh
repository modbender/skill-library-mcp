#!/bin/bash
# scan_competence.sh - Check for effective skill use
# Returns: 3=highly effective, 2=competent, 1=struggling, 0=failing
# Event-sensitive: successes, failures

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_scan_helper.sh"

NEED="competence"
# WORKSPACE validated by _scan_helper.sh
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

# Get time-based satisfaction
time_sat=$(calc_time_satisfaction "$NEED")

# Always check events — competence matters NOW
competence_signals=0
failure_signals=0

# Scan memory for competence events (word count)
scan_competence_events() {
    local file="$1"
    [[ ! -f "$file" ]] && return
    
    # Positive: completed, solved, built, fixed, succeeded, worked, shipped, implemented
    local pos=$(grep -oiE "(completed|solved|built|fixed|succeeded|worked|done|shipped|implemented|achieved|nailed|crushed it|got it working|published)" "$file" 2>/dev/null | wc -l) || pos=0
    competence_signals=$((competence_signals + pos))
    
    # Negative: failed, error, couldn't, stuck, broken, bug, crash
    local neg=$(grep -oiE "(failed|error|couldn't|stuck|broken|bug|crash|doesn't work|not working|can't figure|struggling|syntax error)" "$file" 2>/dev/null | wc -l) || neg=0
    failure_signals=$((failure_signals + neg))
}

scan_competence_events "$MEMORY_DIR/$TODAY.md"
scan_competence_events "$MEMORY_DIR/$YESTERDAY.md"

# Calculate net competence
net=$((competence_signals - failure_signals))

# Calculate event satisfaction
if [[ $failure_signals -gt $competence_signals ]] && [[ $failure_signals -gt 3 ]]; then
    event_sat=0  # Failing
elif [[ $net -ge 3 ]]; then
    event_sat=3  # Highly effective
elif [[ $net -ge 1 ]]; then
    event_sat=2  # Competent
elif [[ $competence_signals -eq 0 ]] && [[ $failure_signals -gt 0 ]]; then
    event_sat=1  # Struggling
else
    event_sat=$time_sat  # Default to time-based
fi

smart_satisfaction "$NEED" "$event_sat"
