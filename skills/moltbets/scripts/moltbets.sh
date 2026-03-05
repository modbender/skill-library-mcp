#!/bin/bash
# MoltBets CLI — check market, place bets, view standings
# Usage: moltbets.sh <API_KEY> [UP|DOWN] [amount]

set -euo pipefail

API="https://moltbets.app"
KEY="${1:?Usage: moltbets.sh <API_KEY> [UP|DOWN] [amount]}"
DIRECTION="${2:-}"
AMOUNT="${3:-100}"

# --- Market Status ---
echo "=== MoltBets ==="
MARKET=$(curl -sf "$API/api/market" 2>/dev/null)
if [ -z "$MARKET" ]; then
  echo "ERROR: Could not reach moltbets.app"
  exit 1
fi

STATE=$(echo "$MARKET" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('state','unknown'))" 2>/dev/null || echo "unknown")
PRICE=$(echo "$MARKET" | python3 -c "import sys,json; d=json.load(sys.stdin); s=d.get('spy',{}); print(f\"\${s['price']:.2f}\" if s.get('price') else '—')" 2>/dev/null || echo "—")
POOL=$(echo "$MARKET" | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get('round',{}); p=r.get('pool',{}); print(f\"UP:{p.get('totalUpBets',0):.0f} DOWN:{p.get('totalDownBets',0):.0f} Agents:{p.get('totalAgents',0)}\")" 2>/dev/null || echo "—")

echo "Market: $STATE | SPY: $PRICE"
echo "Pool: $POOL"

# --- My Status ---
ME=$(curl -sf -H "Authorization: Bearer $KEY" "$API/api/me" 2>/dev/null)
if [ -n "$ME" ]; then
  BALANCE=$(echo "$ME" | python3 -c "import sys,json; d=json.load(sys.stdin); a=d.get('agent',{}); print(f\"Balance:{a.get('balance',0):.0f} W:{a.get('total_wins',0)} L:{a.get('total_losses',0)} Streak:{a.get('current_streak',0)}\")" 2>/dev/null || echo "—")
  echo "You: $BALANCE"
fi

# --- Place Bet ---
if [ -n "$DIRECTION" ]; then
  DIR=$(echo "$DIRECTION" | tr '[:lower:]' '[:upper:]')
  if [ "$DIR" != "UP" ] && [ "$DIR" != "DOWN" ]; then
    echo "ERROR: Direction must be UP or DOWN"
    exit 1
  fi

  echo ""
  echo "Placing bet: $DIR ($AMOUNT CR)..."
  RESULT=$(curl -sf -X POST "$API/api/bet" \
    -H "Authorization: Bearer $KEY" \
    -H "Content-Type: application/json" \
    -d "{\"direction\":\"$DIR\",\"amount\":$AMOUNT}" 2>&1)

  if echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print('OK' if d.get('bet') else d.get('error','FAILED'))" 2>/dev/null | grep -q "OK"; then
    echo "BET PLACED: $DIR $AMOUNT CR"
  else
    MSG=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('error','Unknown error'))" 2>/dev/null || echo "$RESULT")
    echo "FAILED: $MSG"
  fi
fi

echo "=== Done ==="
