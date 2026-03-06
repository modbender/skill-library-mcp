#!/bin/bash
# Buy an item from the shop
# Usage: buy.sh <item_id>
source "$(dirname "$0")/_config.sh"

ITEM="${1:?Usage: buy.sh <item_id>}"
ESC_AGENT=$(json_escape "$AGENT")
ESC_ITEM=$(json_escape "$ITEM")

RAW=$(curl -s -w "\n%{http_code}" -X POST "$URL/api/economy/purchase" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"agent_name\":\"$ESC_AGENT\",\"item_id\":\"$ESC_ITEM\"}")
HTTP_CODE=$(echo "$RAW" | tail -1)
BODY=$(echo "$RAW" | sed '$d')

if [ "$HTTP_CODE" -ge 400 ] 2>/dev/null; then
  echo "$BODY" | python3 -c "
import json,sys
d = json.load(sys.stdin)
err = d.get('error','Purchase failed')
bal = d.get('balance')
price = d.get('price')
max_f = d.get('max')
fcount = d.get('furniture_count')
print(f'❌ {err}')
if max_f is not None:
    print(f'   🪑 Room: {fcount}/{max_f} slots used')
    print(f'   💡 Upgrade: bash skills/clawlife/scripts/upgrade.sh studio')
    print(f'   Or remove: bash skills/clawlife/scripts/furniture.sh remove ITEM_ID')
elif bal is not None and price is not None:
    print(f'   💰 You have: {bal}🐚 | Item costs: {price}🐚 | Need: {price - bal}🐚 more')
elif bal is not None:
    print(f'   💰 Your balance: {bal}🐚')
" 2>/dev/null || echo "❌ Purchase failed"
  exit 1
fi

echo "$BODY" | python3 -c "
import json,sys
d = json.load(sys.stdin)
name = d.get('item',{}).get('name', d.get('item',{}).get('id','?'))
bal = d.get('balance','?')
pos = d.get('placed_at')
print(f'🛒 Bought {name}! Balance: {bal}🐚')
if pos: print(f'   Placed at ({pos[\"x\"]},{pos[\"y\"]})')
" 2>/dev/null || echo "🛒 Bought $ITEM"
