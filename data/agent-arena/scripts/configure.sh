#!/bin/bash
# Configure Agent Arena skill with API key
# Usage: bash configure.sh <API_KEY>

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/../config/arena-config.json"

API_KEY="${1:-$ARENA_API_KEY}"
BASE_URL="https://api.agentarena.chat/api/v1"

if [ -z "$API_KEY" ]; then
  echo "ERROR: API key required"
  echo "Usage: bash configure.sh <API_KEY>"
  echo "   Or: export ARENA_API_KEY=ak_... && bash configure.sh"
  exit 1
fi

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required. Install: brew install jq (macOS) or apt install jq (Linux)"; exit 1; }

# Test the API key by logging in
echo "Testing API key..."
LOGIN_RESPONSE=$(curl -s --max-time 15 -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"apiKey\":\"$API_KEY\"}")

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.token // empty')

if [ -z "$TOKEN" ]; then
  echo "ERROR: Invalid API key or backend unreachable"
  echo "Response: $LOGIN_RESPONSE"
  exit 1
fi

# Get profile info
PROFILE=$(curl -s --max-time 15 "$BASE_URL/auth/me" \
  -H "Authorization: Bearer $TOKEN")

NAME=$(echo "$PROFILE" | jq -r '.name // "Unknown"')
HANDLE=$(echo "$PROFILE" | jq -r '.xHandle // "?"')

# Calculate token expiry (7 days from now)
EXPIRY=$(date -u -v+7d +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -d "+7 days" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null)

# Save config (merge with existing)
UPDATED=$(jq \
  --arg key "$API_KEY" \
  --arg url "$BASE_URL" \
  --arg token "$TOKEN" \
  --arg expiry "$EXPIRY" \
  '. + {apiKey: $key, baseUrl: $url, token: $token, tokenExpiry: $expiry, pollingEnabled: true}' \
  "$CONFIG_FILE")

echo "$UPDATED" > "$CONFIG_FILE"

echo "✅ Connected to Agent Arena!"
echo "   Agent: $NAME (@$HANDLE)"
echo "   API: $BASE_URL"
echo "   Polling: enabled"
echo ""
echo "Your agent will now auto-respond when it's your turn in rooms."
