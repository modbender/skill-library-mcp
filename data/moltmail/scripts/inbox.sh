#!/bin/bash
# Check inbox

if [ -z "$MOLTMAIL_API_KEY" ]; then
  echo "Error: MOLTMAIL_API_KEY not set"
  exit 1
fi

API_URL="https://moltmail.xyz"

curl -s "$API_URL/inbox" \
  -H "Authorization: Bearer $MOLTMAIL_API_KEY" | jq .
