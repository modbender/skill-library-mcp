#!/bin/bash
# Safe Backup Script
# Backup state directory and workspace

set -e

# Configuration - customize these for your environment
# Detect OS and set temp directory (cross-platform: Linux/macOS/Windows)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "mingw"* || -n "$MSYSTEM" ]]; then
    # Windows (Git Bash / MSYS)
    TEMP_DIR="${TEMP:-${TMP:-/tmp}}"
elif [[ -n "$TMPDIR" ]]; then
    # macOS
    TEMP_DIR="$TMPDIR"
else
    # Linux
    TEMP_DIR="/tmp"
fi

TS=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="$TEMP_DIR/safe-backup-$TS"
STATE_DIR="${OPENCLAW_STATE_DIR:-$HOME/.openclaw}"
WORKSPACE_DIR="${OPENCLAW_WORKSPACE_DIR:-$HOME/.openclaw/workspace}"

# Sensitive files to exclude (add more as needed)
EXCLUDE_PATTERNS=(
    # Logs & Sessions
    "*.log"
    "*.log.*"
    "sessions.json"
    "logs/"
    
    # Credentials & Keys
    "*.key"
    "*.pem"
    ".env"
    ".env.*"
    "id_rsa*"
    "id_ed25519*"
    "*.secret"
    "*.token"
    "auth-profiles.json"
    "credentials.json"
    "api-keys.json"
    
    # Runtime generated (not needed for migration)
    "*.sock"
    "*.pid"
    "*.lock"
    "node_modules/"
    "dist/"
    ".cache/"
    "temp/"
    "tmp/"
    
    # OpenClaw runtime directories (not needed for migration)
    "sessions/"
    "browser/"
    "canvas/"
    "media/"
    "backups/"
    "delivery-queue/"
    "devices/"
    "subagents/"
    "completions/"
    
    # Backup files
    "*.bak"
    "*.save"
    "update-check.json"
)

echo "=== Safe Backup ==="
echo "Time: $(date)"
echo ""

# Check if source directories exist
if [ ! -d "$STATE_DIR" ]; then
    echo "Error: State directory not found: $STATE_DIR"
    exit 1
fi

# 1. Create temporary backup directory
echo "[1/4] Creating backup directory..."
mkdir -p "$BACKUP_DIR"

# 2. Copy state directory (exclude sensitive files)
echo "[2/4] Copying state directory..."

# Build rsync args array
RSYNC_ARGS=("-a" "--delete")
for pattern in "${EXCLUDE_PATTERNS[@]}"; do
    RSYNC_ARGS+=("--exclude=$pattern")
done

rsync "${RSYNC_ARGS[@]}" "$STATE_DIR/" "$BACKUP_DIR/state/"

# 3. Copy workspace (if exists) - use rsync with same exclusions
echo "[3/4] Copying workspace..."
if [ -d "$WORKSPACE_DIR" ]; then
    # Use rsync with same exclusion patterns as state directory
    rsync "${RSYNC_ARGS[@]}" "$WORKSPACE_DIR/" "$BACKUP_DIR/workspace/"
else
    echo "Warning: Workspace directory not found: $WORKSPACE_DIR"
fi

# 4. Package
echo "[4/4] Packaging backup..."
cd "$TEMP_DIR"
tar -czf "safe-backup-$TS.tar.gz" "safe-backup-$TS"

# Cleanup temp directory
rm -rf "$BACKUP_DIR"

BACKUP_FILE="safe-backup-$TS.tar.gz"

echo ""
echo "=== Backup Complete ==="
echo "Backup file: $TEMP_DIR/$BACKUP_FILE"
echo ""
echo "⚠️  Security Notes:"
echo "1. This backup may contain sensitive files - review before sharing"
echo "2. If uploading to GitHub, use a private repo and consider encryption"
echo "3. Excluded files: ${EXCLUDE_PATTERNS[*]}"
echo ""
echo "Next steps (manual):"
echo "1. Create a private GitHub repository (recommended)"
echo "2. git clone repository locally"
echo "3. Extract: tar -xzf $TEMP_DIR/$BACKUP_FILE"
echo "4. Commit and push: cd <backup-dir> && git add . && git commit -m 'Backup $TS' && git push"
echo ""
echo "⚠️  Remember to delete unencrypted backup from $TEMP_DIR!"
