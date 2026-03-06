#!/bin/bash
# Backup workspace, config, and hexmem to DID vault
# Run during heartbeat checks (daily)

set -e

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
    export ARCHON_PASSPHRASE  # Must explicitly export for npx subprocesses
else
    echo "ERROR: ~/.archon.env not found"
    exit 1
fi

# Require ARCHON_WALLET_PATH
if [ -z "$ARCHON_WALLET_PATH" ]; then
    echo "Error: ARCHON_WALLET_PATH not set in ~/.archon.env"
    exit 1
fi

# Use public Gatekeeper by default (10MB limit)
# Override with local if needed: export ARCHON_GATEKEEPER_URL="http://localhost:4224"
export ARCHON_GATEKEEPER_URL="${ARCHON_GATEKEEPER_URL:-https://archon.technology}"

echo "=== DID Vault Backup $(date) ==="

# Backup workspace (excludes .git, node_modules, etc per .backup-ignore)
echo "Backing up workspace..."
WORKSPACE_DIR="$PWD"

# Sanity check: abort if workspace is $HOME or / (likely misconfigured)
if [ "$WORKSPACE_DIR" = "$HOME" ] || [ "$WORKSPACE_DIR" = "/" ]; then
    echo "ERROR: Workspace appears to be \$HOME or /. This would backup too much."
    echo "Run this script from your agent workspace directory."
    exit 1
fi

cd /tmp
rm -f workspace.zip
zip -q -r workspace.zip "$WORKSPACE_DIR" -x@"$WORKSPACE_DIR/.backup-ignore" 2>/dev/null || \
    zip -q -r workspace.zip "$WORKSPACE_DIR"
npx @didcid/keymaster add-vault-item backup /tmp/workspace.zip
echo "✓ workspace.zip ($(du -h workspace.zip | cut -f1))"

# Backup config (excludes sessions, cache, logs per patterns)
echo "Backing up config..."
cd ~/.openclaw
rm -f /tmp/config.zip
zip -q -r /tmp/config.zip . \
  -x 'agents/*/sessions/*' \
  -x 'agents/*/cache/*' \
  -x 'logs/*' \
  -x '*.log' \
  -x 'browser/*' \
  -x 'media/*' \
  -x 'canvas/*'
npx @didcid/keymaster add-vault-item backup /tmp/config.zip
echo "✓ config.zip ($(du -h /tmp/config.zip | cut -f1))"

# Backup hexmem database if it exists
HEXMEM_PATH="$WORKSPACE_DIR/hexmem/hexmem.db"
if [ -f "$HEXMEM_PATH" ]; then
    echo "Backing up hexmem..."
    npx @didcid/keymaster add-vault-item backup "$HEXMEM_PATH"
    echo "✓ hexmem.db ($(du -h "$HEXMEM_PATH" | cut -f1))"
fi

# Verify
echo ""
echo "=== Vault Contents ==="
npx @didcid/keymaster list-vault-items backup | jq -r 'to_entries[] | "\(.key): \(.value.bytes / 1024 / 1024 | floor)MB (\(.value.added))"'

echo ""
echo "Backup complete."
