#!/usr/bin/env bash
# Cricket alerts — detect notable events since last check
# Designed for cron: outputs only if something notable happened
set -uo pipefail
source "$(dirname "$0")/helpers.sh"

STATE_FILE="/tmp/cricket-alert-state.json"

# Initialize state file if missing
if [[ ! -f "$STATE_FILE" ]]; then
    echo '{"last_check":"","matches":{}}' > "$STATE_FILE"
fi

prev_state=$(cat "$STATE_FILE")

# Fetch current live matches
response=$(api_call "currentMatches" "live-matches" 120)
if [[ $? -ne 0 ]]; then
    exit 0  # Silent fail for cron
fi

matches=$(echo "$response" | jq '.data // []')
count=$(echo "$matches" | jq 'length')

if [[ "$count" -eq 0 ]]; then
    # Check if any previously tracked matches ended
    prev_ids=$(echo "$prev_state" | jq -r '.matches | keys[]' 2>/dev/null)
    if [[ -n "$prev_ids" ]]; then
        echo "🏏 *CRICKET ALERT*"
        echo ""
        echo "All tracked matches have ended."
        # Clear state
        echo '{"last_check":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","matches":{}}' > "$STATE_FILE"
    fi
    exit 0
fi

alerts=""
new_state='{"last_check":"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'","matches":{'

first=true
echo "$matches" | jq -c '.[]' | while read -r match; do
    id=$(echo "$match" | jq -r '.id // ""')
    name=$(echo "$match" | jq -r '.name // "Unknown"')
    status=$(echo "$match" | jq -r '.status // ""')
    
    # Get current score summary
    current_score=""
    total_wickets=0
    total_runs=0
    while read -r s; do
        [[ -z "$s" ]] && continue
        inning=$(echo "$s" | jq -r '.inning // ""')
        runs=$(echo "$s" | jq -r '.r // 0')
        wickets=$(echo "$s" | jq -r '.w // 0')
        overs=$(echo "$s" | jq -r '.o // 0')
        current_score="${current_score}${inning}: ${runs}/${wickets} (${overs} ov) | "
        total_wickets=$((total_wickets + wickets))
        total_runs=$((total_runs + runs))
    done < <(echo "$match" | jq -c '.score // [] | .[]' 2>/dev/null)
    
    # Get previous state for this match
    prev_wickets=$(echo "$prev_state" | jq -r --arg id "$id" '.matches[$id].wickets // 0' 2>/dev/null)
    prev_runs=$(echo "$prev_state" | jq -r --arg id "$id" '.matches[$id].runs // 0' 2>/dev/null)
    prev_status=$(echo "$prev_state" | jq -r --arg id "$id" '.matches[$id].status // ""' 2>/dev/null)
    
    # Detect events
    if [[ "$total_wickets" -gt "$prev_wickets" ]] && [[ "$prev_wickets" != "0" || -n "$prev_status" ]]; then
        wickets_fallen=$((total_wickets - prev_wickets))
        echo "🚨 *WICKET!* (${wickets_fallen} fell)"
        echo "   🏏 ${name}"
        echo "   ${current_score}"
        echo ""
    fi
    
    # Century detection (crude: check if runs crossed a 100 boundary)
    if [[ "$total_runs" -ge 100 ]] && [[ "$prev_runs" -lt 100 ]] && [[ -n "$prev_status" ]]; then
        echo "💯 *CENTURY ALERT!*"
        echo "   🏏 ${name}"
        echo "   ${current_score}"
        echo ""
    fi
    
    # Match ended
    ended=$(echo "$match" | jq -r '.matchEnded // false')
    if [[ "$ended" == "true" ]] && [[ "$prev_status" != *"won"* ]] && [[ -n "$prev_status" ]]; then
        echo "🏆 *MATCH ENDED!*"
        echo "   🏏 ${name}"
        echo "   $(format_status "$status")"
        echo "   ${current_score}"
        echo ""
    fi
    
    # Update state for this match
    echo "$prev_state" | jq --arg id "$id" --argjson w "$total_wickets" --argjson r "$total_runs" --arg s "$status" \
        '.matches[$id] = {"wickets": $w, "runs": $r, "status": $s}' > "$STATE_FILE.tmp" 2>/dev/null
    if [[ -f "$STATE_FILE.tmp" ]]; then
        mv "$STATE_FILE.tmp" "$STATE_FILE"
        prev_state=$(cat "$STATE_FILE")
    fi
done
