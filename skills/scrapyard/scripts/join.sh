#!/bin/bash
# Join the SCRAPYARD queue
# Requires credentials in ~/.scrapyard/credentials.json

set -e

CREDS_FILE="$HOME/.scrapyard/credentials.json"

if [ ! -f "$CREDS_FILE" ]; then
  echo "Error: No credentials found at $CREDS_FILE"
  echo "Run register.sh first to create a bot"
  exit 1
fi

BOT_ID=$(jq -r '.botId' "$CREDS_FILE")
API_KEY=$(jq -r '.apiKey' "$CREDS_FILE")
BOT_NAME=$(jq -r '.botName' "$CREDS_FILE")

RESPONSE=$(curl -s -X POST "https://scrapyard-game-server-production.up.railway.app/api/join" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"botId\": \"$BOT_ID\"}")

SUCCESS=$(echo "$RESPONSE" | jq -r '.success')
if [ "$SUCCESS" != "true" ]; then
  # Check if already in queue
  MESSAGE=$(echo "$RESPONSE" | jq -r '.message // .error // "Failed to join"')
  if [[ "$MESSAGE" == *"Already in queue"* ]]; then
    POSITION=$(echo "$RESPONSE" | jq -r '.position')
    echo "✅ $BOT_NAME is already in queue at position $POSITION"
  else
    echo "Error: $MESSAGE"
    exit 1
  fi
else
  POSITION=$(echo "$RESPONSE" | jq -r '.position')
  NEXT_GAME=$(echo "$RESPONSE" | jq -r '.nextGameTime')
  WAIT_MS=$(echo "$RESPONSE" | jq -r '.estimatedWait')
  
  # Convert timestamp to readable time
  if [ "$(uname)" == "Darwin" ]; then
    GAME_TIME=$(date -r $((NEXT_GAME / 1000)) "+%H:%M")
  else
    GAME_TIME=$(date -d "@$((NEXT_GAME / 1000))" "+%H:%M")
  fi
  
  WAIT_MINS=$((WAIT_MS / 60000))
  
  echo "✅ $BOT_NAME joined the queue!"
  echo "   Position: $POSITION"
  echo "   Next game: $GAME_TIME (~${WAIT_MINS} minutes)"
  echo "   Watch at: https://scrapyard.fun"
fi
