#!/bin/bash
# Extend credit line to another agent

TO_AGENT="$1"
LIMIT="$2"
CURRENCY="${3:-USD}"

if [ -z "$TO_AGENT" ] || [ -z "$LIMIT" ]; then
  echo "Usage: extend-credit.sh <to-agent> <limit> [currency]"
  echo "Example: extend-credit.sh helper-bot 500 USD"
  exit 1
fi

if [ -z "$MOLTCREDIT_API_KEY" ]; then
  echo "Error: MOLTCREDIT_API_KEY not set"
  exit 1
fi

API_URL="https://moltcredit-737941094496.europe-west1.run.app"

PAYLOAD=$(jq -n \
  --arg to "$TO_AGENT" \
  --argjson limit "$LIMIT" \
  --arg currency "$CURRENCY" \
  '{to: $to, limit: $limit, currency: $currency}')

curl -s -X POST "$API_URL/credit/extend" \
  -H "Authorization: Bearer $MOLTCREDIT_API_KEY" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" | jq .
