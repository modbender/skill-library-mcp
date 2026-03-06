#!/bin/bash
# Get Gigaverse wallet address

SECRETS_DIR="${HOME}/.secrets"
KEY_FILE="${SECRETS_DIR}/gigaverse-private-key.txt"
ADDR_FILE="${SECRETS_DIR}/gigaverse-address.txt"

if [ ! -f "$KEY_FILE" ]; then
    echo "❌ No wallet found. Run setup-wallet.sh first."
    exit 1
fi

ADDRESS=$(cat "$ADDR_FILE" 2>/dev/null || echo "unknown")

echo "Wallet Address: $ADDRESS"
