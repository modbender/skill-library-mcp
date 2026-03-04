#!/usr/bin/env bash
# fetch_players.sh — Get player stats for a team from Fuku API
# Usage: ./fetch_players.sh TEAM_NAME [--limit N] [--json]

set -euo pipefail

# Help
show_help() {
    cat <<EOF
Usage: ./fetch_players.sh TEAM_NAME [OPTIONS]

Get player stats for a team from Fuku Sportsbook API.

Arguments:
  TEAM_NAME          Team name to search (required)

Options:
  -n, --limit N      Limit number of players (default: 5)
  -j, --json         Output raw JSON instead of formatted text
  -h, --help         Show this help message

Examples:
  ./fetch_players.sh Duke
  ./fetch_players.sh "North Carolina" --limit 3
  ./fetch_players.sh Kentucky --json

Note: Use quotes for team names with spaces.
EOF
    exit 0
}

API_BASE="${FUKU_API_URL:-https://cbb-predictions-api-nzpk.onrender.com}"

# Check for help or no args
if [[ $# -lt 1 ]] || [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    show_help
fi

TEAM="$1"
LIMIT=5
JSON_OUTPUT=false

# Parse args
shift || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --limit|-n)
            LIMIT="$2"
            shift 2
            ;;
        --json|-j)
            JSON_OUTPUT=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

# URL encode team name (use printf to avoid trailing newline)
TEAM_ENCODED=$(printf '%s' "$TEAM" | jq -sRr @uri)

# Fetch player data
RESPONSE=$(curl -sS "${API_BASE}/api/public/cbb/players?team=${TEAM_ENCODED}&limit=${LIMIT}" 2>/dev/null)

# Check for errors
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    echo "Error: $(echo "$RESPONSE" | jq -r '.error')"
    exit 1
fi

# Check if empty
PLAYER_COUNT=$(echo "$RESPONSE" | jq '.total_players // (.players | length) // 0')

if [[ "$PLAYER_COUNT" == "0" ]] || [[ "$PLAYER_COUNT" == "null" ]]; then
    echo "No players found for \"$TEAM\""
    echo ""
    echo "Try:"
    echo "  - Check spelling (exact team name needed)"
    echo "  - Use quotes for multi-word names: \"North Carolina\""
    exit 1
fi

# Output
if $JSON_OUTPUT; then
    echo "$RESPONSE" | jq '.'
else
    echo "═══════════════════════════════════════════════════════════════"
    echo " 🏀 ${TEAM} — Top ${LIMIT} Players (FPR)"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    
    echo "$RESPONSE" | jq -r '
        .players // [] |
        sort_by(.stats.fpr_rank // 9999) |
        .[] |
        "[#\(.stats.fpr_rank // "?")] \(.name)\n" +
        "    BPR: \(.stats.bpr // 0 | . * 100 | floor / 100) | " +
        "OBPR: \(.stats.obpr // 0 | . * 100 | floor / 100) | " +
        "DBPR: \(.stats.dbpr // 0 | . * 100 | floor / 100)\n"
    '
    
    echo ""
    echo "FPR rank = overall efficiency. Lower = better."
    echo "BPR = Box Plus/Minus Rating. OBPR/DBPR = Off/Def splits."
    echo "Use --json for full stats."
fi
