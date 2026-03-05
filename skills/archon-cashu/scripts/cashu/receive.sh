#!/bin/bash
# Archon Cashu Wallet — Receive ecash from dmail inbox
# Usage: receive.sh [--auto]
set -e

AUTO=false
[ "$1" = "--auto" ] && AUTO=true

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh" > /dev/null 2>&1

echo "📬 Checking dmail inbox for cashu tokens..."

# Step 1: Refresh notices
npx --yes @didcid/keymaster refresh-dmail 2>/dev/null || true

# Step 2: Get all dmails as JSON
DMAILS=$(npx --yes @didcid/keymaster list-dmail 2>/dev/null)
if [ -z "$DMAILS" ] || [ "$DMAILS" = "{}" ]; then
    echo "No messages in inbox."
    exit 0
fi

# Step 3: Extract inbox messages with cashu tokens
TMPFILE=$(mktemp)
echo "$DMAILS" | jq -r '
    to_entries[] | 
    select(.value.tags | index("sent") | not) |
    select(.value.message.body | test("cashu[AB][A-Za-z0-9_+/=-]{20,}")) |
    "\(.value.sender // "Unknown")\t\(.value.message.subject)\t\(.value.message.body)"
' 2>/dev/null > "$TMPFILE" || true

if [ ! -s "$TMPFILE" ]; then
    echo "No cashu tokens found in inbox."
    rm -f "$TMPFILE"
    echo ""
    echo "💰 Current balance:"
    $CASHU_BIN balance 2>&1
    exit 0
fi

# Step 4: Process each token
RECEIVED=0
while IFS=$'\t' read -r SENDER SUBJECT BODY; do
    # Extract all cashu tokens from body
    TOKENS=$(echo "$BODY" | grep -oP 'cashu[AB][A-Za-z0-9_+/=-]{20,}' || true)
    
    for TOKEN in $TOKENS; do
        echo ""
        echo "🎫 Found token from $SENDER ($SUBJECT)"
        
        # Try to receive
        RESULT=$($CASHU_BIN receive "$TOKEN" 2>&1) || true
        
        if echo "$RESULT" | grep -q "Received"; then
            SATS=$(echo "$RESULT" | grep -oP '\d+(?= sat)' | head -1)
            echo "   ✅ Received $SATS sats from $SENDER"
            RECEIVED=$((RECEIVED + 1))
        elif echo "$RESULT" | grep -qi "already spent\|Token already"; then
            echo "   ⚠️  Already redeemed"
        else
            echo "   ❌ Error: $RESULT"
        fi
    done
done < "$TMPFILE"

rm -f "$TMPFILE"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$RECEIVED" -gt 0 ]; then
    echo "📥 Received $RECEIVED new payment(s)"
fi
echo "💰 Current balance:"
$CASHU_BIN balance 2>&1
