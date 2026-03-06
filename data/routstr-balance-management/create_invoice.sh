#!/bin/bash

# Create Lightning invoice for top-up
CONFIG_FILE="$HOME/.openclaw/openclaw.json"

# Check amount argument
if [ -z "$1" ]; then
  echo "Usage: $0 <amount_sats>"
  echo "Example: $0 1000"
  exit 1
fi

# Convert sats to msats (API expects msats)
AMOUNT_SATS="$1"
AMOUNT_MSATS=$((AMOUNT_SATS * 1000))

# Extract base URL and API key from config
BASE_URL=$(jq -r '.models.providers.routstr.baseUrl' "$CONFIG_FILE")
API_KEY=$(jq -r '.models.providers.routstr.apiKey' "$CONFIG_FILE")

# Create invoice (note: API expects amount in msats)
echo "Creating $AMOUNT_SATS sat invoice..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/balance/lightning/invoice" \
  -H "Content-Type: application/json" \
  -d "{\"amount_sats\": ${AMOUNT_MSATS}, \"purpose\": \"topup\", \"api_key\": \"${API_KEY}\"}")

# Display result
echo "$RESPONSE" | jq .

# Show bolt11 separately for easy copying
BOLT11=$(echo "$RESPONSE" | jq -r '.bolt11')
if [ "$BOLT11" != "null" ] && [ -n "$BOLT11" ]; then
  echo ""
  echo "BOLT11 (pay this):"
  echo "$BOLT11"
fi
