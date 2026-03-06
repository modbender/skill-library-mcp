#!/bin/bash
# Create a new vault

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

# Parse arguments
VAULT_ALIAS=""
SECRET_MEMBERS=""
while [[ $# -gt 0 ]]; do
    case $1 in
        -a|--alias)
            VAULT_ALIAS="$2"
            shift 2
            ;;
        -s|--secret-members)
            SECRET_MEMBERS="--secretMembers"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [-a|--alias <vault-alias>] [-s|--secret-members]"
            exit 1
            ;;
    esac
done

# Create vault
if [ -n "$VAULT_ALIAS" ]; then
    npx @didcid/keymaster create-vault --alias "$VAULT_ALIAS" $SECRET_MEMBERS
else
    npx @didcid/keymaster create-vault $SECRET_MEMBERS
fi
