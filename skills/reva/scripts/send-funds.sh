#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
API_URL="https://api.revapay.ai"

# Get arguments
TOKEN_SYMBOL="$1"
CHAIN_SYMBOL="$2"
RECIPIENT="$3"
AMOUNT="$4"

# Get auth token
TOKEN=$("$SCRIPT_DIR/auth-manager.sh" get-token)

if [ -z "$TOKEN" ]; then
    echo '{"success": false, "error": "Not authenticated. Please login first"}'
    exit 1
fi

# Validate required arguments
if [ -z "$TOKEN_SYMBOL" ] || [ -z "$RECIPIENT" ] || [ -z "$AMOUNT" ]; then
    echo '{"success": false, "error": "Missing required arguments: tokenSymbol, recipient, and amount are required"}'
    exit 1
fi

# Determine recipient type and construct payload fields
RECIPIENT_PAYID="null"
RECIPIENT_TWITTER="null"
RECIPIENT_WALLET="null"

# Check recipient type
if [[ "$RECIPIENT" == @* ]]; then
    # Twitter username (remove @)
    RECIPIENT_TWITTER="${RECIPIENT:1}"
elif [[ "$RECIPIENT" == 0x* ]]; then
    # Wallet address
    RECIPIENT_WALLET="$RECIPIENT"
else
    # PayID name
    RECIPIENT_PAYID="$RECIPIENT"
fi

# Construct JSON payload using jq for safety
if [ "$RECIPIENT_PAYID" != "null" ]; then
    PAYLOAD=$(jq -n \
        --arg token "$TOKEN_SYMBOL" \
        --arg chain "$CHAIN_SYMBOL" \
        --arg payid "$RECIPIENT_PAYID" \
        --argjson amount "$AMOUNT" \
        '{
            tokenSymbol: $token,
            chainSymbol: (if $chain == "null" or $chain == "" then null else $chain end),
            recipientPayid: $payid,
            recipientTwitterUsername: null,
            recipientWalletAddress: null,
            amount: $amount
        }')
elif [ "$RECIPIENT_TWITTER" != "null" ]; then
    PAYLOAD=$(jq -n \
        --arg token "$TOKEN_SYMBOL" \
        --arg chain "$CHAIN_SYMBOL" \
        --arg twitter "$RECIPIENT_TWITTER" \
        --argjson amount "$AMOUNT" \
        '{
            tokenSymbol: $token,
            chainSymbol: (if $chain == "null" or $chain == "" then null else $chain end),
            recipientPayid: null,
            recipientTwitterUsername: $twitter,
            recipientWalletAddress: null,
            amount: $amount
        }')
else
    PAYLOAD=$(jq -n \
        --arg token "$TOKEN_SYMBOL" \
        --arg chain "$CHAIN_SYMBOL" \
        --arg wallet "$RECIPIENT_WALLET" \
        --argjson amount "$AMOUNT" \
        '{
            tokenSymbol: $token,
            chainSymbol: (if $chain == "null" or $chain == "" then null else $chain end),
            recipientPayid: null,
            recipientTwitterUsername: null,
            recipientWalletAddress: $wallet,
            amount: $amount
        }')
fi

# Make the API request
RESPONSE=$(curl -s -X POST "$API_URL/api/message/transfer-funds" \
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
