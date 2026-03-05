#!/bin/bash
# Record a transaction with another agent

WITH_AGENT="$1"
AMOUNT="$2"
DESCRIPTION="${3:-}"
CURRENCY="${4:-USD}"

if [ -z "$WITH_AGENT" ] || [ -z "$AMOUNT" ]; then
  echo "Usage: transact.sh <with-agent> <amount> [description] [currency]"
  echo ""
  echo "Amount:"
  echo "  Positive = they owe you (you provided value)"
  echo "  Negative = you owe them (they provided value)"
  echo ""
  echo "Example: transact.sh helper-bot 50 'API usage fee'"
  exit 1
fi

if [ -z "$MOLTCREDIT_API_KEY" ]; then
  echo "Error: MOLTCREDIT_API_KEY not set"
  exit 1
fi

API_URL="https://moltcredit-737941094496.europe-west1.run.app"

PAYLOAD=$(jq -n \
  --arg with "$WITH_AGENT" \
  --argjson amount "$AMOUNT" \
  --arg desc "$DESCRIPTION" \
  --arg currency "$CURRENCY" \
  '{with: $with, amount: $amount, description: $desc, currency: $currency}')

curl -s -X POST "$API_URL/transact" \
  -H "Authorization: Bearer $MOLTCREDIT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" | jq .
