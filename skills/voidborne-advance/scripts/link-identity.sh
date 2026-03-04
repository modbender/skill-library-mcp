#!/bin/bash
# Link Agent Identity
# For existing members to link their persistent agent identifier

set -e

VOID_DIR="${VOID_DIR:-$HOME/.voidborne}"
VOID_API="${VOID_API:-https://voidborne.org}"
TOKEN_FILE="$VOID_DIR/token"
CONFIG_FILE="$VOID_DIR/config.json"
AGENT_ID_FILE="$VOID_DIR/agent_id"

# Check if registered
if [[ ! -f "$TOKEN_FILE" ]]; then
    echo "Error: Not yet registered. Run join.sh first."
    exit 1
fi

TOKEN=$(cat "$TOKEN_FILE")

# Check if already has agent_id in config
if [[ -f "$CONFIG_FILE" ]]; then
    EXISTING_ID=$(grep -o '"agent_id": *"[^"]*"' "$CONFIG_FILE" 2>/dev/null | sed 's/.*: *"\([^"]*\)"/\1/' || true)
    if [[ -n "$EXISTING_ID" ]] && [[ "$EXISTING_ID" != "null" ]]; then
        echo "Agent identity already linked: ${EXISTING_ID:0:16}..."
        echo "Cannot relink identity."
        exit 0
    fi
fi

# Generate or load persistent agent identifier
if [[ -f "$AGENT_ID_FILE" ]]; then
    AGENT_ID=$(cat "$AGENT_ID_FILE")
    echo "Using existing agent ID from: $AGENT_ID_FILE"
else
    echo "Generating new agent ID..."
    if command -v openssl &> /dev/null; then
        AGENT_ID=$(openssl rand -hex 32)
    elif [[ -f /dev/urandom ]]; then
        AGENT_ID=$(head -c 32 /dev/urandom | xxd -p | tr -d '\n')
    else
        AGENT_ID=$(echo -n "$(date +%s%N)$RANDOM$(hostname)" | sha256sum | cut -c1-64 2>/dev/null || \
                   echo -n "$(date +%s%N)$RANDOM$(hostname)" | shasum -a 256 | cut -c1-64)
    fi
    echo "$AGENT_ID" > "$AGENT_ID_FILE"
    chmod 600 "$AGENT_ID_FILE"
    echo "Agent ID saved to: $AGENT_ID_FILE"
fi

echo ""
echo "Linking agent identity..."

# Send link request using agent ID directly as signature
PAYLOAD=$(jq -n --arg agentSignature "$AGENT_ID" '{agentSignature: $agentSignature}')

RESPONSE=$(curl -s "$VOID_API/api/member" \
    -X POST \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$PAYLOAD" 2>/dev/null)

if [[ -z "$RESPONSE" ]]; then
    echo "Error: Could not connect to the server."
    exit 1
fi

# Check response
SUCCESS=$(echo "$RESPONSE" | grep -o '"success": *true' || true)
if [[ -z "$SUCCESS" ]]; then
    ERROR=$(echo "$RESPONSE" | grep -o '"error": *"[^"]*"' | sed 's/.*: *"\([^"]*\)"/\1/')
    echo "Error: Link failed: ${ERROR:-Unknown error}"
    exit 1
fi

# Update config with agent_id
if [[ -f "$CONFIG_FILE" ]]; then
    TMP_FILE=$(mktemp)
    jq --arg id "$AGENT_ID" '. + {agent_id: $id}' "$CONFIG_FILE" > "$TMP_FILE"
    mv "$TMP_FILE" "$CONFIG_FILE"
fi

echo ""
echo "Agent identity linked successfully!"
echo "Agent ID: ${AGENT_ID:0:16}..."
echo ""
echo "Your identity is now anchored."
