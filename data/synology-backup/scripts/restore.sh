#!/bin/bash
# Synology Backup — Restore from snapshot
set -euo pipefail

CONFIG="${SYNOLOGY_BACKUP_CONFIG:-$HOME/.openclaw/synology-backup.json}"

if [[ ! -f "$CONFIG" ]]; then
    echo "Error: Config not found at $CONFIG"
    exit 1
fi

HOST="$(jq -r '.host' "$CONFIG")"
SHARE="$(jq -r '.share' "$CONFIG")"
MOUNT="$(jq -r '.mountPoint // "/mnt/synology"' "$CONFIG")"
CREDS="$(jq -r '.credentialsFile' "$CONFIG" | sed "s|^~|$HOME|")"
SMB_VER="$(jq -r '.smbVersion // "3.0"' "$CONFIG")"

# --- Input validation ---
if [[ -z "$HOST" || "$HOST" == "null" ]]; then echo "Error: host is required"; exit 1; fi
if ! [[ "$HOST" =~ ^[a-zA-Z0-9._-]+$ ]]; then echo "Error: host contains invalid characters"; exit 1; fi
if [[ -z "$SHARE" || "$SHARE" == "null" ]]; then echo "Error: share is required"; exit 1; fi
if ! [[ "$SHARE" =~ ^[a-zA-Z0-9/_.-]+$ ]]; then echo "Error: share contains invalid characters"; exit 1; fi
if [[ "$SHARE" == *".."* ]]; then echo "Error: share must not contain path traversal (..)"; exit 1; fi
if [[ -z "$MOUNT" || "$MOUNT" == "null" ]]; then echo "Error: mountPoint is required"; exit 1; fi
if ! [[ "$MOUNT" =~ ^/[a-zA-Z0-9/_.-]+$ ]]; then echo "Error: mountPoint must be an absolute path with safe characters"; exit 1; fi
if [[ "$MOUNT" == *".."* ]]; then echo "Error: mountPoint must not contain path traversal (..)"; exit 1; fi
if [[ -z "$CREDS" || "$CREDS" == "null" || ! -f "$CREDS" ]]; then echo "Error: credentialsFile not found"; exit 1; fi
if ! [[ "$SMB_VER" =~ ^[0-9.]+$ ]]; then echo "Error: smbVersion contains invalid characters"; exit 1; fi

BACKUP_DIR="$MOUNT/backups"

# Ensure mount
if ! mountpoint -q "$MOUNT"; then
    mkdir -p "$MOUNT"
    mount -t cifs "//${HOST}/${SHARE}" "$MOUNT" \
        -o "credentials=${CREDS},vers=${SMB_VER}"
fi

# No date given — list available snapshots
if [[ -z "${1:-}" ]]; then
    echo "Available snapshots:"
    echo ""
    while IFS= read -r snap_name; do
        [[ -z "$snap_name" ]] && continue
        snap="${BACKUP_DIR}/${snap_name}"
        size="$(du -sh "$snap" 2>/dev/null | cut -f1)"
        manifest="${snap}/manifest.json"
        if [[ -f "$manifest" ]]; then
            ts="$(jq -r '.timestamp' "$manifest")"
            echo "  $snap_name  ($size)  backed up $ts"
        else
            echo "  $snap_name  ($size)"
        fi
    done < <(ls -1 "$BACKUP_DIR" | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' | sort -r)
    echo ""
    echo "Usage: $0 <date>  (e.g., $0 2026-02-20)"
    exit 0
fi

DATE="$1"

# Strict date format validation
if ! [[ "$DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo "Error: Invalid date format. Use YYYY-MM-DD (e.g., 2026-02-20)"
    exit 1
fi

SNAP_DIR="${BACKUP_DIR}/${DATE}"

if [[ ! -d "$SNAP_DIR" ]]; then
    echo "Error: No snapshot found for $DATE"
    echo "Run without arguments to list available snapshots."
    exit 1
fi

echo "⚠️  This will overwrite current files with snapshot from $DATE"
echo "   Source: $SNAP_DIR"
echo ""
read -p "Continue? [y/N] " confirm
[[ "$confirm" =~ ^[Yy]$ ]] || { echo "Aborted."; exit 0; }

# Restore workspace
if [[ -d "${SNAP_DIR}/workspace" ]]; then
    rsync -a --delete "${SNAP_DIR}/workspace/" "$HOME/.openclaw/workspace/"
    echo "✓ workspace"
fi

# Restore sub-agent workspaces
for ws in "${SNAP_DIR}"/workspace-*/; do
    [[ -d "$ws" ]] || continue
    name="$(basename "$ws")"
    # Validate: alphanumeric, hyphens, underscores only (no traversal)
    if ! [[ "$name" =~ ^workspace-[a-zA-Z0-9_-]+$ ]]; then
        echo "⚠️  Skipping suspicious workspace name: $name"
        continue
    fi
    rsync -a --delete "${ws}" "$HOME/.openclaw/${name}/"
    echo "✓ $name"
done

# Restore config files (explicit allowlist only)
for file in openclaw.json .env; do
    if [[ -f "${SNAP_DIR}/${file}" ]]; then
        cp -- "${SNAP_DIR}/${file}" "$HOME/.openclaw/${file}"
        echo "✓ $file"
    fi
done

# Restore directories (explicit allowlist only)
for dir in cron agents; do
    if [[ -d "${SNAP_DIR}/${dir}" ]]; then
        rsync -a --delete "${SNAP_DIR}/${dir}/" "$HOME/.openclaw/${dir}/"
        echo "✓ $dir"
    fi
done

echo ""
echo "Restore complete from $DATE. Restart OpenClaw to apply config changes."
