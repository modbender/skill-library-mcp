#!/bin/bash
# List shop items
# Usage: shop.sh
source "$(dirname "$0")/_config.sh"

if [ $# -ne 0 ]; then
  echo "Usage: shop.sh" >&2
  exit 1
fi

RESP=$(api_get "/api/economy/shop") || exit 1
echo "$RESP" | python3 -c "
import json,sys
data = json.load(sys.stdin)
shop = data.get('shop', {})
for category, items in shop.items():
    print(f'\n  === {category.upper()} ===')
    for i in items:
        owned = ' ✅ OWNED' if i.get('owned') else ''
        print(f'  {i[\"id\"]:25s} {i.get(\"price\",\"?\"):>4}🐚  {i.get(\"name\",\"\")} — {i.get(\"description\",\"\")[:50]}{owned}')
"
