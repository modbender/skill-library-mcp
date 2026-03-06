#!/bin/bash
# =============================================================================
# restore.sh — Restore OpenClaw from backup tarball
# =============================================================================
# Usage: bash restore.sh <backup-file.tar.gz>
# =============================================================================

set -euo pipefail

BACKUP_FILE="${1:-}"
OPENCLAW_DIR="$HOME/.openclaw"
WORKSPACE="$OPENCLAW_DIR/workspace"

if [ -z "$BACKUP_FILE" ] || [ ! -f "$BACKUP_FILE" ]; then
    echo "Usage: bash restore.sh <backup-file.tar.gz>"
    echo "  Restores workspace, config, secrets, and cron jobs from backup"
    exit 1
fi

echo "=== OpenClaw Restore ==="
echo "Backup: $BACKUP_FILE"
echo

# Extract to temp directory
TEMP_DIR=$(mktemp -d)
tar xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Find the backup root (may be nested)
BACKUP_ROOT=$(find "$TEMP_DIR" -maxdepth 2 -name "SOUL.md" -printf '%h\n' | head -1)
if [ -z "$BACKUP_ROOT" ]; then
    BACKUP_ROOT="$TEMP_DIR"
fi

echo "Extracted to: $BACKUP_ROOT"

# --- Workspace files ---------------------------------------------------------
echo "Restoring workspace files..."
mkdir -p "$WORKSPACE" "$WORKSPACE/memory" "$WORKSPACE/scripts"

for f in SOUL.md USER.md AGENTS.md IDENTITY.md TOOLS.md HEARTBEAT.md MEMORY.md BOOT.md; do
    [ -f "$BACKUP_ROOT/$f" ] && cp "$BACKUP_ROOT/$f" "$WORKSPACE/$f" && echo "  ✓ $f"
done

# Memory files
if [ -d "$BACKUP_ROOT/memory" ]; then
    cp -r "$BACKUP_ROOT/memory/"* "$WORKSPACE/memory/" 2>/dev/null || true
    echo "  ✓ memory/ ($(ls "$WORKSPACE/memory/" | wc -l) files)"
fi

# Scripts
if [ -d "$BACKUP_ROOT/scripts" ]; then
    cp -r "$BACKUP_ROOT/scripts/"* "$WORKSPACE/scripts/" 2>/dev/null || true
    chmod +x "$WORKSPACE/scripts/"*.sh 2>/dev/null || true
    echo "  ✓ scripts/ ($(ls "$WORKSPACE/scripts/"*.sh 2>/dev/null | wc -l) scripts)"
fi

# --- OpenClaw config ---------------------------------------------------------
echo "Restoring config..."
if [ -f "$BACKUP_ROOT/openclaw.json" ]; then
    cp "$BACKUP_ROOT/openclaw.json" "$OPENCLAW_DIR/openclaw.json"
    echo "  ✓ openclaw.json"
fi

if [ -f "$BACKUP_ROOT/dot-env" ]; then
    cp "$BACKUP_ROOT/dot-env" "$OPENCLAW_DIR/.env"
    echo "  ✓ .env"
fi

# --- Cron database -----------------------------------------------------------
if [ -d "$BACKUP_ROOT/cron-db" ]; then
    echo "Restoring cron database..."
    for crondir in "$OPENCLAW_DIR/cron" "$OPENCLAW_DIR/data/cron"; do
        mkdir -p "$crondir"
        cp -r "$BACKUP_ROOT/cron-db/"* "$crondir/" 2>/dev/null && break
    done
    echo "  ✓ cron jobs restored"
fi

# --- GPG keys + password store -----------------------------------------------
if [ -d "$BACKUP_ROOT/gnupg" ]; then
    echo "Restoring GPG keys..."
    mkdir -p "$HOME/.gnupg"
    chmod 700 "$HOME/.gnupg"
    cp -r "$BACKUP_ROOT/gnupg/"* "$HOME/.gnupg/" 2>/dev/null || true
    chmod 600 "$HOME/.gnupg/"* 2>/dev/null || true
    echo "  ✓ GPG keys"
fi

if [ -d "$BACKUP_ROOT/password-store" ]; then
    echo "Restoring password store..."
    cp -r "$BACKUP_ROOT/password-store" "$HOME/.password-store" 2>/dev/null || true
    echo "  ✓ password store ($(pass ls 2>/dev/null | grep -c '├\|└' || echo '?') secrets)"
fi

# --- OAuth credentials -------------------------------------------------------
if [ -d "$BACKUP_ROOT/gog-config" ]; then
    echo "Restoring GOG credentials..."
    mkdir -p "$HOME/.config/gog"
    cp -r "$BACKUP_ROOT/gog-config/"* "$HOME/.config/gog/" 2>/dev/null || true
    echo "  ✓ GOG config"
fi

if [ -d "$BACKUP_ROOT/keyrings" ]; then
    mkdir -p "$HOME/.local/share/keyrings"
    cp -r "$BACKUP_ROOT/keyrings/"* "$HOME/.local/share/keyrings/" 2>/dev/null || true
    echo "  ✓ keyrings"
fi

if [ -f "$BACKUP_ROOT/rclone.conf" ]; then
    mkdir -p "$HOME/.config/rclone"
    cp "$BACKUP_ROOT/rclone.conf" "$HOME/.config/rclone/rclone.conf"
    echo "  ✓ rclone config"
fi

# --- Cleanup -----------------------------------------------------------------
rm -rf "$TEMP_DIR"

echo
echo "=== Restore Complete ==="
echo "Next: run 'bash verify.sh' to confirm everything works"
echo "Then: 'openclaw gateway restart' to apply config"
