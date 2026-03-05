#!/bin/bash
# Save content to Obsidian vault via scp
# Usage: ./save-to-obsidian.sh <source_file> <vault_dir> [ssh_host] [filename_override]
# Set OBSIDIAN_HOST and OBSIDIAN_VAULT_PATH in TOOLS.md

set -euo pipefail

SOURCE="${1:?Usage: $0 <source_file> <vault_dir> [ssh_host] [filename_override]}"
VAULT_DIR="${2:?Usage: $0 <source_file> <vault_dir> [ssh_host] [filename_override]}"
SSH_HOST="${3:-${OBSIDIAN_HOST:-}}"
FILENAME="${4:-$(basename "$SOURCE")}"

if [[ -z "$SSH_HOST" ]]; then
    echo "Error: SSH host required (arg 3 or OBSIDIAN_HOST env var)"
    exit 1
fi

# Sanitize filename (no spaces, safe for iCloud)
SAFE_FILENAME=$(echo "$FILENAME" | tr ' ' '-' | tr -cd '[:alnum:]._-')
if [[ -z "$SAFE_FILENAME" ]]; then
    SAFE_FILENAME="obsidian-note-$(date +%Y%m%d-%H%M%S).md"
fi

DEST_PATH="${VAULT_DIR}/${SAFE_FILENAME}"

echo "Saving to Obsidian..."
echo "  Source: $SOURCE"
echo "  Dest:   ${SSH_HOST}:${DEST_PATH}"

if scp "$SOURCE" "${SSH_HOST}:${DEST_PATH}"; then
    echo "✅ Saved: $SAFE_FILENAME"
    echo "   iCloud sync will propagate within 1-2 minutes"
else
    echo "❌ scp failed. Check: SSH access to $SSH_HOST, vault path exists, disk space"
    exit 1
fi
