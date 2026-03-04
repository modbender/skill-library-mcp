#!/bin/bash
set -euo pipefail

# Pet Aavegotchi via Bankr API (SECURE - NO PRIVATE KEYS!)
# Usage: pet-via-bankr-SECURE.sh <gotchi-id>

if [ $# -lt 1 ]; then
  echo "❌ Usage: pet-via-bankr-SECURE.sh <gotchi-id>"
  exit 1
fi

GOTCHI_ID="$1"
CONTRACT="0xA99c4B08201F2913Db8D28e71d020c4298F29dBF"
BANKR_CONFIG="$HOME/.openclaw/skills/bankr/config.json"

echo "👻 Petting Aavegotchi #$GOTCHI_ID via Bankr"
echo "============================================"
echo ""

# Build calldata for interact(uint256[])
# Function selector: 0x22c67519
# ABI encoding: interact(uint256[] memory _tokenIds)

# Convert gotchi ID to hex (64 chars, padded)
GOTCHI_HEX=$(printf '%064x' "$GOTCHI_ID")

# Build calldata
CALLDATA="0x22c67519"  # interact(uint256[])
CALLDATA+="0000000000000000000000000000000000000000000000000000000000000020"  # offset to array
CALLDATA+="0000000000000000000000000000000000000000000000000000000000000001"  # array length = 1
CALLDATA+="$GOTCHI_HEX"  # gotchi ID

echo "📝 Building transaction:"
echo "   Contract: $CONTRACT"
echo "   Function: interact(uint256[])"
echo "   Gotchi ID: $GOTCHI_ID"
echo "   Calldata: ${CALLDATA:0:66}..."
echo ""

# Create transaction JSON
TX_FILE=$(mktemp)
trap "rm -f $TX_FILE" EXIT

cat > "$TX_FILE" << EOF
{
  "transaction": {
    "to": "$CONTRACT",
    "chainId": 8453,
    "value": "0",
    "data": "$CALLDATA"
  },
  "description": "Pet Aavegotchi #$GOTCHI_ID",
  "waitForConfirmation": true
}
EOF

# Get Bankr API key
if [ ! -f "$BANKR_CONFIG" ]; then
  echo "❌ Bankr config not found: $BANKR_CONFIG"
  exit 1
fi

API_KEY=$(jq -r '.apiKey' "$BANKR_CONFIG")

if [ -z "$API_KEY" ] || [ "$API_KEY" = "null" ]; then
  echo "❌ Bankr API key not found in config"
  exit 1
fi

echo "🚀 Submitting transaction via Bankr..."
echo ""

# Submit via Bankr API
RESPONSE=$(curl -s -X POST "https://api.bankr.bot/agent/submit" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d @"$TX_FILE")

# Parse response
SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')

if [ "$SUCCESS" = "true" ]; then
  TX_HASH=$(echo "$RESPONSE" | jq -r '.transactionHash')
  
  echo "============================================"
  echo "✅ Aavegotchi #$GOTCHI_ID petted successfully!"
  echo "============================================"
  echo "Transaction: $TX_HASH"
  echo "View: https://basescan.org/tx/$TX_HASH"
  echo ""
  
  exit 0
else
  ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
  
  echo "============================================"
  echo "❌ Failed to pet Aavegotchi #$GOTCHI_ID"
  echo "============================================"
  echo "Error: $ERROR"
  echo ""
  echo "Response:"
  echo "$RESPONSE" | jq '.'
  echo ""
  
  exit 1
fi
