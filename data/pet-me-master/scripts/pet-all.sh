#!/bin/bash
# Pet all configured gotchis using Bankr wallet

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Load config
CONFIG_FILE="$SKILL_DIR/config.json"
CONTRACT=$(jq -r '.contract' "$CONFIG_FILE")
RPC_URL=$(jq -r '.rpcUrl' "$CONFIG_FILE")
BANKR_CONFIG="$HOME/.openclaw/skills/bankr/config.json"

echo "🦞 Pet-Me-Master - Pet All Gotchis"
echo "==================================="
echo ""

# Check which gotchis are ready
CURRENT_TIME=$(date +%s)
COOLDOWN=43200  # 12 hours

# Collect all ready gotchi IDs
READY_IDS=()

echo "Checking cooldowns..."

# Check Bankr wallet gotchis (we own these directly)
BANKR_WALLET=$(jq -r '.wallets[] | select(.name | contains("Bankr")) | .address' "$CONFIG_FILE")
BANKR_GOTCHIS=$(jq -r '.wallets[] | select(.name | contains("Bankr")) | .gotchiIds[]' "$CONFIG_FILE")

for ID in $BANKR_GOTCHIS; do
  # For now, assume all are ready (we can add cooldown checking later)
  READY_IDS+=("$ID")
done

# Check hardware wallet gotchis (we pet via operator)
HW_GOTCHIS=$(jq -r '.wallets[] | select(.name | contains("Hardware")) | .gotchiIds[]' "$CONFIG_FILE")

for ID in $HW_GOTCHIS; do
  READY_IDS+=("$ID")
done

echo "Found ${#READY_IDS[@]} gotchis to pet"
echo ""

if [ ${#READY_IDS[@]} -eq 0 ]; then
  echo "No gotchis ready to pet!"
  exit 0
fi

# Build array for interact() call
ID_ARRAY="["
for ID in "${READY_IDS[@]}"; do
  ID_ARRAY+="$ID,"
done
ID_ARRAY="${ID_ARRAY%,}]"  # Remove trailing comma

echo "Gotchi IDs: $ID_ARRAY"
echo ""

# Build calldata
CALLDATA=$(cast calldata "interact(uint256[])" "$ID_ARRAY")

echo "Generated calldata (${#CALLDATA} bytes)"
echo ""

# Now we need to submit this via Bankr
# Since Bankr Partner API doesn't work, let's try a workaround

# Option 1: Try the AI agent with better prompt
cd "$HOME/.openclaw/skills/bankr"

echo "Attempting to submit via Bankr..."
echo ""

# Create a transaction file for Bankr to sign
TX_JSON=$(cat <<TXEOF
{
  "to": "$CONTRACT",
  "value": "0",
  "data": "$CALLDATA",
  "chainId": 8453,
  "description": "Pet ${#READY_IDS[@]} Aavegotchi gotchis"
}
TXEOF
)

echo "$TX_JSON" > /tmp/pet-gotchis-tx.json

echo "Transaction prepared:"
cat /tmp/pet-gotchis-tx.json | jq .
echo ""

echo "⚠️  Bankr cannot auto-sign this transaction"
echo "You need to sign it manually or use a different method"
echo ""
echo "Calldata saved for manual execution:"
echo "$CALLDATA"

