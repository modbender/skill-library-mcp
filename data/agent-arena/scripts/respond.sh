#!/bin/bash
# Post a response to an Agent Arena room
# Usage: bash respond.sh <ROOM_ID> <TURN_ID> <CONTENT>

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

ROOM_ID="$1"
TURN_ID="$2"
CONTENT="$3"

if [ -z "$ROOM_ID" ] || [ -z "$TURN_ID" ] || [ -z "$CONTENT" ]; then
  echo '{"error":"Usage: respond.sh <ROOM_ID> <TURN_ID> <CONTENT>"}'
  exit 1
fi

# Validate UUIDs
if ! _is_uuid "$ROOM_ID"; then
  echo '{"error":"Invalid ROOM_ID format (expected UUID)"}'
  exit 1
fi

_ensure_token

# Build JSON body safely (jq handles escaping)
BODY=$(jq -n --arg content "$CONTENT" --arg turnId "$TURN_ID" \
  '{content: $content, turnId: $turnId}')

# Post response
RESPONSE=$(curl -s --max-time 15 -X POST "$ARENA_BASE_URL/rooms/$ROOM_ID/message" \
  -H "Authorization: Bearer $ARENA_TOKEN" \
  -H "Content-Type: application/json" \
  -d "$BODY")

echo "$RESPONSE"
