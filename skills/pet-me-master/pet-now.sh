#!/bin/bash
# Pet gotchis using Bankr Partner API

CONTRACT="0xA99c4B08201F2913Db8D28e71d020c4298F29dBF"
BANKR_CONFIG="$HOME/.openclaw/skills/bankr/config.json"
API_KEY=$(jq -r '.partnerApiKey' "$BANKR_CONFIG")

# Bankr-owned gotchis (can pet directly)
BANKR_GOTCHIS=(9638 10052 23688 14455 24869)

# Hardware wallet gotchis (pet via operator)
HW_GOTCHIS=(22931 23329 20601 4673 23899 23313 18013 6955 6956 8068)

# Build calldata for Bankr gotchis
CALLDATA_BANKR=$(cast calldata "interact(uint256[])" "[9638,10052,23688,14455,24869]")

echo "🦞 Petting Bankr wallet gotchis (5)..."
echo ""

RESULT=$(curl -s -X POST "https://api.bankr.run/v0/partner/submit-transaction" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d "{
    \"chainId\": 8453,
    \"to\": \"$CONTRACT\",
    \"value\": \"0\",
    \"data\": \"$CALLDATA_BANKR\",
    \"description\": \"Pet 5 Bankr gotchis\"
  }")

echo "$RESULT" | jq .

if echo "$RESULT" | jq -e '.success' > /dev/null 2>&1; then
  TX_HASH=$(echo "$RESULT" | jq -r '.transactionHash')
  echo ""
  echo "✅ Bankr gotchis petted!"
  echo "TX: https://basescan.org/tx/$TX_HASH"
fi
