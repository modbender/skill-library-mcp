#!/usr/bin/env bash
set -euo pipefail

BACKUP_SCRIPT="/root/.openclaw/workspace/scripts/backup-local.sh"

if [ ! -x "$BACKUP_SCRIPT" ]; then
  echo "Error: backup script not found or not executable: $BACKUP_SCRIPT" >&2
  exit 1
fi

"$BACKUP_SCRIPT"
