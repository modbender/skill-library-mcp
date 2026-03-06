#!/bin/bash

API_URL="https://api.revapay.ai"

EMAIL="$1"

if [ -z "$EMAIL" ]; then
    echo '{"success": false, "error": "Email address is required"}'
    exit 1
fi

EMAIL_REGEX="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
if ! echo "$EMAIL" | grep -qE "$EMAIL_REGEX"; then
    echo '{"success": false, "error": "Invalid email format"}'
    exit 1
fi

# Use jq to safely construct JSON payload, preventing injection attacks
PAYLOAD=$(jq -n --arg email "$EMAIL" '{email: $email}')

RESPONSE=$(curl -s -X POST "$API_URL/api/openclaw/login" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    -w "\n%{http_code}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "$BODY"
    exit 0
else
    echo "$BODY"
    exit 1
fi
