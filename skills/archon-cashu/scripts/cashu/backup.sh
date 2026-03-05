#!/bin/bash
# Archon Cashu Wallet — Backup to Archon Vault
# Encrypts cashu wallet proofs and backs up to an Archon vault
#
# Usage: backup.sh [--auto] [--restore] [--list]
#   --auto     Non-interactive, suitable for cron
#   --restore  Restore latest backup from vault
#   --list     List available backups in vault
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/config.sh" > /dev/null 2>&1

# Backup config
CASHU_WALLET_DIR="${CASHU_WALLET_DIR:-$HOME/.cashu}"
VAULT_NAME="${CASHU_VAULT_NAME:-cashu-wallet-vault}"
BACKUP_DIR="/tmp/cashu-backup-$$"

# Get or create vault DID
get_vault_did() {
    local VAULT_DID="${CASHU_VAULT_DID:-}"
    
    if [ -z "$VAULT_DID" ]; then
        # Check if vault exists by name in aliases
        VAULT_DID=$(npx --yes @didcid/keymaster resolve-alias "$VAULT_NAME" 2>/dev/null || true)
    fi
    
    if [ -z "$VAULT_DID" ]; then
        echo "Creating vault '$VAULT_NAME'..." >&2
        # Create vault via keymaster API
        VAULT_RESULT=$(curl -s -X POST "http://localhost:4226/api/v1/vaults" \
            -H "Content-Type: application/json" -d '{}')
        VAULT_DID=$(echo "$VAULT_RESULT" | jq -r '.did // empty')
        
        if [ -z "$VAULT_DID" ]; then
            echo "Error: Failed to create vault" >&2
            echo "$VAULT_RESULT" >&2
            exit 1
        fi
        
        # Save vault DID to config
        echo "" >> "$CONFIG_FILE"
        echo "# Cashu wallet backup vault" >> "$CONFIG_FILE"
        echo "CASHU_VAULT_DID=\"$VAULT_DID\"" >> "$CONFIG_FILE"
        echo "CASHU_VAULT_NAME=\"$VAULT_NAME\"" >> "$CONFIG_FILE"
        echo "Created vault: $VAULT_DID" >&2
    fi
    
    echo "$VAULT_DID"
}

do_backup() {
    local AUTO="${1:-false}"
    local TIMESTAMP=$(date +%Y%m%d%H%M%S)
    local VAULT_DID=$(get_vault_did)
    
    mkdir -p "$BACKUP_DIR"
    
    echo "📦 Backing up cashu wallet..."
    echo "   Wallet dir: $CASHU_WALLET_DIR"
    echo "   Vault: $VAULT_DID"
    
    # Step 1: Export wallet data
    # Copy wallet database
    if [ -d "$CASHU_WALLET_DIR" ]; then
        cp -r "$CASHU_WALLET_DIR" "$BACKUP_DIR/cashu-wallet"
    else
        echo "⚠️  No wallet directory at $CASHU_WALLET_DIR"
        rm -rf "$BACKUP_DIR"
        exit 1
    fi
    
    # Step 2: Record balance for verification
    BALANCE=$($CASHU_BIN balance 2>&1 || echo "unknown")
    echo "$BALANCE" > "$BACKUP_DIR/balance.txt"
    
    # Step 3: Record metadata
    cat > "$BACKUP_DIR/metadata.json" << EOF
{
    "timestamp": "$TIMESTAMP",
    "date": "$(date -Iseconds)",
    "balance": "$BALANCE",
    "mint": "$CASHU_MINT_URL",
    "wallet_dir": "$CASHU_WALLET_DIR",
    "hostname": "$(hostname)",
    "sha256": "$(find "$BACKUP_DIR/cashu-wallet" -type f -exec sha256sum {} \; | sha256sum | cut -d' ' -f1)"
}
EOF
    
    # Step 4: Create tarball
    TARBALL="/tmp/cashu-backup-${TIMESTAMP}.tar.gz"
    tar -czf "$TARBALL" -C "$BACKUP_DIR" .
    
    # Step 5: Upload to IPFS and store CID in vault
    echo "🔐 Uploading encrypted backup to IPFS..."
    
    # Add to IPFS
    IPFS_RESULT=$(curl -s -X POST "http://localhost:5001/api/v0/add" \
        -F "file=@${TARBALL}" 2>/dev/null)
    IPFS_CID=$(echo "$IPFS_RESULT" | jq -r '.Hash // empty')
    
    if [ -z "$IPFS_CID" ]; then
        echo "⚠️  IPFS upload failed. Backup saved locally at: $TARBALL"
        rm -rf "$BACKUP_DIR"
        return
    fi
    
    echo "📌 IPFS CID: $IPFS_CID"
    
    # Store backup reference in vault via keymaster API
    STORE_RESULT=$(curl -s -X POST "http://localhost:4226/api/v1/vaults/$VAULT_DID" \
        -H "Content-Type: application/json" \
        -d "{\"key\": \"cashu-backup-${TIMESTAMP}\", \"value\": {\"cid\": \"$IPFS_CID\", \"timestamp\": \"$TIMESTAMP\", \"balance\": \"$BALANCE\", \"sha256\": \"$(sha256sum "$TARBALL" | cut -d' ' -f1)\"}}" 2>/dev/null)
    
    if echo "$STORE_RESULT" | jq -e '.error' > /dev/null 2>&1; then
        echo "⚠️  Vault store failed: $(echo "$STORE_RESULT" | jq -r '.error')"
        echo "   Backup still available on IPFS: $IPFS_CID"
    else
        echo "✅ Stored in vault"
    fi
    
    # Clean up local tarball
    rm -f "$TARBALL"
    
    # Cleanup
    rm -rf "$BACKUP_DIR"
    
    echo ""
    echo "✅ Backup complete: cashu-backup-${TIMESTAMP}"
    echo "   Balance at backup: $BALANCE"
}

do_restore() {
    local VAULT_DID=$(get_vault_did)
    
    echo "🔄 Restoring cashu wallet from vault..."
    echo "   Vault: $VAULT_DID"
    
    RESTORE_SCRIPT="$SCRIPT_DIR/../backup/verify-backup.sh"
    if [ -x "$RESTORE_SCRIPT" ]; then
        echo "Checking vault for latest backup..."
        "$RESTORE_SCRIPT" "$VAULT_DID" 2>&1
    else
        echo "⚠️  Manual restore required."
        echo "1. Download encrypted backup from vault"
        echo "2. Decrypt: ../crypto/decrypt-file.sh <backup.enc> <backup.tar.gz>"
        echo "3. Extract: tar -xzf backup.tar.gz -C $CASHU_WALLET_DIR"
    fi
}

do_list() {
    local VAULT_DID=$(get_vault_did)
    echo "📋 Cashu wallet backups in vault: $VAULT_DID"
    
    # List vault contents
    LIST_SCRIPT="$SCRIPT_DIR/../backup/verify-backup.sh"
    if [ -x "$LIST_SCRIPT" ]; then
        "$LIST_SCRIPT" "$VAULT_DID" 2>&1
    else
        echo "Use the Archon explorer or CLI to list vault contents."
    fi
}

# Main
case "${1:-}" in
    --auto)
        do_backup true
        ;;
    --restore)
        do_restore
        ;;
    --list)
        do_list
        ;;
    *)
        do_backup false
        ;;
esac
