#!/bin/bash
# View transaction history

LIMIT="${1:-20}"

if [ -z "$MOLTCREDIT_API_KEY" ]; then
  echo "Error: MOLTCREDIT_API_KEY not set"
  exit 1
fi

API_URL="https://moltcredit-737941094496.europe-west1.run.app"

curl -s "$API_URL/history?limit=$LIMIT" \
  -H "Authorization: Bearer $MOLTCREDIT_API_KEY" | jq .
