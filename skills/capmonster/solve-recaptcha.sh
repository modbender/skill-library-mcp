#!/bin/bash
# CapMonster reCAPTCHA v2 Solver
# Usage: ./solve-recaptcha.sh <website_url> <sitekey>
#
# Example:
#   ./solve-recaptcha.sh "https://scholar.google.com/" "6LfwuyUTAAAAAOAmoS0fdqijC2PbbdH4kjq62Y1b"

set -e

API_KEY="${CAPMONSTER_API_KEY}"
WEBSITE_URL="$1"
SITEKEY="$2"

if [ -z "$WEBSITE_URL" ] || [ -z "$SITEKEY" ]; then
  echo "Usage: $0 <website_url> <sitekey>"
  echo ""
  echo "Example:"
  echo "  $0 \"https://scholar.google.com/\" \"6LfwuyUTAAAAAOAmoS0fdqijC2PbbdH4kjq62Y1b\""
  exit 1
fi

# Create task
echo "🔄 Creating task for: $WEBSITE_URL"
RESPONSE=$(curl -s -X POST https://api.capmonster.cloud/createTask \
  -H "Content-Type: application/json" \
  -d "{
    \"clientKey\": \"$API_KEY\",
    \"task\": {
      \"type\": \"RecaptchaV2TaskProxyless\",
      \"websiteURL\": \"$WEBSITE_URL\",
      \"websiteKey\": \"$SITEKEY\"
    }
  }")

TASK_ID=$(echo "$RESPONSE" | jq -r .taskId)
ERROR_ID=$(echo "$RESPONSE" | jq -r .errorId)

if [ "$ERROR_ID" != "0" ]; then
  echo "❌ Error: $(echo "$RESPONSE" | jq -r .errorDescription)"
  exit 1
fi

echo "📋 Task ID: $TASK_ID"

# Poll for result
echo -n "⏳ Waiting for solution"
for i in {1..60}; do
  RESULT=$(curl -s -X POST https://api.capmonster.cloud/getTaskResult \
    -H "Content-Type: application/json" \
    -d "{\"clientKey\": \"$API_KEY\", \"taskId\": $TASK_ID}")
  
  STATUS=$(echo "$RESULT" | jq -r .status)
  ERROR_ID=$(echo "$RESULT" | jq -r .errorId)
  
  if [ "$ERROR_ID" != "0" ]; then
    echo ""
    echo "❌ Error: $(echo "$RESULT" | jq -r .errorDescription)"
    exit 1
  fi
  
  if [ "$STATUS" = "ready" ]; then
    TOKEN=$(echo "$RESULT" | jq -r '.solution.gRecaptchaResponse')
    COST=$(echo "$RESULT" | jq -r '.cost')
    echo ""
    echo "✅ Solved! Cost: \$$COST"
    echo ""
    echo "=== TOKEN ==="
    echo "$TOKEN"
    echo "============="
    exit 0
  fi
  
  printf "."
  sleep 2
done

echo ""
echo "❌ Timeout after 120 seconds"
exit 1
