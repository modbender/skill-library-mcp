#!/bin/bash
# Personality Backup — Reusable OpenClaw Skill
# Creates an AES-encrypted 7z archive of agent personality data
# Usage: bash backup.sh [config.json]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_FILE="${1:-$HOME/.openclaw/secrets/backup-config.json}"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "ERROR: Config file not found: $CONFIG_FILE"
  echo "Usage: $0 [/path/to/backup-config.json]"
  exit 1
fi

# Parse config with Python (portable JSON parsing)
eval "$(python3 "$SCRIPT_DIR/parse_config.py" "$CONFIG_FILE")"

BACKUP_DIR="/tmp/agent-backup-$$"
ARCHIVE_NAME="backup-$(date +%Y-%m-%d).7z"
ARCHIVE_PATH="/tmp/$ARCHIVE_NAME"

trap "rm -rf $BACKUP_DIR $ARCHIVE_PATH" EXIT

echo "$(date) — Starting personality backup..."

mkdir -p "$BACKUP_DIR"

# 1. Personality files
echo "Copying personality files..."
IFS=',' read -ra PFILES <<< "$CFG_PERSONALITY_FILES"
for f in "${PFILES[@]}"; do
  [ -f "$CFG_WORKSPACE/$f" ] && cp "$CFG_WORKSPACE/$f" "$BACKUP_DIR/"
done

# 2. Memory
if [ "$CFG_BACKUP_MEMORY" = "true" ] && [ -d "$CFG_WORKSPACE/memory" ]; then
  echo "Copying memory..."
  cp -r "$CFG_WORKSPACE/memory" "$BACKUP_DIR/memory"
fi

# 3. Secrets
if [ "$CFG_BACKUP_SECRETS" = "true" ] && [ -d "$CFG_SECRETS_DIR" ]; then
  echo "Copying secrets..."
  mkdir -p "$BACKUP_DIR/secrets"
  cp -r "$CFG_SECRETS_DIR"/* "$BACKUP_DIR/secrets/" 2>/dev/null || true
fi

# 4. Config
if [ "$CFG_BACKUP_CONFIG" = "true" ]; then
  echo "Copying config..."
  mkdir -p "$BACKUP_DIR/config"
  [ -f "$CFG_CONFIG_FILE" ] && cp "$CFG_CONFIG_FILE" "$BACKUP_DIR/config/"
fi

# 5. Projects
if [ "$CFG_BACKUP_PROJECTS" = "true" ] && [ -d "$CFG_WORKSPACE/projects" ]; then
  echo "Copying projects..."
  EXCLUDE_ARGS=""
  IFS=',' read -ra EXCLUDES <<< "$CFG_PROJECT_EXCLUDES"
  for ex in "${EXCLUDES[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude=$ex"
  done
  rsync -a $EXCLUDE_ARGS "$CFG_WORKSPACE/projects/" "$BACKUP_DIR/projects/" 2>/dev/null || true
  # Small images (under 500KB)
  find "$CFG_WORKSPACE/projects/" -maxdepth 3 \( -name '*.png' -o -name '*.jpg' \) -size -500k \
    -exec bash -c 'dest="'"$BACKUP_DIR"'/projects/${1#'"$CFG_WORKSPACE"'/projects/}"; mkdir -p "$(dirname "$dest")"; cp "$1" "$dest"' _ {} \; 2>/dev/null || true
fi

# 6. Scripts
if [ "$CFG_BACKUP_SCRIPTS" = "true" ] && [ -d "$CFG_WORKSPACE/scripts" ]; then
  echo "Copying scripts..."
  cp -r "$CFG_WORKSPACE/scripts" "$BACKUP_DIR/scripts-workspace" 2>/dev/null || true
fi

# 7. Other workspace .md files
for f in "$CFG_WORKSPACE"/*.md; do
  [ -f "$f" ] && cp "$f" "$BACKUP_DIR/" 2>/dev/null
done

# 8. Generate RESTORE.md
if [ "$CFG_GENERATE_RESTORE" = "true" ]; then
  echo "Generating RESTORE.md..."
  python3 "$SCRIPT_DIR/generate_restore.py" "$CONFIG_FILE" "$BACKUP_DIR/RESTORE.md"
fi

# 9. Create encrypted archive
echo "Creating encrypted 7z archive..."
7z a -t7z -mhe=on -p"$CFG_PASSWORD" "$ARCHIVE_PATH" "$BACKUP_DIR"/* > /dev/null
SIZE=$(du -sh "$ARCHIVE_PATH" | cut -f1)
echo "Archive size: $SIZE"

# 10. Deliver
if [ "$CFG_DELIVERY" = "email" ]; then
  echo "Sending via email..."
  CFG_ARCHIVE_PATH="$ARCHIVE_PATH" CFG_ARCHIVE_NAME="$ARCHIVE_NAME" CFG_SIZE="$SIZE" \
    python3 "$SCRIPT_DIR/deliver_email.py" "$CONFIG_FILE"
elif [ "$CFG_DELIVERY" = "local" ]; then
  mkdir -p "$CFG_LOCAL_DIR"
  cp "$ARCHIVE_PATH" "$CFG_LOCAL_DIR/"
  echo "Saved to: $CFG_LOCAL_DIR/$ARCHIVE_NAME"
fi

echo "$(date) — Backup complete! ($SIZE)"
