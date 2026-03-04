#!/usr/bin/env bash
# backup.sh — Create local backups of ~/.openclaw/
# Always produces two files:
#   1. Full backup (encrypted) — everything, for disaster recovery on same/similar environment
#   2. Workspace-only backup — just the workspace (memory, skills, files), safe for any environment
# Part of the OpenClaw backup skill.
set -euo pipefail

# ---------------------------------------------------------------------------
# Paths & defaults
# ---------------------------------------------------------------------------
OPENCLAW_DIR="$HOME/.openclaw"
SKILL_DIR="$OPENCLAW_DIR/workspace/skills/backup"
CONFIG_FILE="$SKILL_DIR/config.json"
CRED_DIR="$OPENCLAW_DIR/credentials/backup"
DEFAULT_BACKUP_DIR="$HOME/backups/openclaw"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log()  { echo "[backup] $(date '+%H:%M:%S') $*"; }
die()  { echo "[backup] ERROR: $*" >&2; exit 1; }

read_config() {
  local key="$1"
  if [[ -f "$CONFIG_FILE" ]] && command -v jq &>/dev/null; then
    jq -r ".$key // empty" "$CONFIG_FILE" 2>/dev/null || true
  fi
}

# ---------------------------------------------------------------------------
# Configuration (config.json → env var → default)
# ---------------------------------------------------------------------------
ENCRYPT="${BACKUP_ENCRYPT:-$(read_config encrypt)}"
ENCRYPT="${ENCRYPT:-true}"

RETAIN_DAYS="${BACKUP_RETAIN_DAYS:-$(read_config retainDays)}"
RETAIN_DAYS="${RETAIN_DAYS:-30}"

STOP_GATEWAY="${BACKUP_STOP_GATEWAY:-true}"

BACKUP_DIR="${BACKUP_DIR:-$DEFAULT_BACKUP_DIR}"

# Passphrase: env var → file
PASSPHRASE="${BACKUP_PASSPHRASE:-}"
if [[ -z "$PASSPHRASE" && -f "$CRED_DIR/backup-passphrase" ]]; then
  PASSPHRASE="$(cat "$CRED_DIR/backup-passphrase")"
fi

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------
[[ -d "$OPENCLAW_DIR" ]] || die "OpenClaw directory not found at $OPENCLAW_DIR"

if [[ "$ENCRYPT" == "true" && -z "$PASSPHRASE" ]]; then
  die "Encryption enabled but no passphrase found. Set BACKUP_PASSPHRASE or create $CRED_DIR/backup-passphrase"
fi

if ! command -v jq &>/dev/null; then
  log "WARNING: jq not installed — config.json will not be read. Install with: sudo apt install jq"
fi

# ---------------------------------------------------------------------------
# Prepare
# ---------------------------------------------------------------------------
mkdir -p "$BACKUP_DIR"

TIMESTAMP="$(date '+%Y%m%d-%H%M')"
HOSTNAME_SHORT="$(hostname -s 2>/dev/null || echo unknown)"

# ---------------------------------------------------------------------------
# Stop gateway for consistency
# ---------------------------------------------------------------------------
GATEWAY_WAS_RUNNING=false
if [[ "$STOP_GATEWAY" == "true" ]]; then
  if command -v openclaw &>/dev/null && openclaw gateway status 2>/dev/null | grep -qi "running"; then
    log "Stopping gateway for consistent backup..."
    openclaw gateway stop 2>/dev/null || true
    GATEWAY_WAS_RUNNING=true
  fi
fi

cleanup() {
  if [[ "$GATEWAY_WAS_RUNNING" == "true" ]]; then
    log "Restarting gateway..."
    openclaw gateway start 2>/dev/null || log "WARNING: Failed to restart gateway. Run: openclaw gateway start"
  fi
}
trap cleanup EXIT

# ---------------------------------------------------------------------------
# 1. Full backup (encrypted)
# ---------------------------------------------------------------------------
FULL_NAME="openclaw-${HOSTNAME_SHORT}-${TIMESTAMP}-full.tar.gz"
FULL_PATH="$BACKUP_DIR/$FULL_NAME"

log "Creating full backup..."
tar czf "$FULL_PATH" -C "$HOME" .openclaw/
log "Full archive: $FULL_PATH ($(du -h "$FULL_PATH" | cut -f1))"

if [[ "$ENCRYPT" == "true" ]]; then
  log "Encrypting full backup with AES-256..."
  gpg --batch --yes --symmetric --cipher-algo AES256 \
    --passphrase "$PASSPHRASE" \
    --output "${FULL_PATH}.gpg" \
    "$FULL_PATH"
  rm -f "$FULL_PATH"
  FULL_PATH="${FULL_PATH}.gpg"
  log "Encrypted: $FULL_PATH ($(du -h "$FULL_PATH" | cut -f1))"
else
  log "WARNING: Full backup is NOT encrypted — contains credentials in plaintext"
fi

# ---------------------------------------------------------------------------
# 2. Workspace-only backup (safe for any environment)
# ---------------------------------------------------------------------------
WS_NAME="openclaw-${HOSTNAME_SHORT}-${TIMESTAMP}-workspace.tar.gz"
WS_PATH="$BACKUP_DIR/$WS_NAME"

log "Creating workspace-only backup..."
tar czf "$WS_PATH" -C "$HOME" .openclaw/workspace/
log "Workspace archive: $WS_PATH ($(du -h "$WS_PATH" | cut -f1))"

if [[ "$ENCRYPT" == "true" ]]; then
  log "Encrypting workspace backup..."
  gpg --batch --yes --symmetric --cipher-algo AES256 \
    --passphrase "$PASSPHRASE" \
    --output "${WS_PATH}.gpg" \
    "$WS_PATH"
  rm -f "$WS_PATH"
  WS_PATH="${WS_PATH}.gpg"
  log "Encrypted: $WS_PATH ($(du -h "$WS_PATH" | cut -f1))"
fi

# ---------------------------------------------------------------------------
# Prune old backups
# ---------------------------------------------------------------------------
if [[ "$RETAIN_DAYS" -gt 0 ]]; then
  PRUNED=$(find "$BACKUP_DIR" -name 'openclaw-*.tar.gz*' -mtime +"$RETAIN_DAYS" -print -delete 2>/dev/null | wc -l)
  if [[ "$PRUNED" -gt 0 ]]; then
    log "Pruned $PRUNED backup(s) older than $RETAIN_DAYS days"
  fi
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
log "Backup complete:"
log "  Full:      $FULL_PATH"
log "  Workspace: $WS_PATH"

# Output the full backup path (used by upload.sh)
echo "$FULL_PATH"
