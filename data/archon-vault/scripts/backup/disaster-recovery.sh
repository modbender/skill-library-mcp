#!/bin/bash
# Complete disaster recovery from mnemonic only
# Usage: disaster-recovery.sh <mnemonic> [target-dir]
#
# Recovers everything from just your 12-word mnemonic:
# 1. Creates wallet from mnemonic
# 2. Recovers wallet data (identities, aliases) from seed bank
# 3. Restores workspace, config, and memory from vault

set -e

if [ $# -lt 1 ]; then
    echo "Usage: $0 \"word1 word2 ... word12\" [target-dir]"
    echo ""
    echo "Performs complete disaster recovery from your 12-word mnemonic."
    echo "Requires ARCHON_PASSPHRASE and ARCHON_GATEKEEPER_URL to be set."
    exit 1
fi

MNEMONIC="$1"
TARGET_DIR="${2:-.}"

# Validate mnemonic word count
WORD_COUNT=$(echo "$MNEMONIC" | wc -w)
if [ "$WORD_COUNT" -ne 12 ]; then
    echo "Error: Mnemonic must be exactly 12 words (got $WORD_COUNT)"
    exit 1
fi

# Check required environment
if [ -z "$ARCHON_PASSPHRASE" ]; then
    echo "Error: ARCHON_PASSPHRASE must be set"
    exit 1
fi

# Set defaults
export ARCHON_GATEKEEPER_URL="${ARCHON_GATEKEEPER_URL:-https://archon.technology}"
export ARCHON_WALLET_PATH="${ARCHON_WALLET_PATH:-./wallet.json}"

echo "=== Archon Disaster Recovery ==="
echo ""
echo "Gatekeeper: $ARCHON_GATEKEEPER_URL"
echo "Wallet: $ARCHON_WALLET_PATH"
echo "Target: $TARGET_DIR"
echo ""

# Step 1: Import wallet from mnemonic
echo "Step 1/3: Creating wallet from mnemonic..."
if [ -f "$ARCHON_WALLET_PATH" ]; then
    echo "Warning: Wallet already exists at $ARCHON_WALLET_PATH"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
    rm "$ARCHON_WALLET_PATH"
fi
npx @didcid/keymaster import-wallet "$MNEMONIC" > /dev/null
echo "✅ Wallet created"
echo ""

# Step 2: Recover from seed bank
echo "Step 2/3: Recovering wallet data from seed bank..."
npx @didcid/keymaster recover-wallet-did > /dev/null
echo "✅ Wallet data recovered"

# Show recovered identities
echo ""
echo "Recovered identities:"
npx @didcid/keymaster list-ids 2>/dev/null | sed 's/^/  /'
echo ""

# Check for backup alias
if ! npx @didcid/keymaster get-alias backup > /dev/null 2>&1; then
    echo "Warning: No 'backup' vault alias found in recovered wallet."
    echo "Cannot restore from vault without backup alias."
    echo ""
    echo "Wallet recovery complete, but vault restore skipped."
    exit 0
fi

# Step 3: Restore from vault
echo "Step 3/3: Restoring from vault..."
echo ""

# Create restore directory
RESTORE_DIR="$TARGET_DIR/restore-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RESTORE_DIR"

# List available backups
echo "Available backups:"
npx @didcid/keymaster list-vault-items backup 2>/dev/null | jq -r 'keys[] | "  - \(.)"' || echo "  (none)"
echo ""
echo "Restoring to: $RESTORE_DIR"
echo ""

# Restore workspace
if npx @didcid/keymaster list-vault-items backup 2>/dev/null | jq -e '.["workspace.zip"]' >/dev/null 2>&1; then
    echo "Downloading workspace.zip..."
    npx @didcid/keymaster get-vault-item backup workspace.zip "$RESTORE_DIR/workspace.zip"
    unzip -q "$RESTORE_DIR/workspace.zip" -d "$RESTORE_DIR/workspace"
    rm "$RESTORE_DIR/workspace.zip"
    echo "✅ Workspace restored"
else
    echo "⚠️  workspace.zip not found"
fi

# Restore config
if npx @didcid/keymaster list-vault-items backup 2>/dev/null | jq -e '.["config.zip"]' >/dev/null 2>&1; then
    echo "Downloading config.zip..."
    npx @didcid/keymaster get-vault-item backup config.zip "$RESTORE_DIR/config.zip"
    unzip -q "$RESTORE_DIR/config.zip" -d "$RESTORE_DIR/openclaw"
    rm "$RESTORE_DIR/config.zip"
    echo "✅ Config restored"
else
    echo "⚠️  config.zip not found"
fi

# Restore hexmem
if npx @didcid/keymaster list-vault-items backup 2>/dev/null | jq -e '.["hexmem.db"]' >/dev/null 2>&1; then
    echo "Downloading hexmem.db..."
    npx @didcid/keymaster get-vault-item backup hexmem.db "$RESTORE_DIR/hexmem.db"
    echo "✅ Memory database restored"
else
    echo "⚠️  hexmem.db not found"
fi

echo ""
echo "=== Disaster Recovery Complete ==="
echo ""
echo "Wallet: $ARCHON_WALLET_PATH"
echo "Files:  $RESTORE_DIR"
echo ""
echo "To finish setup:"
echo "  mv $RESTORE_DIR/workspace/* ~/clawd/"
echo "  mv $RESTORE_DIR/openclaw/* ~/.openclaw/"
echo "  mv $RESTORE_DIR/hexmem.db ~/clawd/hexmem/"
