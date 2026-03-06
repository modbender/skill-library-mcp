#!/bin/bash
set -euo pipefail

# gotchi-equip: Unequip all wearables from an Aavegotchi
# Usage: unequip-all.sh <gotchi-id>
# Example: unequip-all.sh 9638

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Validate inputs
if [ $# -ne 1 ]; then
    echo "❌ Usage: unequip-all.sh <gotchi-id>"
    echo ""
    echo "Example:"
    echo "  unequip-all.sh 9638"
    exit 1
fi

GOTCHI_ID="$1"

echo "👻 Unequipping ALL Wearables from Gotchi #$GOTCHI_ID"
echo ""
echo "==================================================================="
echo "Gotchi ID: $GOTCHI_ID"
echo "Action: Remove all equipped wearables"
echo "==================================================================="
echo ""

# Create temp Node.js script
TEMP_SCRIPT=$(mktemp)
trap "rm -f $TEMP_SCRIPT" EXIT

cat > "$TEMP_SCRIPT" << EOF
const { buildUnequipAllTransaction } = require('$SKILL_DIR/lib/equip-lib.js');
const fs = require('fs');

const gotchiId = $GOTCHI_ID;

try {
    const txData = buildUnequipAllTransaction(gotchiId);
    
    console.log('📋 Transaction prepared:');
    console.log('   To:', txData.transaction.to);
    console.log('   Chain:', txData.transaction.chainId);
    console.log('   Description:', txData.description);
    console.log('');
    
    // Save for Bankr submission
    const outFile = '$SKILL_DIR/unequip-tx.json';
    fs.writeFileSync(outFile, JSON.stringify(txData, null, 2));
    console.log('💾 Saved transaction to:', outFile);
    console.log('');
} catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
}
EOF

# Run the script
cd "$SKILL_DIR"
node "$TEMP_SCRIPT"

# Submit via Bankr
echo "🚀 Submitting transaction via Bankr..."
echo ""

BANKR_CONFIG="$HOME/.openclaw/skills/bankr/config.json"
if [ ! -f "$BANKR_CONFIG" ]; then
    echo "❌ Bankr config not found: $BANKR_CONFIG"
    exit 1
fi

API_KEY=$(jq -r '.apiKey' "$BANKR_CONFIG")

RESPONSE=$(curl -s -X POST "https://api.bankr.bot/agent/submit" \
    -H "X-API-Key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d @unequip-tx.json)

echo "$RESPONSE" | jq '.'

# Check success
SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')
if [ "$SUCCESS" = "true" ]; then
    TX_HASH=$(echo "$RESPONSE" | jq -r '.transactionHash')
    echo ""
    echo "==================================================================="
    echo "🎉 SUCCESS! All wearables unequipped!"
    echo "==================================================================="
    echo "Transaction: $TX_HASH"
    echo "View on BaseScan: https://basescan.org/tx/$TX_HASH"
    echo ""
else
    echo ""
    echo "❌ Transaction failed!"
    exit 1
fi
