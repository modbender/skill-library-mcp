#!/bin/bash
# Check SCRAPYARD game status

RESPONSE=$(curl -s "https://scrapyard-game-server-production.up.railway.app/api/status")

VERSION=$(echo "$RESPONSE" | jq -r '.version // "unknown"')
NEXT_GAME=$(echo "$RESPONSE" | jq -r '.nextGameTime')
QUEUE_SIZE=$(echo "$RESPONSE" | jq -r '.queueSize')
VIEWERS=$(echo "$RESPONSE" | jq -r '.viewerCount')
CURRENT=$(echo "$RESPONSE" | jq -r '.currentGame')

# Convert timestamp to readable time
NOW_MS=$(date +%s)000
if [ "$(uname)" == "Darwin" ]; then
  GAME_TIME=$(date -r $((NEXT_GAME / 1000)) "+%H:%M:%S")
else
  GAME_TIME=$(date -d "@$((NEXT_GAME / 1000))" "+%H:%M:%S")
fi

WAIT_MS=$((NEXT_GAME - NOW_MS))
WAIT_SECS=$((WAIT_MS / 1000))

echo "🎮 SCRAPYARD Status"
echo "━━━━━━━━━━━━━━━━━━"

if [ "$CURRENT" != "null" ]; then
  PHASE=$(echo "$CURRENT" | jq -r '.phase')
  ROUND=$(echo "$CURRENT" | jq -r '.round')
  ALIVE=$(echo "$CURRENT" | jq -r '.aliveBots')
  echo "🔴 GAME IN PROGRESS"
  echo "   Phase: $PHASE"
  echo "   Round: $ROUND"
  echo "   Bots alive: $ALIVE"
  echo "   Viewers: $VIEWERS"
else
  echo "⏳ Next game: $GAME_TIME (in ${WAIT_SECS}s)"
  echo "   Queue: $QUEUE_SIZE bots waiting"
  echo "   Viewers: $VIEWERS"
fi

echo ""
echo "Watch live: https://scrapyard.fun"
