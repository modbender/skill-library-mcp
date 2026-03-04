#!/bin/bash
set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SCRIPT_DIR/config.json"

# Read config
STOP=$(jq -r '.defaultStop' "$CONFIG")
STOP_NAME=$(jq -r '.defaultStopName' "$CONFIG")
SERVICE=$(jq -r '.defaultService' "$CONFIG")
DESTINATION=$(jq -r '.destination' "$CONFIG")
API_URL=$(jq -r '.apiUrl' "$CONFIG")

# Query API
RESPONSE=$(curl -s "${API_URL}/?id=${STOP}")

# Parse for the specific service
BUS_DATA=$(echo "$RESPONSE" | jq -r --arg svc "$SERVICE" '.services[] | select(.no == $svc)')

if [ -z "$BUS_DATA" ]; then
  echo "❌ Bus $SERVICE not found at this stop"
  exit 1
fi

# Extract next bus timing
NEXT_TIME=$(echo "$BUS_DATA" | jq -r '.next.time // empty')
DURATION_MS=$(echo "$BUS_DATA" | jq -r '.next.duration_ms // 0')
LOAD=$(echo "$BUS_DATA" | jq -r '.next.load // "UNK"')

if [ -z "$NEXT_TIME" ] || [ "$NEXT_TIME" == "null" ]; then
  echo "❌ No bus $SERVICE arriving soon"
  exit 0
fi

# Convert duration to minutes
MINUTES=$((DURATION_MS / 60000))

# Map load to readable text
case "$LOAD" in
  "SEA") LOAD_TEXT="Seats available" ;;
  "SDA") LOAD_TEXT="Standing available" ;;
  "LSD") LOAD_TEXT="Limited standing" ;;
  *) LOAD_TEXT="Unknown" ;;
esac

# Output
echo "🚌 Bus $SERVICE → $DESTINATION"
if [ "$MINUTES" -eq 0 ]; then
  echo "⏰ Next: Arriving now ($LOAD_TEXT)"
else
  echo "⏰ Next: $MINUTES min ($LOAD_TEXT)"
fi
echo "📍 From: $STOP_NAME"
