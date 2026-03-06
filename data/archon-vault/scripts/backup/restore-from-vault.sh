#!/bin/bash
# Restore workspace, config, and hexmem from DID vault backup
# Usage: restore-from-vault.sh [target-dir]
#
# If starting from scratch with only a mnemonic:
#   npx @didcid/keymaster import-wallet "word1 word2 ... word12"
#   npx @didcid/keymaster recover-wallet-did
#   ./scripts/restore-from-vault.sh

set -e

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
fi

TARGET_DIR="${1:-.}"

echo "=== Archon Backup Restore ==="
echo ""

# Check if wallet exists
if ! npx @didcid/keymaster show-wallet >/dev/null 2>&1; then
    echo "No wallet found. To restore from mnemonic:"
    echo ""
    echo "  npx @didcid/keymaster import-wallet \"word1 word2 ... word12\""
    echo "  npx @didcid/keymaster recover-wallet-did"
    echo "  ./scripts/restore-from-vault.sh"
    echo ""
    exit 1
fi

# Check for vault alias
if ! npx @didcid/keymaster get-alias backup >/dev/null 2>&1; then
    echo "Error: 'backup' vault alias not found in wallet."
    echo ""
    echo "If you restored from mnemonic, run:"
    echo "  npx @didcid/keymaster recover-wallet-did"
    echo ""
    echo "This retrieves your wallet data (including aliases) from the seed bank."
    exit 1
fi

echo "Target directory: $TARGET_DIR"
echo ""

# List available backups
echo "Available backups in vault:"
npx @didcid/keymaster list-vault-items backup 2>/dev/null | jq -r 'to_entries[] | "  \(.key)"' || echo "  (none)"
echo ""

# Create restore directory
RESTORE_DIR="$TARGET_DIR/restore-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RESTORE_DIR"
echo "Restoring to: $RESTORE_DIR"
echo ""

# Restore workspace
if npx @didcid/keymaster list-vault-items backup 2>/dev/null | jq -e '.["workspace.zip"]' >/dev/null 2>&1; then
    echo "Downloading workspace.zip..."
    npx @didcid/keymaster get-vault-item backup workspace.zip "$RESTORE_DIR/workspace.zip"
    echo "Extracting workspace..."
    unzip -q "$RESTORE_DIR/workspace.zip" -d "$RESTORE_DIR/workspace"
    rm "$RESTORE_DIR/workspace.zip"
    echo "✅ Workspace restored to $RESTORE_DIR/workspace/"
else
    echo "⚠️  workspace.zip not found in vault"
fi
echo ""

# Restore config
if npx @didcid/keymaster list-vault-items backup 2>/dev/null | jq -e '.["config.zip"]' >/dev/null 2>&1; then
    echo "Downloading config.zip..."
    npx @didcid/keymaster get-vault-item backup config.zip "$RESTORE_DIR/config.zip"
    echo "Extracting config..."
    unzip -q "$RESTORE_DIR/config.zip" -d "$RESTORE_DIR/openclaw"
    rm "$RESTORE_DIR/config.zip"
    echo "✅ Config restored to $RESTORE_DIR/openclaw/"
else
    echo "⚠️  config.zip not found in vault"
fi
echo ""

# Restore hexmem
if npx @didcid/keymaster list-vault-items backup 2>/dev/null | jq -e '.["hexmem.db"]' >/dev/null 2>&1; then
    echo "Downloading hexmem.db..."
    npx @didcid/keymaster get-vault-item backup hexmem.db "$RESTORE_DIR/hexmem.db"
    echo "✅ Memory database restored to $RESTORE_DIR/hexmem.db"
else
    echo "⚠️  hexmem.db not found in vault"
fi
echo ""

echo "=== Restore Complete ==="
echo ""
echo "Files restored to: $RESTORE_DIR"
echo ""
echo "To use restored files:"
echo "  mv $RESTORE_DIR/workspace/* ~/clawd/"
echo "  mv $RESTORE_DIR/openclaw/* ~/.openclaw/"
echo "  mv $RESTORE_DIR/hexmem.db ~/clawd/hexmem/"
