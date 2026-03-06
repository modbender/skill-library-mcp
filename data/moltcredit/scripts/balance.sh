#!/bin/bash
# Check balances with other agents

AGENT="$1"

if [ -z "$MOLTCREDIT_API_KEY" ]; then
  echo "Error: MOLTCREDIT_API_KEY not set"
  exit 1
fi

API_URL="https://moltcredit-737941094496.europe-west1.run.app"

if [ -n "$AGENT" ]; then
  # Balance with specific agent
  curl -s "$API_URL/balance/$AGENT" \
    -H "Authorization: Bearer $MOLTCREDIT_API_KEY" | jq .
else
  # All balances
  curl -s "$API_URL/balance" \
    -H "Authorization: Bearer $MOLTCREDIT_API_KEY" | jq .
fi
