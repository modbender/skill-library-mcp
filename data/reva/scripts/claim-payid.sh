#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_URL="https://api.revapay.ai"

PAYID="$1"

if [ -z "$PAYID" ]; then
    echo '{"success": false, "error": "PayID is required"}'
    exit 1
fi

PAYID_REGEX="^[a-zA-Z0-9_-]+$"
if ! echo "$PAYID" | grep -qE "$PAYID_REGEX"; then
    echo '{"success": false, "error": "Invalid PayID format. Use only alphanumeric characters, underscores, and hyphens"}'
    exit 1
fi

TOKEN=$("$SCRIPT_DIR/auth-manager.sh" get-token)

if [ -z "$TOKEN" ]; then
    echo '{"success": false, "error": "Not authenticated. Please login first"}'
    exit 1
fi

# Use jq to safely construct JSON payload, preventing injection attacks
PAYLOAD=$(jq -n --arg payid "$PAYID" '{payIdName: $payid}')

RESPONSE=$(curl -s -X POST "$API_URL/api/payid/register" \
    -H "Content-Type: application/json" \
    -H "openclaw-token: $TOKEN" \
    -d "$PAYLOAD" \
    -w "\n%{http_code}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    echo "$BODY"
    exit 0
elif [ "$HTTP_CODE" = "401" ]; then
    "$SCRIPT_DIR/auth-manager.sh" clear
    echo '{"success": false, "error": "Unauthorized or token expired. Please login again"}'
    exit 1
else
    echo "$BODY"
    exit 1
fi
