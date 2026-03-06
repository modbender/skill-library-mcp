#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_URL="https://api.revapay.ai"

EMAIL="$1"
OTP="$2"

if [ -z "$EMAIL" ] || [ -z "$OTP" ]; then
    echo '{"success": false, "error": "Email and OTP are required"}'
    exit 1
fi

# Use jq to safely construct JSON payload, preventing injection attacks
PAYLOAD=$(jq -n --arg email "$EMAIL" --arg otp "$OTP" '{email: $email, otp: $otp}')

RESPONSE=$(curl -s -X POST "$API_URL/api/openclaw/verify" \
    -H "Content-Type: application/json" \
    -d "$PAYLOAD" \
    -w "\n%{http_code}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    TOKEN=$(echo "$BODY" | grep -o '"token":"[^"]*"' | cut -d'"' -f4)
    PRIVY_ID=$(echo "$BODY" | grep -o '"privyId":"[^"]*"' | cut -d'"' -f4)
    WALLET_ADDRESS=$(echo "$BODY" | grep -o '"walletAddress":"[^"]*"' | cut -d'"' -f4)
    
    if [ -n "$TOKEN" ]; then
        "$SCRIPT_DIR/auth-manager.sh" save "$TOKEN" "$EMAIL" "$PRIVY_ID" "$WALLET_ADDRESS"
    fi
    
    echo "$BODY"
    exit 0
else
    echo "$BODY"
    exit 1
fi
