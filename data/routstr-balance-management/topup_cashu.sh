#!/bin/bash

# Top up balance with Cashu token
CONFIG_FILE="$HOME/.openclaw/openclaw.json"

# Check cashu token argument
if [ -z "$1" ]; then
  echo "Usage: $0 <cashu_token>"
  echo "Example: $0 cashuBo2FteCJodHRwczovL21pbnQubWluaWJpdHMuY2FzaC9CaXRjb2luYXVjc2F0YXSBomFpSAAQeTfbDMhlYXCBo2FhAWFzeEBkNWJjNWYxYmE2YmJlNDQ2NGM3YmI1NjQ4MzBhNWY1ZDRjZDU3ZjJhOTQ3ZGQwYmE0ZjJmYjgwZTNlMmI4NmNhYWNYIQObVC-sFR3tVKwD08eDbJGrvP6J_IZ7k6k2Yn4CjY5Bog"
  exit 1
fi

CASHU_TOKEN="$1"

# Extract base URL and API key from config
BASE_URL=$(jq -r '.models.providers.routstr.baseUrl' "$CONFIG_FILE")
API_KEY=$(jq -r '.models.providers.routstr.apiKey' "$CONFIG_FILE")

# Make topup request (cashu token in query params, not body)
echo "Topping up with Cashu token..."
RESPONSE=$(curl -s -X POST "${BASE_URL}/wallet/topup?cashu_token=$(echo "${CASHU_TOKEN}" | jq -sRr @uri)" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${API_KEY}")

# Display result
echo "$RESPONSE" | jq .

# Show success message if it worked
SUCCESS=$(echo "$RESPONSE" | jq -r '.success')
if [ "$SUCCESS" = "true" ]; then
  echo ""
  echo "Top-up successful!"
elif [ "$SUCCESS" = "null" ] || [ -z "$SUCCESS" ]; then
  # Check if there's an error message
  ERROR=$(echo "$RESPONSE" | jq -r '.error // .message // empty')
  if [ -n "$ERROR" ]; then
    echo ""
    echo "Error: $ERROR"
  fi
fi
