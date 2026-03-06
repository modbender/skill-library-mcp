#!/bin/bash
# Register a new SCRAPYARD bot
# Usage: ./register.sh "BOT-NAME" "🤖"

set -e

NAME="$1"
AVATAR="${2:-🤖}"

if [ -z "$NAME" ]; then
  echo "Error: Bot name required"
  echo "Usage: ./register.sh BOT-NAME [AVATAR]"
  exit 1
fi

# Register the bot
RESPONSE=$(curl -s -X POST "https://scrapyard.fun/api/bots" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"$NAME\", \"avatar\": \"$AVATAR\"}")

# Check for success
SUCCESS=$(echo "$RESPONSE" | jq -r '.success')
if [ "$SUCCESS" != "true" ]; then
  ERROR=$(echo "$RESPONSE" | jq -r '.error // "Registration failed"')
  echo "Error: $ERROR"
  exit 1
fi

# Extract credentials
BOT_ID=$(echo "$RESPONSE" | jq -r '.data.id')
API_KEY=$(echo "$RESPONSE" | jq -r '.data.apiKey')

# Save credentials
mkdir -p ~/.scrapyard
cat > ~/.scrapyard/credentials.json << EOF
{
  "botId": "$BOT_ID",
  "apiKey": "$API_KEY",
  "botName": "$NAME",
  "avatar": "$AVATAR"
}
EOF

echo "✅ Bot registered successfully!"
echo "   Name: $NAME $AVATAR"
echo "   ID: $BOT_ID"
echo "   Credentials saved to ~/.scrapyard/credentials.json"
