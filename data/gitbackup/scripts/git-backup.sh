#!/usr/bin/env bash
set -euo pipefail

WORKSPACE="/root/.openclaw/workspace"
BACKUP_DIR="/root/.openclaw/backups"
TS="$(date -u +"%Y%m%dT%H%M%SZ")"
BUNDLE_PATH="${BACKUP_DIR}/openclaw-git-${TS}.bundle"

if ! git -C "$WORKSPACE" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: $WORKSPACE is not a Git repository." >&2
  exit 1
fi

mkdir -p "$BACKUP_DIR"

git -C "$WORKSPACE" bundle create "$BUNDLE_PATH" --all

BYTES=$(wc -c < "$BUNDLE_PATH" | tr -d ' ')

echo "Created git bundle: $BUNDLE_PATH"
echo "Size: ${BYTES} bytes"
