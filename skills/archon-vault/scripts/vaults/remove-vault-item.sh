#!/bin/bash
# Remove an item from a vault

set -e

# Ensure environment is loaded
if [ -z "$ARCHON_PASSPHRASE" ]; then
    if [ -f ~/.archon.env ]; then
        source ~/.archon.env
    else
        echo "Error: ARCHON_PASSPHRASE not set. Run create-id.sh first."
        exit 1
    fi
fi

# Set wallet path
if [ -z "$ARCHON_WALLET_PATH" ]; then
    echo "Error: ARCHON_WALLET_PATH not set in ~/.archon.env"
    exit 1
fi

# Check arguments
if [ $# -ne 2 ]; then
    echo "Usage: $0 <vault-id> <item-name>"
    exit 1
fi

VAULT_ID="$1"
ITEM_NAME="$2"

# Remove item from vault
npx @didcid/keymaster remove-vault-item "$VAULT_ID" "$ITEM_NAME"
