#!/usr/bin/env bash
# restore.sh — Restore OpenClaw from a backup file.
# Use a *-full.tar.gz(.gpg) file for full disaster recovery (same environment).
# Use a *-workspace.tar.gz file to restore just the agent workspace (any environment).
# Part of the OpenClaw backup skill.
set -euo pipefail

# ---------------------------------------------------------------------------
# Paths & defaults
# ---------------------------------------------------------------------------
OPENCLAW_DIR="$HOME/.openclaw"
CRED_DIR="$OPENCLAW_DIR/credentials/backup"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
log()  { echo "[restore] $(date '+%H:%M:%S') $*"; }
die()  { echo "[restore] ERROR: $*" >&2; exit 1; }

safe_load_creds() {
  # Safely read KEY=VALUE pairs from a credential file without executing arbitrary shell
  local file="$1"
  [[ -f "$file" ]] || return 1
  while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]] && continue
    # Strip 'export ' prefix if present
    key="${key#export }"
    # Trim whitespace
    key="$(echo "$key" | xargs)"
    # Strip surrounding quotes from value
    value="${value#\"}"
    value="${value%\"}"
    value="${value#\'}"
    value="${value%\'}"
    export "$key=$value"
  done < "$file"
}

# ---------------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------------
WORKSPACE_ONLY=false
SOURCE=""

for arg in "$@"; do
  case "$arg" in
    --workspace-only) WORKSPACE_ONLY=true ;;
    -*) die "Unknown option: $arg" ;;
    *) SOURCE="$arg" ;;
  esac
done

if [[ -z "$SOURCE" ]]; then
  echo "Usage: restore.sh [--workspace-only] <backup-file-or-cloud-url>"
  echo ""
  echo "Backup types:"
  echo "  *-full.tar.gz.gpg     Full restore (config, credentials, workspace, sessions)"
  echo "  *-workspace.tar.gz    Workspace only (memory, skills, files — safe for any environment)"
  echo ""
  echo "Options:"
  echo "  --workspace-only      Only extract the workspace from a full backup"
  echo ""
  echo "Examples:"
  echo "  restore.sh openclaw-myhost-20260215-full.tar.gz.gpg"
  echo "  restore.sh openclaw-myhost-20260215-workspace.tar.gz"
  echo "  restore.sh --workspace-only openclaw-myhost-20260215-full.tar.gz.gpg"
  echo "  restore.sh s3://mybucket/openclaw/openclaw-myhost-20260215-full.tar.gz.gpg"
  exit 1
fi

# Auto-detect workspace backup by filename
if [[ "$SOURCE" == *-workspace.tar.gz* ]]; then
  WORKSPACE_ONLY=true
fi

WORK_DIR="$(mktemp -d)"
trap 'rm -rf "$WORK_DIR"' EXIT

