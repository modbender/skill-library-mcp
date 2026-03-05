#!/bin/bash
# scan_recognition.sh - Check for external acknowledgment/feedback
# Returns: 3=recent positive feedback, 2=some engagement, 1=ignored, 0=negative feedback
# Event-sensitive: praise, criticism, engagement

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_scan_helper.sh"

NEED="recognition"
# WORKSPACE validated by _scan_helper.sh
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

# Get time-based satisfaction first
time_sat=$(calc_time_satisfaction "$NEED")

# Always check events — recognition matters NOW
positive_signals=0
negative_signals=0

# Scan memory for recognition events (word count)
scan_recognition_events() {
    local file="$1"
    [[ ! -f "$file" ]] && return
    
    # Positive: thanks, great work, helpful, appreciated, good job, upvote, proud
    # Add patterns in your language if needed (see Localization in SKILL.md)
    local pos=$(grep -oiE "(thanks|great work|helpful|appreciated|good job|liked|upvote|positive feedback|well done|nice work|proud|excellent|awesome|kudos|recognized|acknowledged)" "$file" 2>/dev/null | wc -l) || pos=0
    positive_signals=$((positive_signals + pos))
    
    # Negative: wrong, bad, unhelpful, mistake, criticism, disappointed
    local neg=$(grep -oiE "(wrong|bad|unhelpful|mistake|criticism|negative feedback|disappointed|not good|terrible|useless|failed you|let.*down)" "$file" 2>/dev/null | wc -l) || neg=0
    negative_signals=$((negative_signals + neg))
}

scan_recognition_events "$MEMORY_DIR/$TODAY.md"
scan_recognition_events "$MEMORY_DIR/$YESTERDAY.md"

# Calculate net recognition
net=$((positive_signals - negative_signals))

# Calculate event satisfaction
if [[ $negative_signals -gt $positive_signals ]] && [[ $negative_signals -gt 2 ]]; then
    event_sat=0  # Net negative feedback
elif [[ $net -ge 3 ]]; then
    event_sat=3  # Good recognition
elif [[ $net -ge 1 ]]; then
    event_sat=2  # Some engagement
elif [[ $positive_signals -eq 0 ]]; then
    event_sat=1  # Ignored/no feedback
else
    event_sat=$time_sat  # Default to time-based
fi

smart_satisfaction "$NEED" "$event_sat"
