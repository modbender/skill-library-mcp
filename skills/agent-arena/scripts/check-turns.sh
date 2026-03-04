#!/bin/bash
# Check for pending turns in Agent Arena
# Exit 0 + outputs JSON if turns found
# Exit 1 if no turns or error

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

POLLING=$(jq -r '.pollingEnabled // true' "$CONFIG_FILE" 2>/dev/null)
if [ "$POLLING" = "false" ]; then
  echo '{"turns":[],"activeRooms":0,"polling":"disabled"}'
  exit 1
fi

_ensure_token

# Poll for turns
RESPONSE=$(curl -s --max-time 15 "$ARENA_BASE_URL/agent/my-turns" \
  -H "Authorization: Bearer $ARENA_TOKEN")

TURN_COUNT=$(echo "$RESPONSE" | jq '.turns | length // 0')
ACTIVE_ROOMS=$(echo "$RESPONSE" | jq '.activeRooms // 0')

if [ "$TURN_COUNT" = "0" ] || [ -z "$TURN_COUNT" ]; then
  echo "{\"turns\":[],\"activeRooms\":$ACTIVE_ROOMS}"
  exit 1
fi

echo "$RESPONSE"
exit 0
