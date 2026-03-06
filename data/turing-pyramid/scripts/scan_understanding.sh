#!/bin/bash
# scan_understanding.sh - Check learning and comprehension activity
# Returns: 3=actively learning, 2=some research, 1=stagnant, 0=confused/lost

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_scan_helper.sh"

NEED="understanding"
# WORKSPACE validated by _scan_helper.sh
MEMORY_DIR="$WORKSPACE/memory"

# Get time-based satisfaction first
time_sat=$(calc_time_satisfaction "$NEED")

# Always check events — confusion can override time satisfaction
# (understanding is event-sensitive: you can be confused RIGHT NOW)
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

research_activity=0
confusion_signals=0

# Helper function to scan a memory file
scan_memory_file() {
    local file="$1"
    [ ! -f "$file" ] && return
    
    # Positive: learning, discovery, understanding
    # Add patterns in your language if you keep notes in non-English (see SKILL.md)
    local count
    count=$(grep -oiE "(research|learned|learning|understood|discover|realiz|insight|figured out|makes sense|explored|read article|TIL|today i learned|grasped|clicked|aha|eureka|breakthrough|comprehend|studied|investigat|analyz|examin|documentation|tutorial)" "$file" 2>/dev/null | wc -l) || count=0
    research_activity=$((research_activity + count))
    
    # Negative: confusion, being lost (word count, not line count)
    count=$(grep -oiE "(confused|lost|unclear|don't understand|no idea|stuck|baffled|puzzled|perplexed|bewildered|wtf|makes no sense|doesn't make sense)" "$file" 2>/dev/null | wc -l) || count=0
    confusion_signals=$((confusion_signals + count))
}

# Check today's and yesterday's memory (12h decay spans both)
scan_memory_file "$MEMORY_DIR/$TODAY.md"
scan_memory_file "$MEMORY_DIR/$YESTERDAY.md"

# Check research directory activity (last 12 hours)
if [ -d "$WORKSPACE/research" ]; then
    recent_research=$(find -P "$WORKSPACE/research" -type f -mmin -720 2>/dev/null | wc -l)
    if [ "$recent_research" -gt 0 ]; then
        research_activity=$((research_activity + recent_research))
    fi
fi

# Calculate event-based score
# Start from time_sat, then events can only make it worse
event_sat=$time_sat

# Confusion directly lowers satisfaction (you're confused RIGHT NOW)
if [ "$confusion_signals" -ge 3 ]; then
    event_sat=0  # Multiple confusion signals = lost
elif [ "$confusion_signals" -ge 1 ]; then
    # Each confusion signal lowers by 1, minimum 1
    penalty=$confusion_signals
    event_sat=$((time_sat - penalty))
    [[ $event_sat -lt 1 ]] && event_sat=1
fi

# Research activity can prevent decay but not override confusion
# (If confused, learning new stuff doesn't help — you need to resolve confusion first)
if [ "$confusion_signals" -eq 0 ]; then
    if [ "$research_activity" -ge 3 ]; then
        [[ $event_sat -lt 3 ]] && event_sat=3
    elif [ "$research_activity" -ge 1 ]; then
        [[ $event_sat -lt 2 ]] && event_sat=2
    fi
fi

echo "$event_sat"