# ---------------------------------------------------------------------------
# Download if remote
# ---------------------------------------------------------------------------
if [[ "$SOURCE" == s3://* ]]; then
  log "Downloading from S3..."
  LOCAL_FILE="$WORK_DIR/$(basename "$SOURCE")"
  if [[ -f "$CRED_DIR/aws-credentials" ]]; then
    safe_load_creds "$CRED_DIR/aws-credentials"
  fi
  aws s3 cp "$SOURCE" "$LOCAL_FILE"

elif [[ "$SOURCE" == gs://* ]]; then
  log "Downloading from GCS..."
  LOCAL_FILE="$WORK_DIR/$(basename "$SOURCE")"
  if [[ -f "$CRED_DIR/gcs-key.json" ]]; then
    gcloud auth activate-service-account --key-file="$CRED_DIR/gcs-key.json" 2>/dev/null || true
  fi
  gsutil cp "$SOURCE" "$LOCAL_FILE"

elif [[ -f "$SOURCE" ]]; then
  LOCAL_FILE="$SOURCE"

else
  die "Source not found or unsupported: $SOURCE"
fi

log "Restoring from: $LOCAL_FILE"
if [[ "$WORKSPACE_ONLY" == "true" ]]; then
  log "Mode: workspace-only (memory, skills, files)"
else
  log "Mode: full restore (config, credentials, workspace, sessions)"
fi

# ---------------------------------------------------------------------------
# Decrypt if needed
# ---------------------------------------------------------------------------
ARCHIVE="$LOCAL_FILE"
if [[ "$ARCHIVE" == *.gpg ]]; then
  log "Decrypting..."

  PASSPHRASE="${BACKUP_PASSPHRASE:-}"
  if [[ -z "$PASSPHRASE" && -f "$CRED_DIR/backup-passphrase" ]]; then
    PASSPHRASE="$(cat "$CRED_DIR/backup-passphrase")"
  fi
  [[ -n "$PASSPHRASE" ]] || die "Encrypted backup but no passphrase. Set BACKUP_PASSPHRASE or create $CRED_DIR/backup-passphrase"

  DECRYPTED="$WORK_DIR/$(basename "${ARCHIVE%.gpg}")"
  gpg --batch --yes --decrypt \
    --passphrase "$PASSPHRASE" \
    --output "$DECRYPTED" \
    "$ARCHIVE"

  ARCHIVE="$DECRYPTED"
  log "Decrypted successfully"
fi

# ---------------------------------------------------------------------------
# Stop gateway
# ---------------------------------------------------------------------------
if command -v openclaw &>/dev/null; then
  if openclaw gateway status 2>/dev/null | grep -qi "running"; then
    log "Stopping gateway..."
    openclaw gateway stop 2>/dev/null || true
  fi
fi

# ---------------------------------------------------------------------------
# Restore
# ---------------------------------------------------------------------------
if [[ "$WORKSPACE_ONLY" == "true" ]]; then
  # Workspace-only: only replace the workspace directory
  WORKSPACE_DIR="$OPENCLAW_DIR/workspace"

  if [[ -d "$WORKSPACE_DIR" ]]; then
    SAFETY="${WORKSPACE_DIR}.pre-restore"
    [[ -d "$SAFETY" ]] && rm -rf "$SAFETY"
    log "Moving existing workspace → ${SAFETY}/"
    mv "$WORKSPACE_DIR" "$SAFETY"
  fi

  log "Extracting workspace..."
  # Handle both archive types:
  # - workspace archive: contains .openclaw/workspace/
  # - full archive with --workspace-only: contains .openclaw/ (extract only workspace subdir)
  if tar -tzf "$ARCHIVE" 2>/dev/null | head -1 | grep -q "^\.openclaw/workspace/"; then
    # Workspace-only archive or full archive — extract just the workspace path
    tar xzf "$ARCHIVE" -C "$HOME" .openclaw/workspace/
  else
    die "Could not find workspace directory in archive"
  fi

  log "Workspace restored to $WORKSPACE_DIR"
else
  # Full restore: replace entire ~/.openclaw/
  if [[ -d "$OPENCLAW_DIR" ]]; then
    SAFETY="$HOME/.openclaw.pre-restore"
    [[ -d "$SAFETY" ]] && rm -rf "$SAFETY"
    log "Moving existing ~/.openclaw/ → ~/.openclaw.pre-restore/"
    mv "$OPENCLAW_DIR" "$SAFETY"
  fi

  log "Extracting full backup..."
  tar xzf "$ARCHIVE" -C "$HOME"
  log "Full restore complete"
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
if [[ "$WORKSPACE_ONLY" == "true" ]]; then
  log "Workspace restored! Your gateway config and credentials are untouched."
  echo ""
  echo "Next steps:"
  echo "  1. Start the gateway:  openclaw gateway start"
  echo "  2. Your agent's memory, skills, and files are restored"
  echo "  3. Previous workspace saved at: ${WORKSPACE_DIR}.pre-restore/"
else
  log "Full restore complete!"
  echo ""
  echo "Your previous state is saved at ~/.openclaw.pre-restore/"
  echo ""
  echo "Next steps:"
  echo "  1. Review the restored files at ~/.openclaw/"
  echo "  2. Start the gateway:  openclaw gateway start"
  echo "  3. If everything works, remove the safety copy:"
  echo "     rm -rf ~/.openclaw.pre-restore/"
fi
