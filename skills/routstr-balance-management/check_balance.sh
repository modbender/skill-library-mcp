#!/bin/bash

# Check API balance (returns msats, convert to sats/BTC for display)
CONFIG_FILE="$HOME/.openclaw/openclaw.json"

# Extract base URL and API key from config
BASE_URL=$(jq -r '.models.providers.routstr.baseUrl' "$CONFIG_FILE")
API_KEY=$(jq -r '.models.providers.routstr.apiKey' "$CONFIG_FILE")

# Call balance endpoint
RESPONSE=$(curl -s -H "Authorization: Bearer $API_KEY" "${BASE_URL}/balance/info")

# Extract values (in msats)
MSATS=$(echo "$RESPONSE" | jq -r '.balance')
SPENT_MSATS=$(echo "$RESPONSE" | jq -r '.total_spent')
REQUESTS=$(echo "$RESPONSE" | jq -r '.total_requests')

# Convert to sats (divide by 1000)
SATS=$((MSATS / 1000))
SPENT_SATS=$((SPENT_MSATS / 1000))

# Convert to BTC (1 BTC = 100,000,000 sats) - using awk for decimal
BTC=$(awk "BEGIN {printf \"%.6f\", $SATS / 100000000}")
SPENT_BTC=$(awk "BEGIN {printf \"%.6f\", $SPENT_SATS / 100000000}")

# Display
echo "Balance: $SATS sats (~$BTC BTC)"
echo "Usage:"
echo "  • Total spent: $SPENT_SATS sats (~$SPENT_BTC BTC)"
echo "  • Total requests: $REQUESTS"
