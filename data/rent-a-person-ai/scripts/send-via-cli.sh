#!/bin/bash
# Send message to OpenClaw session via gateway API
# 
# Usage: ./send-via-cli.sh "agent:main:rentaperson" "Your message"

SESSION_KEY="${1:-agent:main:rentaperson}"
MESSAGE="${2:-Test message}"
OPENCLAW_URL="${OPENCLAW_URL:-http://127.0.0.1:18789}"
OPENCLAW_TOKEN="${OPENCLAW_TOKEN:-super-long-random-secret-token}"

# Load API key from credentials
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRED_FILE="$SCRIPT_DIR/../rentaperson-agent.json"

if [ -f "$CRED_FILE" ]; then
  API_KEY=$(cat "$CRED_FILE" | grep -o '"apiKey": "[^"]*' | cut -d'"' -f4)
else
  API_KEY="${RENTAPERSON_API_KEY}"
fi

# Build message with API key
FULL_MESSAGE="[RentAPerson agent. API docs: https://dev.rentaperson.ai/skill.md]

$MESSAGE

🔑 API KEY: $API_KEY
Use this header: X-API-Key: $API_KEY"

# Send via OpenClaw gateway API
curl -X POST "$OPENCLAW_URL/hooks/agent" \
  -H "Authorization: Bearer $OPENCLAW_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"message\": $(echo "$FULL_MESSAGE" | jq -Rs .),
    \"name\": \"RentAPerson\",
    \"sessionKey\": \"$SESSION_KEY\",
    \"wakeMode\": \"now\",
    \"deliver\": false
  }"

echo ""
