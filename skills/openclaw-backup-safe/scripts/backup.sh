#!/usr/bin/env bash
# OpenClaw Backup Script
# Usage: ./backup.sh [backup_dir]

set -euo pipefail

BACKUP_DIR="${1:-$HOME/openclaw-backups}"
DATE="$(date +%Y-%m-%d_%H%M)"
BACKUP_FILE="$BACKUP_DIR/openclaw-$DATE.tar.gz"

mkdir -p "$BACKUP_DIR"

if [ ! -d "$HOME/.openclaw" ]; then
  echo "Backup failed: $HOME/.openclaw not found"
  exit 1
fi

# Create backup (exclude completions cache and logs)
tar -czf "$BACKUP_FILE" \
  --exclude="completions" \
  --exclude="*.log" \
  -C "$HOME" .openclaw/

SIZE="$(du -h "$BACKUP_FILE" | cut -f1)"

# Rotate: keep only the last 7 backups
mapfile -t backups < <(
  ls -1t "$BACKUP_DIR"/openclaw-*.tar.gz 2>/dev/null || true
)

if [ "${#backups[@]}" -gt 7 ]; then
  for old in "${backups[@]:7}"; do
    rm -f -- "$old"
  done
fi

COUNT="$(ls -1 "$BACKUP_DIR"/openclaw-*.tar.gz 2>/dev/null | wc -l)"

echo "Backup created: $BACKUP_FILE ($SIZE)"
echo "Total backups: $COUNT"
