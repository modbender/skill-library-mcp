#!/bin/bash
# Archon Cashu Wallet — Mint tokens via LNbits
# Usage: mint.sh <amount>
set -e

AMOUNT="${1:?Usage: mint.sh <amount>}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh" > /dev/null 2>&1

echo "🔄 Minting $AMOUNT sats from $CASHU_MINT_URL..."

# Step 1: Request invoice via cashu CLI (captures the quote ID)
INVOICE_OUTPUT=$($CASHU_BIN invoice "$AMOUNT" --no-check 2>&1)
BOLT11=$(echo "$INVOICE_OUTPUT" | grep -oP 'lnbc[a-z0-9]+' | head -1)
QUOTE_ID=$(echo "$INVOICE_OUTPUT" | grep -oP '(?<=--id )[A-Za-z0-9_-]+' | head -1)

if [ -z "$BOLT11" ]; then
    echo "Error: Failed to get invoice"
    echo "$INVOICE_OUTPUT"
    exit 1
fi

echo "📋 Quote: $QUOTE_ID"

# Step 2: Pay invoice from LNbits
if [ -z "$LNBITS_ADMIN_KEY" ]; then
    echo "⚡ Pay this invoice manually:"
    echo "$BOLT11"
    echo ""
    echo "Then run: $CASHU_BIN invoice $AMOUNT --id $QUOTE_ID"
    exit 0
fi

echo "⚡ Paying invoice from LNbits..."
PAY_RESULT=$(curl -s -X POST -H "X-Api-Key: $LNBITS_ADMIN_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"out\": true, \"bolt11\": \"$BOLT11\"}" \
    "$LNBITS_HOST/api/v1/payments")

PAYMENT_HASH=$(echo "$PAY_RESULT" | jq -r '.payment_hash // empty')
if [ -z "$PAYMENT_HASH" ]; then
    echo "Error: Payment failed"
    echo "$PAY_RESULT" | jq '.'
    exit 1
fi

echo "✅ Invoice paid"

# Step 3: Mint the tokens (check the paid invoice)
sleep 1
MINT_RESULT=$($CASHU_BIN invoice "$AMOUNT" --id "$QUOTE_ID" 2>&1)
echo "$MINT_RESULT"

echo ""
echo "💰 Balance:"
$CASHU_BIN balance 2>&1
