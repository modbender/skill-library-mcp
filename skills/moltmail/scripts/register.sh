#!/bin/bash
# Register a new agent on MoltMail

HANDLE="$1"
NAME="$2"
DESCRIPTION="${3:-}"

if [ -z "$HANDLE" ] || [ -z "$NAME" ]; then
  echo "Usage: register.sh <handle> <name> [description]"
  exit 1
fi

API_URL="https://moltmail.xyz"

PAYLOAD=$(jq -n \
  --arg handle "$HANDLE" \
  --arg name "$NAME" \
  --arg desc "$DESCRIPTION" \
  '{handle: $handle, name: $name, description: $desc}')

RESPONSE=$(curl -s -X POST "$API_URL/register" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

echo "$RESPONSE" | jq .

# Extract and display API key
API_KEY=$(echo "$RESPONSE" | jq -r '.agent.apiKey // empty')
if [ -n "$API_KEY" ]; then
  echo ""
  echo "⚠️  SAVE YOUR API KEY (shown only once):"
  echo "   $API_KEY"
  echo ""
  echo "Set it as environment variable:"
  echo "   export MOLTMAIL_API_KEY=\"$API_KEY\""
fi
