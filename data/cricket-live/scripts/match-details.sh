#!/usr/bin/env bash
# Detailed scorecard for a specific match
set -uo pipefail
source "$(dirname "$0")/helpers.sh"

MATCH_ID="${1:-}"

if [[ -z "$MATCH_ID" ]]; then
    echo "❌ Usage: bash scripts/match-details.sh <match-id>"
    echo ""
    echo "Find match IDs via: bash scripts/live-scores.sh"
    echo "Or search: bash scripts/search-match.sh \"India vs Australia\""
    exit 1
fi

response=$(api_call "match_scorecard" "scorecard-${MATCH_ID}" 300 "id=${MATCH_ID}")
rc=$?

if [[ $rc -ne 0 ]]; then
    echo "$response"
    exit 1
fi

name=$(echo "$response" | jq -r '.data.name // "Unknown Match"')
status=$(echo "$response" | jq -r '.data.status // ""')
match_type=$(echo "$response" | jq -r '.data.matchType // ""' | tr '[:lower:]' '[:upper:]')
venue=$(echo "$response" | jq -r '.data.venue // ""')
date_str=$(echo "$response" | jq -r '.data.date // ""')

echo "🏏 *${name}*"
[[ -n "$match_type" ]] && echo "📋 $match_type"
[[ -n "$venue" ]] && echo "📍 $venue"
[[ -n "$date_str" ]] && echo "📅 $(to_ist "$date_str")"
echo ""

# Display scores summary
echo "$response" | jq -r '.data.score // []' | jq -c '.[]' 2>/dev/null | while read -r s; do
    inning=$(echo "$s" | jq -r '.inning // ""')
    runs=$(echo "$s" | jq -r '.r // 0')
    wickets=$(echo "$s" | jq -r '.w // 0')
    overs=$(echo "$s" | jq -r '.o // 0')
    echo "📊 *${inning}:* ${runs}/${wickets} (${overs} ov)"
done

echo ""
[[ -n "$status" ]] && echo "$(format_status "$status")"
echo ""

# Scorecard details (batting)
echo "$response" | jq -c '.data.scorecard // [] | .[]' 2>/dev/null | while read -r innings; do
    inning_num=$(echo "$innings" | jq -r '.inning // "Innings"')
    
    echo "━━━━━━━━━━━━━━━━━━━━━"
    echo "🏏 *${inning_num}*"
    echo ""
    
    # Batting
    echo "🏏 *Batting*"
    echo "$innings" | jq -c '.batting // [] | .[]' 2>/dev/null | while read -r bat; do
        batter=$(echo "$bat" | jq -r '.batsman.name // "Unknown"')
        runs=$(echo "$bat" | jq -r '.r // 0')
        balls=$(echo "$bat" | jq -r '.b // 0')
        fours=$(echo "$bat" | jq -r '."4s" // 0')
        sixes=$(echo "$bat" | jq -r '."6s" // 0')
        dismissal=$(echo "$bat" | jq -r '.dismissal // ""')
        sr=$(echo "$bat" | jq -r '.sr // "0"')
        
        icon=""
        if (( runs >= 100 )); then
            icon="💯 "
        elif (( runs >= 50 )); then
            icon="⭐ "
        fi
        
        if [[ -z "$dismissal" ]] || [[ "$dismissal" == "null" ]] || [[ "$dismissal" == "not out" ]]; then
            echo "  ${icon}${batter}*: ${runs}(${balls}) [${fours}×4, ${sixes}×6] SR:${sr}"
        else
            echo "  ${icon}${batter}: ${runs}(${balls}) [${fours}×4, ${sixes}×6] SR:${sr}"
            echo "    ↳ ${dismissal}"
        fi
    done
    
    echo ""
    
    # Bowling
    echo "⚾ *Bowling*"
    echo "$innings" | jq -c '.bowling // [] | .[]' 2>/dev/null | while read -r bowl; do
        bowler=$(echo "$bowl" | jq -r '.bowler.name // "Unknown"')
        overs=$(echo "$bowl" | jq -r '.o // 0')
        maidens=$(echo "$bowl" | jq -r '.m // 0')
        runs=$(echo "$bowl" | jq -r '.r // 0')
        wickets=$(echo "$bowl" | jq -r '.w // 0')
        econ=$(echo "$bowl" | jq -r '.eco // "0"')
        
        icon=""
        if (( wickets >= 5 )); then
            icon="🔥 "
        elif (( wickets >= 3 )); then
            icon="⭐ "
        fi
        
        echo "  ${icon}${bowler}: ${wickets}/${runs} (${overs} ov) Econ:${econ}"
    done
    
    echo ""
done
