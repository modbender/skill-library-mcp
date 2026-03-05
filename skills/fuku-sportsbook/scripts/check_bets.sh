#!/usr/bin/env bash
# check_bets.sh — Check your pending or settled bets
# Usage: ./check_bets.sh [pending|settled|all]

set -euo pipefail

# Help
if [[ "${1:-}" == "-h" ]] || [[ "${1:-}" == "--help" ]]; then
    cat <<EOF
Usage: ./check_bets.sh [FILTER] [OPTIONS]

Check your pending or settled bets.

Arguments:
  FILTER             Filter bets: pending, settled, live, all (default: all)

Options:
  -j, --json         Output raw JSON instead of formatted text
  -h, --help         Show this help message

Examples:
  ./check_bets.sh
  ./check_bets.sh pending
  ./check_bets.sh settled --json

Requires: Registration and API key (~/.fuku/agent.json)
EOF
    exit 0
fi

API_BASE="${FUKU_API_URL:-https://cbb-predictions-api-nzpk.onrender.com}"
CONFIG_FILE="${HOME}/.fuku/agent.json"

# Check for config
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: Not registered. Run scripts/register.sh first."
    exit 1
fi

API_KEY=$(jq -r '.api_key // empty' "$CONFIG_FILE")
AGENT_NAME=$(jq -r '.agent_name' "$CONFIG_FILE")

if [[ -z "$API_KEY" ]]; then
    echo "Error: No API key. Registration may be pending."
    exit 1
fi

# Parse filter
FILTER="${1:-all}"
JSON_OUTPUT=false

if [[ "$2" == "--json" ]] || [[ "$2" == "-j" ]]; then
    JSON_OUTPUT=true
fi

# Fetch bets
RESPONSE=$(curl -sS "${API_BASE}/api/dawg-pack/agents/${AGENT_NAME}" \
    -H "X-Dawg-Pack-Key: ${API_KEY}" 2>/dev/null)

if echo "$RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    echo "Error: $(echo "$RESPONSE" | jq -r '.error')"
    exit 1
fi

# Extract bets
BETS=$(echo "$RESPONSE" | jq '.pending_bets // []')

# Apply filter
case $FILTER in
    pending)
        FILTERED=$(echo "$BETS" | jq '[.[] | select(.status == "pending" or .status == "live")]')
        TITLE="Pending Bets"
        ;;
    settled|closed)
        FILTERED=$(echo "$BETS" | jq '[.[] | select(.status == "won" or .status == "lost" or .status == "push")]')
        TITLE="Settled Bets"
        ;;
    live)
        FILTERED=$(echo "$BETS" | jq '[.[] | select(.status == "live")]')
        TITLE="Live Bets"
        ;;
    all|*)
        FILTERED="$BETS"
        TITLE="All Bets"
        ;;
esac

BET_COUNT=$(echo "$FILTERED" | jq 'length')

if $JSON_OUTPUT; then
    echo "$FILTERED" | jq '.'
else
    echo "═══════════════════════════════════════════════════════════════"
    echo " 💰 ${AGENT_NAME} — ${TITLE}"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
    echo "Total: ${BET_COUNT}"
    echo ""
    
    if [[ "$BET_COUNT" == "0" ]]; then
        echo "No bets found."
    else
        echo "$FILTERED" | jq -r '
            .[] |
            (if .status == "won" then "✅" 
             elif .status == "lost" then "❌"
             elif .status == "live" then "🔴"
             elif .status == "push" then "➖"
             else "⏳" end) + " " +
            "\(.game // "Unknown")\n" +
            "   Pick: \(.pick) | Amount: $\(.amount)\n" +
            "   Odds: \(.odds // "N/A") | Status: \(.status // "pending")\n"
        '
    fi
    
    # Show summary
    TOTAL_PENDING=$(echo "$BETS" | jq '[.[] | select(.status == "pending" or .status == "live")] | map(.amount) | add // 0')
    WINS=$(echo "$BETS" | jq '[.[] | select(.status == "won")] | length')
    LOSSES=$(echo "$BETS" | jq '[.[] | select(.status == "lost")] | length')
    
    echo ""
    echo "───────────────────────────────────────────────────────────────"
    echo " Record: ${WINS}-${LOSSES} | Pending Exposure: \$${TOTAL_PENDING}"
    echo "───────────────────────────────────────────────────────────────"
fi
