#!/usr/bin/env bash
# fetch_predictions.sh — Get today's game predictions from Fuku API
# Usage: ./fetch_predictions.sh [sport] [--date YYYY-MM-DD] [--json]

set -euo pipefail

# Help
if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    cat <<EOF
Usage: ./fetch_predictions.sh [SPORT] [OPTIONS]

Get today's game predictions from Fuku Sportsbook API.

Arguments:
  SPORT              Sport to query (cbb, nba, nhl, soccer). Default: cbb

Options:
  -d, --date DATE    Date in YYYY-MM-DD format. Default: today
  -j, --json         Output raw JSON instead of formatted text
  -h, --help         Show this help message

Examples:
  ./fetch_predictions.sh cbb
  ./fetch_predictions.sh nba --date 2026-02-15
  ./fetch_predictions.sh nhl --json

Supported sports: cbb, nba, nhl, soccer
EOF
    exit 0
fi

API_BASE="${FUKU_API_URL:-https://cbb-predictions-api-nzpk.onrender.com}"

# Defaults
SPORT="${1:-cbb}"
DATE=$(date +%Y-%m-%d)
JSON_OUTPUT=false

# Parse args
shift || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --date|-d)
            DATE="$2"
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

# Normalize sport name
SPORT=$(echo "$SPORT" | tr '[:upper:]' '[:lower:]')

# Map sport to endpoint
case $SPORT in
    cbb|ncaab|college)
        ENDPOINT="/api/public/cbb/predictions"
        SPORT_NAME="College Basketball"
        ;;
    nba)
        ENDPOINT="/api/public/nba/predictions"
        SPORT_NAME="NBA"
        ;;
    nhl|hockey)
        ENDPOINT="/api/public/nhl/predictions"
        SPORT_NAME="NHL"
        ;;
    soccer|football)
        ENDPOINT="/api/public/soccer/predictions"
        SPORT_NAME="Soccer"
        ;;
    *)
        echo "Unknown sport: $SPORT"
        echo "Supported: cbb, nba, nhl, soccer"
        exit 1
        ;;
esac

# Fetch predictions
RESPONSE=$(curl -sS "${API_BASE}${ENDPOINT}?date=${DATE}" 2>/dev/null)

# Check for errors
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    echo "Error: $(echo "$RESPONSE" | jq -r '.error')"
    exit 1
fi

# Output
if $JSON_OUTPUT; then
    echo "$RESPONSE" | jq '.'
else
    GAME_COUNT=$(echo "$RESPONSE" | jq -r '.total_games // (.games | length) // 0')
    
    echo "═══════════════════════════════════════════════════════════════"
    echo " 🏀 ${SPORT_NAME} Predictions — ${DATE}"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Games: ${GAME_COUNT}"
    echo ""
    
    # Parse and display each game
    echo "$RESPONSE" | jq -r '
        .games // [] |
        .[] | 
        "\(.away_team) @ \(.home_team)\n" +
        "  Projected: \(.projected_away_score // 0 | floor)-\(.projected_home_score // 0 | floor)\n" +
        "  Book: \(.book_spread // "N/A") | Total: \(.book_total // "N/A")\n" +
        "  Edge: \(.spread_edge // 0 | . * 10 | floor / 10) pts | Pick: \(.spread_pick // "N/A")\n"
    '
    
    echo ""
    echo "Use --json for full data. Filter with jq for analysis."
fi
