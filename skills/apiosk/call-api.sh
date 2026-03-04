#!/bin/bash
# Call any Apiosk API with automatic x402 payment
# Usage: ./call-api.sh <api-id> --params '{"key":"value"}'

set -e

WALLET_FILE="$HOME/.apiosk/wallet.json"
CONFIG_FILE="$HOME/.apiosk/config.json"

# Check arguments
if [ $# -lt 3 ]; then
  echo "Usage: ./call-api.sh <api-id> --params '{\"key\":\"value\"}'"
  echo ""
  echo "Example: ./call-api.sh weather --params '{\"city\":\"Amsterdam\"}'"
  exit 1
fi

API_ID=$1
shift
if [ "$1" != "--params" ]; then
  echo "❌ Expected --params flag"
  exit 1
fi
shift
PARAMS=$1

# Load wallet
if [ ! -f "$WALLET_FILE" ]; then
  echo "❌ Wallet not found. Run ./setup-wallet.sh first"
  exit 1
fi

WALLET_ADDRESS=$(jq -r '.address' "$WALLET_FILE")
WALLET_KEY=$(jq -r '.private_key' "$WALLET_FILE")
GATEWAY_URL=$(jq -r '.gateway_url' "$CONFIG_FILE")

# Make request
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$GATEWAY_URL/$API_ID" \
  -H "Content-Type: application/json" \
  -H "X-Wallet-Address: $WALLET_ADDRESS" \
  -d "$PARAMS")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" == "200" ]; then
  echo "$BODY" | jq
  
  # Extract price from response header (if available)
  PRICE=$(echo "$BODY" | jq -r '.meta.price_paid_usdc // 0.001')
  echo ""
  echo "✅ Paid: \$$PRICE USDC"
elif [ "$HTTP_CODE" == "402" ]; then
  echo "❌ Payment required but failed"
  echo "$BODY" | jq
  echo ""
  echo "Check your USDC balance: ./check-balance.sh"
elif [ "$HTTP_CODE" == "404" ]; then
  echo "❌ API not found: $API_ID"
  echo ""
  echo "Available APIs:"
  ./list-apis.sh
else
  echo "❌ Request failed (HTTP $HTTP_CODE)"
  echo "$BODY" | jq
fi
