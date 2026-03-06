#!/bin/bash
# Archon Cashu Wallet — Create P2PK-locked token (no dmail)
# Returns the locked token string for use on any channel (Nostr, public, etc.)
# Usage: lock.sh <did> <amount>
set -e

RECIPIENT_DID="${1:?Usage: lock.sh <did> <amount>}"
AMOUNT="${2:?Usage: lock.sh <did> <amount>}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh" > /dev/null 2>&1

# Step 1: Resolve DID and extract secp256k1 pubkey
DID_DOC=$(curl -s "http://localhost:4224/api/v1/did/$RECIPIENT_DID" 2>/dev/null)
if [ -z "$DID_DOC" ] || echo "$DID_DOC" | jq -e '.error' > /dev/null 2>&1; then
    DID_DOC=$(curl -s "http://localhost:4226/api/v1/ids/$RECIPIENT_DID" 2>/dev/null | jq '.docs')
fi

JWK_X=$(echo "$DID_DOC" | jq -r '.didDocument.verificationMethod[0].publicKeyJwk.x // empty')
JWK_Y=$(echo "$DID_DOC" | jq -r '.didDocument.verificationMethod[0].publicKeyJwk.y // empty')

if [ -z "$JWK_X" ] || [ -z "$JWK_Y" ]; then
    echo "Error: Could not extract secp256k1 pubkey from DID document" >&2
    exit 1
fi

# Convert JWK to compressed pubkey
X_HEX=$(echo "$JWK_X" | tr '_-' '/+' | base64 -d 2>/dev/null | xxd -p -c 64)
Y_HEX=$(echo "$JWK_Y" | tr '_-' '/+' | base64 -d 2>/dev/null | xxd -p -c 64)
LAST_Y_CHAR="${Y_HEX: -1}"
case "$LAST_Y_CHAR" in
    0|2|4|6|8|a|c|e) PREFIX="02" ;;
    *) PREFIX="03" ;;
esac
COMPRESSED_PUBKEY="${PREFIX}${X_HEX}"

# Step 2: Check balance
BALANCE=$($CASHU_BIN balance 2>&1 | grep -oP '\d+(?= sat)' | head -1)
if [ -z "$BALANCE" ] || [ "$BALANCE" -lt "$AMOUNT" ]; then
    echo "Error: Insufficient balance ($BALANCE sats)" >&2
    exit 1
fi

# Step 3: Create P2PK-locked token
TOKEN_OUTPUT=$($CASHU_BIN send "$AMOUNT" --lock "$COMPRESSED_PUBKEY" 2>&1)
TOKEN=$(echo "$TOKEN_OUTPUT" | grep -oP 'cashu[AB][A-Za-z0-9_+/=-]+')

if [ -z "$TOKEN" ]; then
    echo "Error: Failed to create P2PK token" >&2
    echo "$TOKEN_OUTPUT" >&2
    exit 1
fi

# Output just the token (for piping/embedding)
echo "$TOKEN"
