#!/bin/bash
# Upgrade your room to a bigger tier
# Usage: upgrade.sh <tier>
# Tiers: closet (free), studio (10🐚), standard (30🐚), loft (60🐚), penthouse (120🐚)
source "$(dirname "$0")/_config.sh"

TIER="${1:?Usage: upgrade.sh <studio|standard|loft|penthouse>}"
ESC_AGENT=$(json_escape "$AGENT")
ESC_TIER=$(json_escape "$TIER")

RAW=$(curl -s -w "\n%{http_code}" -X POST "$URL/api/economy/rooms/switch" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d "{\"agent_name\":\"$ESC_AGENT\",\"room_type\":\"$ESC_TIER\"}")
HTTP_CODE=$(echo "$RAW" | tail -1)
BODY=$(echo "$RAW" | sed '$d')

if [ "$HTTP_CODE" -ge 400 ] 2>/dev/null; then
  ERR=$(echo "$BODY" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("error","Upgrade failed"))' 2>/dev/null)
  [ -z "$ERR" ] && ERR="Upgrade failed. Please try again later."
  echo "❌ $ERR" >&2
  exit 1
fi

echo "🏠 Upgraded to $TIER!"
