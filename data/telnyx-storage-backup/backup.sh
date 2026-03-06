#!/bin/bash
#
# backup.sh - Backup OpenClaw workspace to Telnyx Storage using CLI
#
# This replaces the Python boto3 approach with the simpler Telnyx CLI.
# Setup: telnyx auth setup (one-time)
#
# Usage: ./backup.sh [bucket_name] [workspace_path]
#
# Environment:
#   MAX_BACKUPS - Number of backups to keep (default: 48, ~24h of 30-min backups)
#

set -e

# Defaults
BUCKET="${1:-openclaw-backup}"
WORKSPACE="${2:-$HOME/clawd}"
MAX_BACKUPS="${MAX_BACKUPS:-48}"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ARCHIVE_NAME="openclaw-backup-${TIMESTAMP}.tar.gz"
TEMP_ARCHIVE="/tmp/${ARCHIVE_NAME}"

# Files to backup
FILES_TO_BACKUP=(
    "AGENTS.md"
    "SOUL.md"
    "USER.md"
    "IDENTITY.md"
    "TOOLS.md"
    "MEMORY.md"
    "HEARTBEAT.md"
    "GUARDRAILS.md"
    "INTEGRATIONS.md"
    "memory"
    "knowledge"
    "scripts"
)

echo "🔄 OpenClaw Backup → Telnyx Storage"
echo "========================================"

# Check CLI is available
if ! command -v telnyx &> /dev/null; then
    echo "❌ Telnyx CLI not found. Install: npm install -g telnyx-cli"
    echo "   Then run: telnyx auth setup"
    exit 1
fi

# Check workspace exists
if [ ! -d "$WORKSPACE" ]; then
    echo "❌ Workspace not found: $WORKSPACE"
    exit 1
fi

# Build list of existing files to archive
cd "$WORKSPACE"
EXISTING_FILES=()
echo "Creating archive: ${ARCHIVE_NAME}"
for f in "${FILES_TO_BACKUP[@]}"; do
    if [ -e "$f" ]; then
        echo "  + $f"
        EXISTING_FILES+=("$f")
    else
        echo "  - $f (not found, skipping)"
    fi
done

# Create archive
if [ ${#EXISTING_FILES[@]} -eq 0 ]; then
    echo "❌ No files to backup!"
    exit 1
fi

tar -czf "$TEMP_ARCHIVE" "${EXISTING_FILES[@]}"
SIZE=$(du -h "$TEMP_ARCHIVE" | cut -f1)
echo "Archive size: $SIZE"

# Ensure bucket exists (create if needed, ignore if already exists)
echo "Checking bucket: $BUCKET"
if ! telnyx storage bucket list 2>/dev/null | grep -qw "$BUCKET"; then
    echo "Creating bucket: $BUCKET"
    if ! telnyx storage bucket create "$BUCKET" 2>&1; then
        # Bucket might already exist (race condition or list didn't show it)
        # Verify we can access it
        if ! telnyx storage bucket list 2>/dev/null | grep -qw "$BUCKET"; then
            echo "❌ Failed to create or access bucket: $BUCKET"
            exit 1
        fi
        echo "Bucket already exists, continuing..."
    fi
else
    echo "Bucket exists: $BUCKET"
fi

# Upload
echo "Uploading to: telnyx://${BUCKET}/${ARCHIVE_NAME}"
telnyx storage object put "$BUCKET" "$TEMP_ARCHIVE" --key "$ARCHIVE_NAME"

# Cleanup temp file
rm -f "$TEMP_ARCHIVE"

echo "✅ Backup complete: telnyx://${BUCKET}/${ARCHIVE_NAME}"

# Prune old backups (keep MAX_BACKUPS most recent)
echo ""
echo "Checking for old backups to prune (keeping $MAX_BACKUPS)..."
BACKUP_LIST=$(telnyx storage object list "$BUCKET" 2>/dev/null | grep "openclaw-backup-" | awk '{print $1}' | sort)
BACKUP_COUNT=$(echo "$BACKUP_LIST" | grep -c "openclaw-backup-" || echo 0)

if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
    DELETE_COUNT=$((BACKUP_COUNT - MAX_BACKUPS))
    echo "  Found $BACKUP_COUNT backups, pruning $DELETE_COUNT old backup(s)..."
    
    # Get oldest backups to delete (sorted oldest first, take first N)
    TO_DELETE=$(echo "$BACKUP_LIST" | head -n "$DELETE_COUNT")
    
    for OLD_BACKUP in $TO_DELETE; do
        if telnyx storage object delete "$BUCKET" "$OLD_BACKUP" --force 2>/dev/null; then
            echo "  🗑️  Deleted: $OLD_BACKUP"
        fi
    done
    
    echo "  Cleanup complete."
else
    echo "  $BACKUP_COUNT backup(s) found, no pruning needed."
fi
