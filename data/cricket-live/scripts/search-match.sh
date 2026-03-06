#!/usr/bin/env bash
# Search for a match by team name
set -uo pipefail
source "$(dirname "$0")/helpers.sh"

QUERY="${1:-}"

if [[ -z "$QUERY" ]]; then
    echo "❌ Usage: bash scripts/search-match.sh \"India vs Australia\""
    exit 1
fi

# Extract team names from query (split on "vs", "v", "versus")
TEAM1=$(echo "$QUERY" | sed -E 's/ *(vs?|versus) */\n/' | head -1 | xargs)
TEAM2=$(echo "$QUERY" | sed -E 's/ *(vs?|versus) */\n/' | tail -1 | xargs)

TEAM1=$(resolve_team "$TEAM1")
if [[ "$TEAM1" != "$TEAM2" ]]; then
    TEAM2=$(resolve_team "$TEAM2")
fi

response=$(api_call "matches" "all-matches" 1800 "offset=0")
rc=$?

if [[ $rc -ne 0 ]]; then
    echo "$response"
    exit 1
fi

# Search matches
matches=$(echo "$response" | jq --arg t1 "$TEAM1" --arg t2 "$TEAM2" '[
    .data // [] | .[] | select(
        (.teams // [] | map(ascii_downcase) | any(contains($t1 | ascii_downcase))) and
        (if $t1 != $t2 then
            (.teams // [] | map(ascii_downcase) | any(contains($t2 | ascii_downcase)))
        else true end)
    )
]' 2>/dev/null)

count=$(echo "$matches" | jq 'length')

if [[ "$count" -eq 0 ]]; then
    echo "🔍 No matches found for: $QUERY"
    echo ""
    echo "Try broader search terms or check upcoming matches"
    exit 0
fi

echo "🔍 *SEARCH RESULTS: ${QUERY}*"
echo "━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "$matches" | jq -c '.[]' | head -10 | while read -r match; do
    name=$(echo "$match" | jq -r '.name // "Unknown"')
    id=$(echo "$match" | jq -r '.id // ""')
    status=$(echo "$match" | jq -r '.status // ""')
    date_str=$(echo "$match" | jq -r '.date // .dateTimeGMT // ""')
    match_type=$(echo "$match" | jq -r '.matchType // ""' | tr '[:lower:]' '[:upper:]')
    started=$(echo "$match" | jq -r '.matchStarted // false')
    ended=$(echo "$match" | jq -r '.matchEnded // false')
    
    state_icon="📅"
    if [[ "$ended" == "true" ]]; then
        state_icon="✅"
    elif [[ "$started" == "true" ]]; then
        state_icon="🔴"
    fi
    
    echo "${state_icon} *${name}*"
    [[ -n "$match_type" ]] && echo "   📋 $match_type"
    echo "   📅 $(to_ist "$date_str")"
    [[ -n "$status" ]] && echo "   $(format_status "$status")"
    echo "   🔗 ID: $id"
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Details: bash scripts/match-details.sh <match-id>"
