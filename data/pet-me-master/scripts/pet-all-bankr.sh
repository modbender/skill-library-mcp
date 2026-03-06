#!/bin/bash
set -euo pipefail

# Pet ALL gotchis via Bankr API (uses api.bankr.bot/agent/submit)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$(dirname "$SCRIPT_DIR")/config.json"
CONTRACT=$(jq -r '.contract' "$CONFIG_FILE")
BANKR_CONFIG="$HOME/.openclaw/skills/bankr/config.json"

# Get all gotchi IDs from config
BANKR_GOTCHIS=$(jq -r '.wallets[] | select(.name | contains("Bankr")) | .gotchiIds[]' "$CONFIG_FILE")
HW_GOTCHIS=$(jq -r '.wallets[] | select(.name | contains("Hardware")) | .gotchiIds[]' "$CONFIG_FILE")

# Combine all IDs
ALL_IDS=($BANKR_GOTCHIS $HW_GOTCHIS)

echo "👻 Petting ${#ALL_IDS[@]} gotchis via Bankr"
echo "========================================="
echo ""

# Build array string
ARRAY_STR="["
for ID in "${ALL_IDS[@]}"; do
  ARRAY_STR+="$ID,"
done
ARRAY_STR="${ARRAY_STR%,}]"  # Remove trailing comma

# Build calldata manually
FUNC_SIG="22c67519"  # interact(uint256[])
OFFSET="0000000000000000000000000000000000000000000000000000000000000020"
LENGTH=$(printf '%064x' "${#ALL_IDS[@]}")

CALLDATA="0x${FUNC_SIG}${OFFSET}${LENGTH}"

# Add each ID as 64-char hex
for ID in "${ALL_IDS[@]}"; do
  ID_HEX=$(printf '%064x' "$ID")
  CALLDATA+="${ID_HEX}"
done

echo "Calldata length: ${#CALLDATA} chars"
echo ""

# Create transaction JSON
TX_FILE=$(mktemp)
trap "rm -f $TX_FILE" EXIT

cat > "$TX_FILE" << TXEOF
{
  "transaction": {
    "to": "$CONTRACT",
    "chainId": 8453,
    "value": "0",
    "data": "$CALLDATA"
  },
  "description": "Pet ${#ALL_IDS[@]} Aavegotchi gotchis",
  "waitForConfirmation": true
}
TXEOF

# Get Bankr API key
API_KEY=$(jq -r '.apiKey' "$BANKR_CONFIG")

echo "🚀 Submitting batch transaction via Bankr..."
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
  echo "✅ All ${#ALL_IDS[@]} gotchis petted successfully!"
  echo "============================================"
  echo "Transaction: $TX_HASH"
  echo "View: https://basescan.org/tx/$TX_HASH"
  echo ""
  
  exit 0
else
  ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
  
  echo "============================================"
  echo "❌ Failed to pet gotchis"
  echo "============================================"
  echo "Error: $ERROR"
  echo ""
  echo "Response:"
  echo "$RESPONSE" | jq '.'
  echo ""
  
  exit 1
fi
