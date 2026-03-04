#!/bin/bash
# Test Yollomi API connectivity. Usage: ./test-api.sh [base_url]
# Requires YOLLOMI_API_KEY in environment

set -e
BASE_URL="${1:-${YOLLOMI_BASE_URL:-https://yollomi.com}}"
if [ -z "$YOLLOMI_API_KEY" ]; then
  echo "Error: YOLLOMI_API_KEY not set"
  exit 1
fi

echo "Testing Yollomi API at $BASE_URL..."
RESP=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/api/v1/generate" \
  -H "Authorization: Bearer $YOLLOMI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type":"image","modelId":"flux","prompt":"A simple test","numOutputs":1}')

HTTP_CODE=$(echo "$RESP" | tail -n1)
BODY=$(echo "$RESP" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
  echo "Success. Response (truncated):"
  echo "$BODY" | head -c 200
  echo "..."
else
  echo "Failed (HTTP $HTTP_CODE): $BODY"
  exit 1
fi
