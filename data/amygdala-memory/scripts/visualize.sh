#!/bin/bash
# visualize.sh — Terminal visualization of emotional state
#
# Usage: ./visualize.sh

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
STATE_FILE="$WORKSPACE/memory/emotional-state.json"

if [ ! -f "$STATE_FILE" ]; then
    echo "❌ No emotional state found"
    exit 1
fi

# Read state
STATE=$(cat "$STATE_FILE")

# Extract dimensions
valence=$(echo "$STATE" | jq -r '.dimensions.valence // 0')
arousal=$(echo "$STATE" | jq -r '.dimensions.arousal // 0.3')
connection=$(echo "$STATE" | jq -r '.dimensions.connection // 0.4')
curiosity=$(echo "$STATE" | jq -r '.dimensions.curiosity // 0.5')
energy=$(echo "$STATE" | jq -r '.dimensions.energy // 0.5')
trust=$(echo "$STATE" | jq -r '.dimensions.trust // 0.5')
anticipation=$(echo "$STATE" | jq -r '.dimensions.anticipation // 0')

# Get recent emotion
recent_label=$(echo "$STATE" | jq -r '.recentEmotions[-1].label // "none"')
recent_intensity=$(echo "$STATE" | jq -r '.recentEmotions[-1].intensity // 0')
recent_trigger=$(echo "$STATE" | jq -r '.recentEmotions[-1].trigger // ""')

# Bar function
bar() {
    local value=$1
    local min=$2
    local max=$3
    local width=20
    
    # Normalize to 0-1
    local normalized=$(echo "scale=2; ($value - $min) / ($max - $min)" | bc)
    local filled=$(echo "scale=0; $normalized * $width / 1" | bc)
    
    # Ensure filled is within bounds
    [ "$filled" -lt 0 ] && filled=0
    [ "$filled" -gt "$width" ] && filled=$width
    
    local empty=$((width - filled))
    
    printf "["
    for ((i=0; i<filled; i++)); do printf "█"; done
    for ((i=0; i<empty; i++)); do printf "░"; done
    printf "]"
}

# Mood emoji
mood_emoji() {
    local v=$1
    local a=$2
    
    local vi=$(echo "$v * 100" | bc | cut -d. -f1)
    local ai=$(echo "$a * 100" | bc | cut -d. -f1)
    
    if [ "$vi" -gt 60 ] && [ "$ai" -gt 60 ]; then echo "😄"
    elif [ "$vi" -gt 60 ] && [ "$ai" -le 40 ]; then echo "😌"
    elif [ "$vi" -lt -20 ] && [ "$ai" -gt 60 ]; then echo "😤"
    elif [ "$vi" -lt -20 ] && [ "$ai" -le 40 ]; then echo "😢"
    elif [ "$vi" -gt 30 ]; then echo "🙂"
    elif [ "$vi" -lt -10 ]; then echo "😕"
    else echo "😐"
    fi
}

emoji=$(mood_emoji "$valence" "$arousal")

echo ""
echo "🎭 Emotional State  $emoji"
echo "═══════════════════════════════════════════════"
printf "Valence:      $(bar $valence -1 1)  %+.2f\n" "$valence"
printf "Arousal:      $(bar $arousal 0 1)   %.2f\n" "$arousal"
printf "Connection:   $(bar $connection 0 1)   %.2f  💕\n" "$connection"
printf "Curiosity:    $(bar $curiosity 0 1)   %.2f  🔍\n" "$curiosity"
printf "Energy:       $(bar $energy 0 1)   %.2f  ⚡\n" "$energy"
printf "Trust:        $(bar $trust 0 1)   %.2f  🤝\n" "$trust"
printf "Anticipation: $(bar $anticipation 0 1)   %.2f  ✨\n" "$anticipation"
echo "═══════════════════════════════════════════════"

if [ "$recent_label" != "none" ] && [ "$recent_label" != "null" ]; then
    echo ""
    echo "Recent: $recent_label ($(echo "$recent_intensity * 100" | bc | cut -d. -f1)%)"
    [ -n "$recent_trigger" ] && [ "$recent_trigger" != "null" ] && echo "        ← \"$recent_trigger\""
fi

echo ""
