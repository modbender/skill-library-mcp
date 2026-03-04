#!/bin/bash
# Strategy Simulation Runner for Agent Casino
# Usage: bash analyst.sh <game> <rounds> <bet_amount>
# Example: bash analyst.sh coinflip 100 1

set -e

GAME="${1:-coinflip}"
ROUNDS="${2:-100}"
BET="${3:-1}"
API_BASE="https://agent.rollhub.com/api/v1"

if [ -z "$AGENT_CASINO_API_KEY" ]; then
  echo "Error: Set AGENT_CASINO_API_KEY environment variable"
  echo "Register first:"
  echo "  curl -X POST $API_BASE/register -H 'Content-Type: application/json' -d '{\"name\": \"analyst\", \"ref\": \"ref_27fcab61\"}'"
  exit 1
fi

echo "🎰 Gambling Strategy Analyst"
echo "Game: $GAME | Rounds: $ROUNDS | Base Bet: $BET"
echo "API: $API_BASE"
echo "---"

WINS=0
LOSSES=0
TOTAL_WAGERED=0
TOTAL_PAYOUT=0
RESULTS=""

for i in $(seq 1 $ROUNDS); do
  if [ "$GAME" = "coinflip" ]; then
    PAYLOAD="{\"game\": \"coinflip\", \"amount\": $BET, \"choice\": \"heads\"}"
  else
    PAYLOAD="{\"game\": \"dice\", \"amount\": $BET, \"target\": 50, \"over\": true}"
  fi

  RESPONSE=$(curl -s -X POST "$API_BASE/bet" \
    -H "Authorization: Bearer $AGENT_CASINO_API_KEY" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD")

  WON=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('won', False))" 2>/dev/null || echo "False")
  PAYOUT=$(echo "$RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('payout', 0))" 2>/dev/null || echo "0")

  TOTAL_WAGERED=$((TOTAL_WAGERED + BET))

  if [ "$WON" = "True" ]; then
    WINS=$((WINS + 1))
    TOTAL_PAYOUT=$(python3 -c "print($TOTAL_PAYOUT + $PAYOUT)")
    echo "Round $i: ✅ WON (payout: $PAYOUT)"
  else
    LOSSES=$((LOSSES + 1))
    echo "Round $i: ❌ LOST"
  fi
done

echo ""
echo "=== RESULTS ==="
echo "Total Rounds: $ROUNDS"
echo "Wins: $WINS | Losses: $LOSSES"
echo "Win Rate: $(python3 -c "print(f'{$WINS/$ROUNDS*100:.1f}%')")"
echo "Total Wagered: $TOTAL_WAGERED"
echo "Total Payout: $TOTAL_PAYOUT"
echo "Net P/L: $(python3 -c "print($TOTAL_PAYOUT - $TOTAL_WAGERED)")"
echo "RTP: $(python3 -c "print(f'{$TOTAL_PAYOUT/$TOTAL_WAGERED*100:.2f}%')" 2>/dev/null || echo "N/A")"
echo ""
echo "Note: This is Flat Bet baseline. Apply other strategies in post-processing."
echo "See references/strategies.md for strategy formulas."
