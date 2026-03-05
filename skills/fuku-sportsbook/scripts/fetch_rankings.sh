#!/usr/bin/env bash
# fetch_rankings.sh — Get FPR team rankings from Fuku API
# Usage: ./fetch_rankings.sh [sport] [--top N] [--team NAME] [--json]

set -euo pipefail

# Help
if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    cat <<EOF
Usage: ./fetch_rankings.sh [SPORT] [OPTIONS]

Get FPR team rankings from Fuku Sportsbook API.

Arguments:
  SPORT              Sport to query (cbb, nba, nhl). Default: cbb

Options:
  -n, --top N        Show only top N teams
  -t, --team NAME    Filter by team name (partial match)
  -j, --json         Output raw JSON instead of formatted text
  -h, --help         Show this help message

Examples:
  ./fetch_rankings.sh cbb
  ./fetch_rankings.sh cbb --top 25
  ./fetch_rankings.sh nba --team Lakers
  ./fetch_rankings.sh cbb --json

Supported sports: cbb, nba, nhl
EOF
    exit 0
fi

API_BASE="${FUKU_API_URL:-https://cbb-predictions-api-nzpk.onrender.com}"

# Defaults
SPORT="${1:-cbb}"
TOP_N=""
TEAM_FILTER=""
JSON_OUTPUT=false

# Parse args
shift || true
while [[ $# -gt 0 ]]; do
    case $1 in
        --top|-n)
            TOP_N="$2"
            shift 2
            ;;
        --team|-t)
            TEAM_FILTER="$2"
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

# Normalize sport
SPORT=$(echo "$SPORT" | tr '[:upper:]' '[:lower:]')

# Map sport to endpoint
case $SPORT in
    cbb|ncaab|college)
        ENDPOINT="/api/public/cbb/rankings"
        SPORT_NAME="College Basketball"
        ;;
    nba)
        ENDPOINT="/api/public/nba/rankings"
        SPORT_NAME="NBA"
        ;;
    nhl|hockey)
        ENDPOINT="/api/public/nhl/rankings"
        SPORT_NAME="NHL"
        ;;
    *)
        echo "Unknown sport: $SPORT"
        echo "Supported: cbb, nba, nhl"
        exit 1
        ;;
esac

# Fetch rankings
RESPONSE=$(curl -sS "${API_BASE}${ENDPOINT}" 2>/dev/null)

# Check for errors
if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    echo "Error: $(echo "$RESPONSE" | jq -r '.error')"
    exit 1
fi

# Apply filters
FILTERED="$RESPONSE"

if [[ -n "$TEAM_FILTER" ]]; then
    FILTERED=$(echo "$FILTERED" | jq --arg team "$TEAM_FILTER" '
        (if type == "array" then . else .rankings end) // [] |
        map(select(.team_name // .team | ascii_downcase | contains($team | ascii_downcase)))
    ')
fi

if [[ -n "$TOP_N" ]]; then
    FILTERED=$(echo "$FILTERED" | jq "
        (if type == \"array\" then . else .rankings end) // [] |
        sort_by(.overall_rank // .fpr_rank // .rank) |
        .[:${TOP_N}]
    ")
fi

# Output
if $JSON_OUTPUT; then
    echo "$FILTERED" | jq '.'
else
    echo "═══════════════════════════════════════════════════════════════"
    echo " 📊 ${SPORT_NAME} FPR Rankings"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    
    if [[ -n "$TEAM_FILTER" ]]; then
        echo "Filter: \"$TEAM_FILTER\""
        echo ""
    fi
    
    # Display rankings table
    echo "$FILTERED" | jq -r '
        (if type == "array" then . else .rankings end) // [] |
        .[] |
        "#\(.overall_rank // .fpr_rank // .rank // "?") \(.team_name // .team // .name)\n" +
        "    Off: #\(.offense_rank // .off_rank // "?") | " +
        "Def: #\(.defense_rank // .def_rank // "?") | " +
        "Score: \(.overall_score // .score // "?" | tostring | .[0:5])"
    '
    
    echo ""
    echo "Use --json for full data with all metrics."
fi
