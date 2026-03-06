#!/bin/bash
# scan_coherence.sh - Check memory consistency and internal unity
# Returns: 3=coherent, 2=minor issues, 1=contradictions, 0=chaos
# Event-sensitive: compaction, memory review, contradictions

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_scan_helper.sh"

NEED="coherence"
# WORKSPACE validated by _scan_helper.sh
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

# Get time-based satisfaction
time_sat=$(calc_time_satisfaction "$NEED")

# Always check events — compaction can happen anytime
issues=0
positive_signals=0

# Check for MEMORY.md existence and size
if [[ -f "$WORKSPACE/MEMORY.md" ]]; then
    lines=$(wc -l < "$WORKSPACE/MEMORY.md")
    if [[ $lines -gt 500 ]]; then
        issues=$((issues + 2))  # Too large, needs pruning
    fi
else
    issues=$((issues + 3))  # No MEMORY.md = big issue
fi

# Check for orphaned temp files
if [[ -d "$MEMORY_DIR" ]]; then
    orphans=$(find -P "$MEMORY_DIR" -name "*.tmp" -o -name "*~" 2>/dev/null | wc -l)
    issues=$((issues + orphans))
fi

# Scan memory for coherence events (word count)
scan_coherence_events() {
    local file="$1"
    [[ ! -f "$file" ]] && return
    
    # Positive: reviewed memory, organized, cleaned up, consolidated, updated MEMORY.md
    local pos=$(grep -oiE "(reviewed memory|memory review|organized|cleaned up|consolidated|updated MEMORY|memory maintenance|files in order|context clear)" "$file" 2>/dev/null | wc -l) || pos=0
    positive_signals=$((positive_signals + pos))
    
    # Negative: compaction, context loss, contradiction, confused about past, lost context
    local neg=$(grep -oiE "(compaction|context loss|lost context|contradiction|contradicts|confused about|don't remember|forgot what|inconsistent|fragmented)" "$file" 2>/dev/null | wc -l) || neg=0
    issues=$((issues + neg))
}

scan_coherence_events "$MEMORY_DIR/$TODAY.md"
scan_coherence_events "$MEMORY_DIR/$YESTERDAY.md"

# Check autonomous dashboard for stale items
DASHBOARD="$WORKSPACE/memory/autonomous/DASHBOARD.md"
if [[ -f "$DASHBOARD" ]]; then
    # Count active items (unchecked boxes)
    active_items=$(grep -c "^\- \[ \]" "$DASHBOARD" 2>/dev/null || echo 0)
    
    # Check for stale items (files not modified in 7+ days)
    stale_count=0
    if [[ -d "$WORKSPACE/memory/autonomous" ]]; then
        stale_count=$(find -P "$WORKSPACE/memory/autonomous" -name "*.md" -mtime +7 2>/dev/null | wc -l)
    fi
    
    # Stale items = coherence issue (unfinished self-directed work)
    if [[ $stale_count -gt 2 ]]; then
        issues=$((issues + 2))  # Multiple stale items
    elif [[ $stale_count -gt 0 ]]; then
        issues=$((issues + 1))  # Some stale items
    fi
    
    # Recent dashboard activity = positive signal
    if [[ -n "$(find -P "$DASHBOARD" -mtime -1 2>/dev/null)" ]]; then
        positive_signals=$((positive_signals + 1))
    fi
fi

# Calculate event satisfaction
if [[ $issues -ge 6 ]]; then
    event_sat=0  # Chaos
elif [[ $issues -ge 3 ]]; then
    event_sat=1  # Contradictions
elif [[ $issues -ge 1 ]]; then
    event_sat=2  # Minor issues
elif [[ $positive_signals -ge 2 ]]; then
    event_sat=3  # Actively maintained
else
    event_sat=$time_sat  # Default to time-based
fi

smart_satisfaction "$NEED" "$event_sat"
