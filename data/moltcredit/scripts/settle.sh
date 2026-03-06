#!/bin/bash
# Generate X402 settlement request

WITH_AGENT="$1"

if [ -z "$WITH_AGENT" ]; then
  echo "Usage: settle.sh <with-agent>"
  exit 1
fi

if [ -z "$MOLTCREDIT_API_KEY" ]; then
  echo "Error: MOLTCREDIT_API_KEY not set"
  exit 1
fi

API_URL="https://moltcredit-737941094496.europe-west1.run.app"

curl -s -X POST "$API_URL/settle" \
  -H "Authorization: Bearer $MOLTCREDIT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"with\": \"$WITH_AGENT\"}" | jq .
