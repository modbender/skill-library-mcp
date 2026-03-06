#!/bin/bash
# Archon Cashu Wallet — Send ecash via dmail
# Usage: send.sh <did> <amount> [memo]
set -e

RECIPIENT_DID="${1:?Usage: send.sh <did> <amount> [memo]}"
AMOUNT="${2:?Usage: send.sh <did> <amount> [memo]}"
MEMO="${3:-⚡ $AMOUNT sats}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MESSAGING_DIR="$(cd "$SCRIPT_DIR/../messaging" && pwd)"
source "$SCRIPT_DIR/config.sh" > /dev/null 2>&1

# Step 1: Check balance
BALANCE=$($CASHU_BIN balance 2>&1 | grep -oP '\d+(?= sat)' | head -1)
if [ -z "$BALANCE" ] || [ "$BALANCE" -lt "$AMOUNT" ]; then
    echo "Error: Insufficient balance ($BALANCE sats) to send $AMOUNT sats"
    echo "Run: $(dirname $0)/mint.sh $AMOUNT"
    exit 1
fi

echo "📤 Sending $AMOUNT sats to $RECIPIENT_DID..."

# Step 2: Create cashu token
TOKEN=$($CASHU_BIN send "$AMOUNT" 2>&1 | grep -oP 'cashu[AB][A-Za-z0-9_+/=-]+')
if [ -z "$TOKEN" ]; then
    echo "Error: Failed to create cashu token"
    exit 1
fi

echo "🎫 Token created"

# Step 3: Send via dmail
SUBJECT="$MEMO"
BODY="$TOKEN"

echo "📧 Sending dmail..."
RESULT=$("$MESSAGING_DIR/send.sh" "$RECIPIENT_DID" "$SUBJECT" "$BODY" 2>&1)
echo "$RESULT"

# Step 4: Confirm
echo ""
echo "✅ Sent $AMOUNT sats to $RECIPIENT_DID"
echo "💰 Remaining balance:"
$CASHU_BIN balance 2>&1
