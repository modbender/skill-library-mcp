#!/bin/bash
# scan_closure.sh - Check for open threads, pending TODOs, completions
# Returns: 3=all closed, 2=some open, 1=many open, 0=overwhelmed
# Event-sensitive: task completion, new TODOs

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_scan_helper.sh"

NEED="closure"
# WORKSPACE validated by _scan_helper.sh
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

# Get time-based satisfaction
time_sat=$(calc_time_satisfaction "$NEED")

# Always check events — completions and new TODOs happen constantly
open_count=0
completed_count=0

# Scan memory for closure events (word count)
scan_closure_events() {
    local file="$1"
    [[ ! -f "$file" ]] && return
    
    # Positive: completed, done, finished, resolved, closed, checked off
    local done=$(grep -oiE "(completed|done|finished|resolved|closed|checked off|\[x\]|✅|✓)" "$file" 2>/dev/null | wc -l) || done=0
    completed_count=$((completed_count + done))
    
    # Negative: TODO, PENDING, open, waiting, need to, should
    local open=$(grep -oiE "(TODO|PENDING|\[ \]|waiting for|need to|should do|to follow up|open question|unresolved|blocked)" "$file" 2>/dev/null | wc -l) || open=0
    open_count=$((open_count + open))
}

scan_closure_events "$MEMORY_DIR/$TODAY.md"
scan_closure_events "$MEMORY_DIR/$YESTERDAY.md"

# Also check last 3 days of memory for accumulated TODOs
if [[ -d "$MEMORY_DIR" ]]; then
    # Count files with unclosed TODOs (not recent ones we already scanned)
    old_todos=$(find -P "$MEMORY_DIR" -name "*.md" -mtime -3 ! -name "$TODAY.md" ! -name "$YESTERDAY.md" \
        -exec grep -l "TODO\|PENDING\|\[ \]" {} \; 2>/dev/null | wc -l)
    open_count=$((open_count + old_todos))
fi

# Check scratchpad/ for stale ideas (older than 7 days = unresolved threads)
if [[ -d "$WORKSPACE/scratchpad" ]]; then
    stale_scratches=$(find -P "$WORKSPACE/scratchpad" -type f -mtime +7 2>/dev/null | wc -l)
    open_count=$((open_count + stale_scratches))
fi

# Net calculation: open items minus completions
net_open=$((open_count - completed_count))
[[ $net_open -lt 0 ]] && net_open=0

# Calculate event satisfaction
if [[ $net_open -ge 15 ]]; then
    event_sat=0  # Overwhelmed
elif [[ $net_open -ge 8 ]]; then
    event_sat=1  # Many open
elif [[ $net_open -ge 4 ]]; then
    event_sat=2  # Some open
else
    event_sat=3  # All closed or manageable
fi

smart_satisfaction "$NEED" "$event_sat"
