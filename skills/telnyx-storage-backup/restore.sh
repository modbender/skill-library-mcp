#!/bin/bash
#
# restore.sh - Restore OpenClaw workspace from Telnyx Storage
#
# Usage: ./restore.sh <backup_name> [bucket_name] [workspace_path]
#
# Examples:
#   ./restore.sh openclaw-backup-20260130-120000.tar.gz
#   ./restore.sh latest  # Restores most recent backup
#

set -e

BACKUP_NAME="${1:-}"
BUCKET="${2:-openclaw-backup}"
WORKSPACE="${3:-$HOME/clawd}"
TEMP_DIR="/tmp/openclaw-restore-$$"

echo "🔄 OpenClaw Restore ← Telnyx Storage"
echo "========================================"

# Check CLI is available
if ! command -v telnyx &> /dev/null; then
    echo "❌ Telnyx CLI not found. Install: npm install -g telnyx-cli"
    echo "   Then run: telnyx auth setup"
    exit 1
fi

# If no backup specified or "latest", find most recent
if [ -z "$BACKUP_NAME" ] || [ "$BACKUP_NAME" = "latest" ]; then
    echo "Finding latest backup in bucket: $BUCKET"
    # Extract just the filename (first column) from the listing
    BACKUP_NAME=$(telnyx storage object list "$BUCKET" 2>/dev/null | grep "openclaw-backup-" | awk '{print $1}' | sort | tail -1)
    if [ -z "$BACKUP_NAME" ]; then
        echo "❌ No backups found in bucket: $BUCKET"
        exit 1
    fi
    echo "Latest backup: $BACKUP_NAME"
fi

# Download
mkdir -p "$TEMP_DIR"
TEMP_ARCHIVE="$TEMP_DIR/$BACKUP_NAME"

echo "Downloading: telnyx://${BUCKET}/${BACKUP_NAME}"
telnyx storage object get "$BUCKET" "$BACKUP_NAME" -o "$TEMP_ARCHIVE"

# Confirm restore
echo ""
echo "⚠️  This will overwrite files in: $WORKSPACE"
read -p "Continue? [y/N] " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    rm -rf "$TEMP_DIR"
    exit 0
fi

# Extract
echo "Extracting to: $WORKSPACE"
mkdir -p "$WORKSPACE"
tar -xzf "$TEMP_ARCHIVE" -C "$WORKSPACE"

# Cleanup
rm -rf "$TEMP_DIR"

echo "✅ Restore complete from: $BACKUP_NAME"
