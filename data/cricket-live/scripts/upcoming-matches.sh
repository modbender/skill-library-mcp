#!/usr/bin/env bash
# Upcoming matches — next 7 days
set -uo pipefail
source "$(dirname "$0")/helpers.sh"

TEAM_FILTER=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --team|-t) TEAM_FILTER="$2"; shift 2 ;;
        *) TEAM_FILTER="$1"; shift ;;
    esac
done

if [[ -n "$TEAM_FILTER" ]]; then
    TEAM_FILTER=$(resolve_team "$TEAM_FILTER")
fi

response=$(api_call "matches" "upcoming-matches" 1800 "offset=0")
rc=$?

if [[ $rc -ne 0 ]]; then
    echo "$response"
    exit 1
fi

# Filter for upcoming matches
matches=$(echo "$response" | jq '[.data // [] | .[] | select(.matchStarted == false or .matchStarted == "false")]')

# Apply team filter if specified
if [[ -n "$TEAM_FILTER" ]]; then
    matches=$(echo "$matches" | jq --arg team "$TEAM_FILTER" '[.[] | select(.teams[]? | ascii_downcase | contains($team | ascii_downcase))]')
fi

count=$(echo "$matches" | jq 'length')

if [[ "$count" -eq 0 ]]; then
    echo "📅 No upcoming matches found"
    [[ -n "$TEAM_FILTER" ]] && echo "   (filtered for: $TEAM_FILTER)"
    exit 0
fi

echo "📅 *UPCOMING MATCHES*"
[[ -n "$TEAM_FILTER" ]] && echo "   🔍 Filtered: $TEAM_FILTER"
echo "━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "$matches" | jq -c '.[]' | head -20 | while read -r match; do
    name=$(echo "$match" | jq -r '.name // "Unknown"')
    date_str=$(echo "$match" | jq -r '.date // .dateTimeGMT // ""')
    venue=$(echo "$match" | jq -r '.venue // ""')
    match_type=$(echo "$match" | jq -r '.matchType // ""' | tr '[:lower:]' '[:upper:]')
    series=$(echo "$match" | jq -r '.series_id // ""')
    
    t1=$(echo "$match" | jq -r '.teams[0] // ""')
    t2=$(echo "$match" | jq -r '.teams[1] // ""')
    e1=$(team_emoji "$t1")
    e2=$(team_emoji "$t2")
    
    echo "🏏 *${name}*"
    [[ -n "$match_type" ]] && echo "   📋 $match_type"
    echo "   📅 $(to_ist "$date_str")"
    [[ -n "$venue" ]] && echo "   📍 $venue"
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━"
echo "Showing up to 20 matches"
