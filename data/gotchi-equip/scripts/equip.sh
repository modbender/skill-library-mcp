#!/bin/bash
set -euo pipefail

# gotchi-equip: Equip wearables on an Aavegotchi
# Usage: equip.sh <gotchi-id> <slot1=wearableId1> [slot2=wearableId2] ...
# Example: equip.sh 9638 right-hand=64 left-hand=65 head=90

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Validate inputs
if [ $# -lt 2 ]; then
    echo "❌ Usage: equip.sh <gotchi-id> <slot=wearableId> [slot2=wearableId2] ..."
    echo ""
    echo "Valid slots: body, face, eyes, head, left-hand, right-hand, pet, background"
    echo ""
    echo "Example:"
    echo "  equip.sh 9638 right-hand=64"
    echo "  equip.sh 9638 head=90 pet=151 right-hand=64"
    exit 1
fi

GOTCHI_ID="$1"
shift

# Build wearables JSON object
WEARABLES_JSON="{"
FIRST=true
for arg in "$@"; do
    if [[ ! "$arg" =~ ^([a-z-]+)=([0-9]+)$ ]]; then
        echo "❌ Invalid format: $arg"
        echo "   Expected: slot=wearableId (e.g., right-hand=64)"
        exit 1
    fi
    
    SLOT="${BASH_REMATCH[1]}"
    WEARABLE_ID="${BASH_REMATCH[2]}"
    
    if [ "$FIRST" = true ]; then
        FIRST=false
    else
        WEARABLES_JSON+=","
    fi
    
    WEARABLES_JSON+="\"$SLOT\":$WEARABLE_ID"
done
WEARABLES_JSON+="}"

echo "👻 Equipping Wearables on Gotchi #$GOTCHI_ID"
echo ""
echo "==================================================================="
echo "Gotchi ID: $GOTCHI_ID"
echo "Wearables: $WEARABLES_JSON"
echo "==================================================================="
echo ""

# Create temp Node.js script
TEMP_SCRIPT=$(mktemp)
trap "rm -f $TEMP_SCRIPT" EXIT

cat > "$TEMP_SCRIPT" << EOF
const { buildEquipTransaction } = require('$SKILL_DIR/lib/equip-lib.js');
const fs = require('fs');

const gotchiId = $GOTCHI_ID;
const wearables = $WEARABLES_JSON;

try {
    const txData = buildEquipTransaction(gotchiId, wearables);
    
    console.log('📋 Transaction prepared:');
    console.log('   To:', txData.transaction.to);
    console.log('   Chain:', txData.transaction.chainId);
    console.log('   Description:', txData.description);
    console.log('');
    
    // Save for Bankr submission
    const outFile = '$SKILL_DIR/equip-tx.json';
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
    -d @equip-tx.json)

echo "$RESPONSE" | jq '.'

# Check success
SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')
if [ "$SUCCESS" = "true" ]; then
    TX_HASH=$(echo "$RESPONSE" | jq -r '.transactionHash')
    echo ""
    echo "==================================================================="
    echo "🎉 SUCCESS! Wearables equipped!"
    echo "==================================================================="
    echo "Transaction: $TX_HASH"
    echo "View on BaseScan: https://basescan.org/tx/$TX_HASH"
    echo ""
else
    echo ""
    echo "❌ Transaction failed!"
    exit 1
fi
