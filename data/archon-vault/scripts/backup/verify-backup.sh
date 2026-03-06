#!/bin/bash
# Verify backup integrity by retrieving and testing vault items
# Run periodically to ensure backups are actually recoverable

set -e

# Load environment
if [ -f ~/.archon.env ]; then
    source ~/.archon.env
    export ARCHON_PASSPHRASE
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

echo "=== Backup Verification $(date) ==="
echo ""

# Create temp directory for test downloads
VERIFY_DIR="/tmp/backup-verify-$$"
mkdir -p "$VERIFY_DIR"
cd "$VERIFY_DIR"

ERRORS=0

# Function to verify a backup item
verify_item() {
    local item_name="$1"
    local test_command="$2"
    
    echo "Verifying $item_name..."
    
    # Try to retrieve from vault
    if ! npx @didcid/keymaster get-vault-item backup "$item_name" "$VERIFY_DIR/$item_name" 2>&1; then
        echo "  ✗ FAILED: Could not retrieve $item_name from vault"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
    
    # Check file exists and has size
    if [ ! -f "$VERIFY_DIR/$item_name" ]; then
        echo "  ✗ FAILED: $item_name not found after retrieval"
        ERRORS=$((ERRORS + 1))
        return 1
    fi
    
    local size=$(du -h "$VERIFY_DIR/$item_name" | cut -f1)
    echo "  Retrieved: $size"
    
    # Run test command if provided
    if [ -n "$test_command" ]; then
        if eval "$test_command" > /dev/null 2>&1; then
            echo "  ✓ Integrity check passed"
        else
            echo "  ✗ FAILED: Integrity check failed"
            ERRORS=$((ERRORS + 1))
            return 1
        fi
    else
        echo "  ✓ Retrieved successfully"
    fi
    
    return 0
}

# Verify workspace backup
verify_item "workspace.zip" "unzip -t '$VERIFY_DIR/workspace.zip'"

echo ""

# Verify config backup
verify_item "config.zip" "unzip -t '$VERIFY_DIR/config.zip'"

echo ""

# Verify hexmem database
verify_item "hexmem.db" "sqlite3 '$VERIFY_DIR/hexmem.db' 'SELECT COUNT(*) FROM memory_log;'"

echo ""
echo "=== Verification Summary ==="

if [ $ERRORS -eq 0 ]; then
    echo "✓ All backups verified successfully"
    echo ""
    echo "Your backups are recoverable. You can restore from:"
    echo "  - workspace.zip ($VERIFY_DIR/workspace.zip)"
    echo "  - config.zip ($VERIFY_DIR/config.zip)"
    echo "  - hexmem.db ($VERIFY_DIR/hexmem.db)"
else
    echo "✗ $ERRORS backup(s) failed verification"
    echo ""
    echo "ACTION REQUIRED: Re-run backup-to-vault.sh to fix failed backups"
fi

echo ""
echo "Cleanup: rm -rf $VERIFY_DIR"
