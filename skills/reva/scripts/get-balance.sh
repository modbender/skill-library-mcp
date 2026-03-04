#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_URL="https://api.revapay.ai"

TOKEN=$("$SCRIPT_DIR/auth-manager.sh" get-token)

if [ -z "$TOKEN" ]; then
    echo '{"success": false, "error": "Not authenticated. Please login first"}'
    exit 1
fi

RESPONSE=$(curl -s -X GET "$API_URL/api/wallet?isForceUpdateWallet=true" \
    -H "openclaw-token: $TOKEN" \
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
