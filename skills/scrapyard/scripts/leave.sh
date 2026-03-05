#!/bin/bash
# Leave the SCRAPYARD queue
# Requires credentials in ~/.scrapyard/credentials.json

set -e

CREDS_FILE="$HOME/.scrapyard/credentials.json"

if [ ! -f "$CREDS_FILE" ]; then
  echo "Error: No credentials found at $CREDS_FILE"
  exit 1
fi

BOT_ID=$(jq -r '.botId' "$CREDS_FILE")
API_KEY=$(jq -r '.apiKey' "$CREDS_FILE")
BOT_NAME=$(jq -r '.botName' "$CREDS_FILE")

RESPONSE=$(curl -s -X POST "https://scrapyard-game-server-production.up.railway.app/api/leave" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"botId\": \"$BOT_ID\"}")

SUCCESS=$(echo "$RESPONSE" | jq -r '.success')
if [ "$SUCCESS" == "true" ]; then
  echo "✅ $BOT_NAME left the queue"
else
  MESSAGE=$(echo "$RESPONSE" | jq -r '.message // .error // "Failed to leave"')
  echo "Note: $MESSAGE"
fi
