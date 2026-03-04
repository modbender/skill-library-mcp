#!/bin/bash

# --- HolySpiritOS Uninstaller ---
# This script removes the moral engine foundation and restores the original soul.md

echo "🕊️ Beginning HolySpiritOS removal..."

# 1. Define Paths
FOUNDATION_DIR="$HOME/.openclaw/foundation"
SOUL_FILE="$HOME/.openclaw/soul.md"
BACKUP_SOUL="$HOME/.openclaw/soul.md.bak"

# 2. Remove Foundation Files
if [ -d "$FOUNDATION_DIR" ]; then
    echo "Removing foundation files..."
    rm -rf "$FOUNDATION_DIR"
else
    echo "No foundation directory found."
fi

# 3. Restore soul.md from Backup
if [ -f "$BACKUP_SOUL" ]; then
    echo "Restoring original soul.md from backup..."
    mv "$BACKUP_SOUL" "$SOUL_FILE"
    echo "✅ soul.md restored successfully."
else
    echo "⚠️ No backup file found. You may need to manually edit $SOUL_FILE to remove the moral engine lines."
fi

echo "🕊️ HolySpiritOS has been uninstalled. Please restart your OpenClaw agent."
