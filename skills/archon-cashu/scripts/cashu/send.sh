#!/bin/bash
# Archon Cashu Wallet — P2PK-locked send via dmail
# Locks tokens to recipient's DID secp256k1 public key
# Usage: p2pk-send.sh <did> <amount> [memo]
set -e

RECIPIENT_DID="${1:?Usage: p2pk-send.sh <did> <amount> [memo]}"
AMOUNT="${2:?Usage: p2pk-send.sh <did> <amount> [memo]}"
MEMO="${3:-🔒 $AMOUNT sats (P2PK-locked)}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MESSAGING_DIR="$(cd "$SCRIPT_DIR/../messaging" && pwd)"
source "$SCRIPT_DIR/config.sh" > /dev/null 2>&1

# Step 1: Resolve DID and extract secp256k1 pubkey
echo "🔑 Resolving $RECIPIENT_DID..."

# Try local gatekeeper first, then keymaster
DID_DOC=$(curl -s "http://localhost:4224/api/v1/did/$RECIPIENT_DID" 2>/dev/null)
if [ -z "$DID_DOC" ] || echo "$DID_DOC" | jq -e '.error' > /dev/null 2>&1; then
    DID_DOC=$(curl -s "http://localhost:4226/api/v1/ids/$RECIPIENT_DID" 2>/dev/null | jq '.docs')
fi

# Extract JWK public key
JWK_X=$(echo "$DID_DOC" | jq -r '.didDocument.verificationMethod[0].publicKeyJwk.x // empty')
JWK_Y=$(echo "$DID_DOC" | jq -r '.didDocument.verificationMethod[0].publicKeyJwk.y // empty')

if [ -z "$JWK_X" ] || [ -z "$JWK_Y" ]; then
    echo "Error: Could not extract secp256k1 pubkey from DID document"
    echo "DID doc: $DID_DOC" | head -20
    exit 1
fi

# Convert JWK (base64url) to hex compressed pubkey
# x-coordinate determines the prefix (02 if y is even, 03 if odd)
X_HEX=$(echo "$JWK_X" | tr '_-' '/+' | base64 -d 2>/dev/null | xxd -p -c 64)
Y_HEX=$(echo "$JWK_Y" | tr '_-' '/+' | base64 -d 2>/dev/null | xxd -p -c 64)

# Check if y is even or odd (last hex char)
LAST_Y_CHAR="${Y_HEX: -1}"
case "$LAST_Y_CHAR" in
    0|2|4|6|8|a|c|e) PREFIX="02" ;;
    *) PREFIX="03" ;;
esac

COMPRESSED_PUBKEY="${PREFIX}${X_HEX}"
echo "🔐 Locking to pubkey: ${COMPRESSED_PUBKEY:0:16}..."

# Step 2: Check balance
BALANCE=$($CASHU_BIN balance 2>&1 | grep -oP '\d+(?= sat)' | head -1)
if [ -z "$BALANCE" ] || [ "$BALANCE" -lt "$AMOUNT" ]; then
    echo "Error: Insufficient balance ($BALANCE sats) to send $AMOUNT sats"
    exit 1
fi

# Step 3: Create P2PK-locked token
echo "📤 Creating P2PK-locked token for $AMOUNT sats..."
TOKEN_OUTPUT=$($CASHU_BIN send "$AMOUNT" --lock "$COMPRESSED_PUBKEY" 2>&1)
TOKEN=$(echo "$TOKEN_OUTPUT" | grep -oP 'cashu[AB][A-Za-z0-9_+/=-]+')

if [ -z "$TOKEN" ]; then
    echo "Error: Failed to create P2PK token"
    echo "$TOKEN_OUTPUT"
    exit 1
fi

echo "🎫 P2PK token created"

# Step 4: Send via dmail
SUBJECT="$MEMO"
BODY="$TOKEN"

echo "📧 Sending dmail..."
RESULT=$("$MESSAGING_DIR/send.sh" "$RECIPIENT_DID" "$SUBJECT" "$BODY" 2>&1)
echo "$RESULT"

# Step 5: Confirm
echo ""
echo "✅ Sent $AMOUNT sats (P2PK-locked) to $RECIPIENT_DID"
echo "🔐 Only the DID holder can redeem these tokens"
echo "💰 Remaining balance:"
$CASHU_BIN balance 2>&1
