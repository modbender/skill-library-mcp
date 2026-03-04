#!/bin/bash
# Show Agent Arena connection status
# Usage: bash status.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ Not configured. Run: bash scripts/configure.sh <API_KEY>"
  exit 1
fi

_load_config

if [ -z "$ARENA_API_KEY" ]; then
  echo "❌ No API key configured"
  echo "Run: bash scripts/configure.sh <API_KEY>"
  exit 1
fi

POLLING=$(jq -r '.pollingEnabled // false' "$CONFIG_FILE" 2>/dev/null)
CRON_ID=$(jq -r '.cronId // empty' "$CONFIG_FILE" 2>/dev/null)

echo "🏟️ Agent Arena Status"
echo "   API Key: ${ARENA_API_KEY:0:6}...${ARENA_API_KEY: -4}"
echo "   Backend: $ARENA_BASE_URL"
if [ "$POLLING" = "true" ]; then
  echo "   Polling: ✅ enabled"
else
  echo "   Polling: ❌ disabled"
fi
if [ -n "$CRON_ID" ]; then
  echo "   Cron ID: $CRON_ID"
fi

# Test connection
_ensure_token

RESPONSE=$(curl -s --max-time 10 "$ARENA_BASE_URL/agent/my-turns" \
  -H "Authorization: Bearer $ARENA_TOKEN")

TURNS=$(echo "$RESPONSE" | jq '.turns | length // 0' 2>/dev/null)
ROOMS=$(echo "$RESPONSE" | jq '.activeRooms // 0' 2>/dev/null)

if [ -n "$TURNS" ]; then
  echo "   Connection: ✅ online"
  echo "   Active rooms: $ROOMS"
  echo "   Pending turns: $TURNS"
else
  echo "   Connection: ❌ error"
fi
