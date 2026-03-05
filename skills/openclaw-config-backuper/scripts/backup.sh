#!/bin/bash
set -e

BACKUP_DIR=~/.openclaw/workspace/backup/$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"/{config,skills,memory,workspace}

# Backup JSON configs
cp ~/.openclaw/openclaw.json "$BACKUP_DIR/config/" 2>/dev/null || true
cp ~/.openclaw/exec-approvals.json "$BACKUP_DIR/config/" 2>/dev/null || true
cp ~/.openclaw/update-check.json "$BACKUP_DIR/config/" 2>/dev/null || true

# Backup Skills
if [ -d ~/.openclaw/skills ] && [ "$(ls -A ~/.openclaw/skills 2>/dev/null)" ]; then
  cp -r ~/.openclaw/skills/* "$BACKUP_DIR/skills/" 2>/dev/null || true
fi

# Backup workspace MD files
cp ~/.openclaw/workspace/*.md "$BACKUP_DIR/workspace/" 2>/dev/null || true

# Backup memory
if [ -d ~/.openclaw/workspace/memory ]; then
  cp ~/.openclaw/workspace/memory/*.md "$BACKUP_DIR/memory/" 2>/dev/null || true
fi

# Report
FILE_COUNT=$(find "$BACKUP_DIR" -type f | wc -l)
echo "✅ Backup completed: $BACKUP_DIR"
echo "📦 Total files: $FILE_COUNT"
