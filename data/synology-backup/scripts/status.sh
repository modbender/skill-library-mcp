#!/bin/bash
# Synology Backup — Status check
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
RETENTION="$(jq -r '.retention // 7' "$CONFIG")"

# --- Input validation ---
if [[ -z "$HOST" || "$HOST" == "null" ]]; then echo "Error: host is required"; exit 1; fi
if ! [[ "$HOST" =~ ^[a-zA-Z0-9._-]+$ ]]; then echo "Error: host contains invalid characters"; exit 1; fi
if [[ -z "$SHARE" || "$SHARE" == "null" ]]; then echo "Error: share is required"; exit 1; fi
if ! [[ "$SHARE" =~ ^[a-zA-Z0-9/_.-]+$ ]]; then echo "Error: share contains invalid characters"; exit 1; fi
if [[ "$SHARE" == *".."* ]]; then echo "Error: share must not contain path traversal (..)"; exit 1; fi
if [[ -z "$MOUNT" || "$MOUNT" == "null" ]]; then echo "Error: mountPoint is required"; exit 1; fi
if ! [[ "$MOUNT" =~ ^/[a-zA-Z0-9/_.-]+$ ]]; then echo "Error: mountPoint must be an absolute path with safe characters"; exit 1; fi
if [[ "$MOUNT" == *".."* ]]; then echo "Error: mountPoint must not contain path traversal (..)"; exit 1; fi
if ! [[ "$SMB_VER" =~ ^[0-9.]+$ ]]; then echo "Error: smbVersion contains invalid characters"; exit 1; fi
if ! [[ "$RETENTION" =~ ^[0-9]+$ ]]; then echo "Error: retention must be a number"; exit 1; fi

BACKUP_DIR="$MOUNT/backups"

echo "=== Synology Backup Status ==="
echo ""

# Check mount
if mountpoint -q "$MOUNT" 2>/dev/null; then
    echo "Mount:     ✅ $MOUNT → //${HOST}/${SHARE}"
else
    echo "Mount:     ❌ Not mounted"
    echo "           Attempting mount..."
    mkdir -p "$MOUNT"
    if [[ -f "$CREDS" ]] && mount -t cifs "//${HOST}/${SHARE}" "$MOUNT" -o "credentials=${CREDS},vers=${SMB_VER}" 2>/dev/null; then
        echo "           ✅ Mounted successfully"
    else
        echo "           ❌ Mount failed — check host, share, and credentials"
        exit 1
    fi
fi

# Check disk space
DISK_INFO="$(df -h "$MOUNT" | tail -1)"
DISK_SIZE="$(echo "$DISK_INFO" | awk '{print $2}')"
DISK_AVAIL="$(echo "$DISK_INFO" | awk '{print $4}')"
DISK_PCT="$(echo "$DISK_INFO" | awk '{print $5}')"
echo "Disk:      $DISK_AVAIL available of $DISK_SIZE ($DISK_PCT used)"

# Snapshot info
if [[ -d "$BACKUP_DIR" ]]; then
    SNAP_COUNT="$(ls -1 "$BACKUP_DIR" | grep -cE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' 2>/dev/null || echo 0)"
    TOTAL_SIZE="$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)"

    echo "Snapshots: $SNAP_COUNT (retention: $RETENTION days)"
    echo "Total:     $TOTAL_SIZE"
    echo ""

    # Latest snapshot
    LATEST_NAME="$(ls -1 "$BACKUP_DIR" | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' | sort -r | head -1)"
    if [[ -n "$LATEST_NAME" ]]; then
        LATEST="${BACKUP_DIR}/${LATEST_NAME}"
        LATEST_SIZE="$(du -sh "$LATEST" 2>/dev/null | cut -f1)"

        if [[ -f "${LATEST}/manifest.json" ]]; then
            LATEST_TS="$(jq -r '.timestamp' "${LATEST}/manifest.json")"
            echo "Latest:    $LATEST_NAME ($LATEST_SIZE) at $LATEST_TS"
        else
            echo "Latest:    $LATEST_NAME ($LATEST_SIZE)"
        fi

        # Age check
        LATEST_EPOCH="$(date -d "$LATEST_NAME" +%s 2>/dev/null || echo 0)"
        NOW_EPOCH="$(date +%s)"
        AGE_HOURS="$(( (NOW_EPOCH - LATEST_EPOCH) / 3600 ))"

        if [[ "$AGE_HOURS" -gt 48 ]]; then
            echo "⚠️  WARNING: Last backup is ${AGE_HOURS}h old!"
        fi
    fi

    echo ""
    echo "All snapshots:"
    while IFS= read -r snap_name; do
        [[ -z "$snap_name" ]] && continue
        size="$(du -sh "${BACKUP_DIR}/${snap_name}" 2>/dev/null | cut -f1)"
        echo "  $snap_name  $size"
    done < <(ls -1 "$BACKUP_DIR" | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' | sort -r)
else
    echo "Snapshots: None (no backups directory)"
fi
