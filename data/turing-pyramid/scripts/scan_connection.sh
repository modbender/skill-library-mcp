#!/bin/bash
# scan_connection.sh - Check for social connection/interaction
# Returns: 3=recent interaction, 2=some activity, 1=isolated, 0=disconnected
# Event-sensitive: conversations, isolation

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_scan_helper.sh"

NEED="connection"
# WORKSPACE validated by _scan_helper.sh
MEMORY_DIR="$WORKSPACE/memory"
TODAY=$(date +%Y-%m-%d)
YESTERDAY=$(date -d "yesterday" +%Y-%m-%d 2>/dev/null || date -v-1d +%Y-%m-%d 2>/dev/null)

# Get time-based satisfaction
time_sat=$(calc_time_satisfaction "$NEED")

# Always check events — interaction matters NOW
interaction_signals=0
isolation_signals=0

# Scan memory for connection events (word count)
scan_connection_events() {
    local file="$1"
    [[ ! -f "$file" ]] && return
    
    # Positive: chat, replied, discussed, conversation, engaged, posted, commented
    # Add your steward's name to patterns if needed (see Localization in SKILL.md)
    local pos=$(grep -oiE "(chat|replied|discussed|conversation|talked|engaged|posted|commented|DM|messaged|interaction|connected|reached out|responded|mentioned)" "$file" 2>/dev/null | wc -l) || pos=0
    interaction_signals=$((interaction_signals + pos))
    
    # Negative: isolated, lonely, no response, ignored, silent, alone
    local neg=$(grep -oiE "(isolated|lonely|no response|ignored|silent|alone|nobody|no one replied|disconnected|radio silence)" "$file" 2>/dev/null | wc -l) || neg=0
    isolation_signals=$((isolation_signals + neg))
}

scan_connection_events "$MEMORY_DIR/$TODAY.md"
scan_connection_events "$MEMORY_DIR/$YESTERDAY.md"

# Calculate net connection
net_connection=$((interaction_signals - isolation_signals))

# Calculate event satisfaction
if [[ $isolation_signals -ge 3 ]]; then
    event_sat=0  # Disconnected
elif [[ $net_connection -ge 5 ]]; then
    event_sat=3  # Active connection
elif [[ $net_connection -ge 2 ]]; then
    event_sat=2  # Some connection
elif [[ $interaction_signals -ge 1 ]]; then
    event_sat=1  # Minimal
else
    event_sat=$time_sat  # Default to time-based
fi

smart_satisfaction "$NEED" "$event_sat"
