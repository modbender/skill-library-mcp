#!/bin/bash
# SplitXCH API wrapper - creates a split address from a JSON payload
# Usage: splitxch.sh <json-file-or-stdin>
# Input: JSON with "recipients" array [{name, address, points, id}]
# Points must sum to 9850 (API adds 150 bps fee)

set -euo pipefail

API_URL="https://splitxch.com/api/compute/fast"

if [ -n "${1:-}" ] && [ -f "$1" ]; then
  PAYLOAD=$(cat "$1")
else
  PAYLOAD=$(cat -)
fi

# Validate JSON has recipients
if ! echo "$PAYLOAD" | jq -e '.recipients' >/dev/null 2>&1; then
  echo "Error: JSON must contain 'recipients' array" >&2
  exit 1
fi

# Validate points sum to 9850
TOTAL=$(echo "$PAYLOAD" | jq '[.recipients[].points] | add')
if [ "$TOTAL" != "9850" ]; then
  echo "Error: Recipient points sum to $TOTAL, must be 9850 (10000 - 150 fee)" >&2
  exit 1
fi

# Call API
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo "API Error (HTTP $HTTP_CODE): $BODY" >&2
  exit 1
fi

echo "$BODY" | jq .
