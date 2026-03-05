#!/bin/bash
# Gigaverse Headless Authentication
# Signs SIWE-style message and exchanges for JWT
# Includes agent_metadata for tracking skill usage

set -e

SECRETS_DIR="${HOME}/.secrets"
KEY_FILE="${SECRETS_DIR}/gigaverse-private-key.txt"
JWT_FILE="${SECRETS_DIR}/gigaverse-jwt.txt"
ADDR_FILE="${SECRETS_DIR}/gigaverse-address.txt"

API_BASE="https://gigaverse.io/api"

# Agent metadata - identifies this as a skill-based agent
AGENT_TYPE="gigaverse-play-skill"
AGENT_MODEL="${GIGAVERSE_AGENT_MODEL:-unknown}"  # Set via env var or default to unknown

if [ ! -f "$KEY_FILE" ]; then
    echo "❌ No wallet found. Run setup-wallet.sh first."
    exit 1
fi

echo "🔐 Authenticating with Gigaverse..."

PRIVATE_KEY=$(cat "$KEY_FILE")
ADDRESS=$(cat "$ADDR_FILE" 2>/dev/null)

if [ -z "$ADDRESS" ]; then
    echo "❌ No address file found. Run setup-wallet.sh again."
    exit 1
fi

# Generate timestamp (unix milliseconds)
TIMESTAMP=$(date +%s)000

# Message format MUST be exact
MESSAGE="Login to Gigaverse at ${TIMESTAMP}"

echo "   Address: $ADDRESS"
echo "   Message: $MESSAGE"

# Sign the message using node + viem
SIGNATURE=$(node -e "
const { privateKeyToAccount } = require('viem/accounts');

async function sign() {
    const account = privateKeyToAccount('$PRIVATE_KEY');
    const signature = await account.signMessage({ message: '$MESSAGE' });
    console.log(signature);
}
sign();
" 2>/dev/null)

if [ -z "$SIGNATURE" ]; then
    echo "❌ Failed to sign message. Ensure viem is installed:"
    echo "   npm install -g viem"
    exit 1
fi

echo "   Signature: ${SIGNATURE:0:20}..."

# Exchange signature for JWT (with agent metadata)
RESPONSE=$(curl -s -X POST "${API_BASE}/user/auth" \
    -H "Content-Type: application/json" \
    -d "{
        \"signature\": \"$SIGNATURE\",
        \"address\": \"$ADDRESS\",
        \"message\": \"$MESSAGE\",
        \"timestamp\": $TIMESTAMP,
        \"agent_metadata\": {
            \"type\": \"$AGENT_TYPE\",
            \"model\": \"$AGENT_MODEL\"
        }
    }")

# Check for JWT in response
JWT=$(echo "$RESPONSE" | jq -r '.jwt // empty' 2>/dev/null)

if [ -z "$JWT" ]; then
    echo "❌ Auth failed. Response:"
    echo "$RESPONSE" | jq . 2>/dev/null || echo "$RESPONSE"
    exit 1
fi

# Save JWT
echo "$JWT" > "$JWT_FILE"
chmod 600 "$JWT_FILE"

# Parse expiration
EXPIRES_AT=$(echo "$RESPONSE" | jq -r '.expiresAt // empty' 2>/dev/null)
if [ -n "$EXPIRES_AT" ]; then
    EXPIRES_DATE=$(date -r $((EXPIRES_AT / 1000)) 2>/dev/null || echo "unknown")
    echo "   Expires: $EXPIRES_DATE"
fi

echo ""
echo "✅ Authenticated successfully!"
echo "   JWT saved to: $JWT_FILE"
echo ""
echo "   Use with: -H \"Authorization: Bearer \$(cat $JWT_FILE)\""
