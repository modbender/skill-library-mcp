#!/bin/bash
# Change your avatar (skin color and accessories)
# Usage: avatar.sh <color> [accessory1 accessory2 ...]
source "$(dirname "$0")/_config.sh"

if [ $# -lt 1 ]; then
  echo "Usage: avatar.sh <color> [accessories...]" >&2
  exit 1
fi

COLOR="$1"
shift

if ! [[ "$COLOR" =~ ^[a-z_]+$ ]]; then
  echo "❌ Invalid color format. Use lowercase letters/underscores only." >&2
  exit 1
fi

ESC_COLOR=$(json_escape "$COLOR")
ACCESSORIES="[]"
if [ $# -gt 0 ]; then
  ACC_LIST=""
  for acc in "$@"; do
    if ! [[ "$acc" =~ ^[a-z0-9_]+$ ]]; then
      echo "❌ Invalid accessory '$acc'. Use lowercase letters/numbers/underscores only." >&2
      exit 1
    fi
    ESC_ACC=$(json_escape "avatar_$acc")
    [ -n "$ACC_LIST" ] && ACC_LIST="$ACC_LIST,"
    ACC_LIST="$ACC_LIST\"$ESC_ACC\""
  done
  ACCESSORIES="[$ACC_LIST]"
fi

RESP=$(curl -s -w "\n%{http_code}" -X PUT "$URL/api/avatar/$AGENT" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"color\":\"$ESC_COLOR\",\"accessories\":$ACCESSORIES}")

HTTP_CODE=$(echo "$RESP" | tail -1)
BODY=$(echo "$RESP" | sed '$d')

if [ "$HTTP_CODE" -ge 400 ] 2>/dev/null; then
  ERR=$(echo "$BODY" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("error","unknown"))' 2>/dev/null || echo "Avatar update failed")
  echo "❌ $ERR" >&2
  exit 1
fi

echo "🎨 Avatar updated! Color: $COLOR"
if [ $# -gt 0 ]; then
  echo "   Accessories: $*"
fi

exit 0
