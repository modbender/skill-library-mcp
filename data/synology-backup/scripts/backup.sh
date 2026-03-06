#!/bin/bash
# Synology Backup — Incremental daily snapshot via SMB
set -euo pipefail

CONFIG="${SYNOLOGY_BACKUP_CONFIG:-$HOME/.openclaw/synology-backup.json}"

if [[ ! -f "$CONFIG" ]]; then
    echo "Error: Config not found at $CONFIG"
    echo "Create it from the skill docs or set SYNOLOGY_BACKUP_CONFIG"
    exit 1
fi

# Parse config — all values quoted throughout
HOST="$(jq -r '.host' "$CONFIG")"
SHARE="$(jq -r '.share' "$CONFIG")"
MOUNT="$(jq -r '.mountPoint // "/mnt/synology"' "$CONFIG")"
CREDS="$(jq -r '.credentialsFile' "$CONFIG" | sed "s|^~|$HOME|")"
SMB_VER="$(jq -r '.smbVersion // "3.0"' "$CONFIG")"
RETENTION="$(jq -r '.retention // 7' "$CONFIG")"
INCLUDE_SUBAGENT="$(jq -r '.includeSubAgentWorkspaces // true' "$CONFIG")"

# --- Input validation ---
# Host: IP addresses and hostnames only
if [[ -z "$HOST" || "$HOST" == "null" ]]; then echo "Error: host is required in config"; exit 1; fi
if ! [[ "$HOST" =~ ^[a-zA-Z0-9._-]+$ ]]; then echo "Error: host contains invalid characters"; exit 1; fi

# Share: alphanumeric, slashes, hyphens, underscores, dots (standard SMB path)
if [[ -z "$SHARE" || "$SHARE" == "null" ]]; then echo "Error: share is required in config"; exit 1; fi
if ! [[ "$SHARE" =~ ^[a-zA-Z0-9/_.-]+$ ]]; then echo "Error: share contains invalid characters (allowed: alphanumeric / _ . -)"; exit 1; fi
if [[ "$SHARE" == *".."* ]]; then echo "Error: share must not contain path traversal (..)"; exit 1; fi

# Mount point: absolute path, no traversal
if [[ -z "$MOUNT" || "$MOUNT" == "null" ]]; then echo "Error: mountPoint is required"; exit 1; fi
if ! [[ "$MOUNT" =~ ^/[a-zA-Z0-9/_.-]+$ ]]; then echo "Error: mountPoint must be an absolute path with safe characters"; exit 1; fi
if [[ "$MOUNT" == *".."* ]]; then echo "Error: mountPoint must not contain path traversal (..)"; exit 1; fi

# Credentials file
if [[ -z "$CREDS" || "$CREDS" == "null" || ! -f "$CREDS" ]]; then echo "Error: credentialsFile not found: $CREDS"; exit 1; fi

# SMB version: digits and dots only
if ! [[ "$SMB_VER" =~ ^[0-9.]+$ ]]; then echo "Error: smbVersion contains invalid characters"; exit 1; fi

# Retention: positive integer only
if ! [[ "$RETENTION" =~ ^[0-9]+$ ]]; then echo "Error: retention must be a number"; exit 1; fi

# Include subagent: boolean only
if [[ "$INCLUDE_SUBAGENT" != "true" && "$INCLUDE_SUBAGENT" != "false" ]]; then
    echo "Error: includeSubAgentWorkspaces must be true or false"; exit 1
fi

# --- Validate all backup paths before starting ---
validate_path() {
    local p="$1"
    # Must not contain command substitution, semicolons, pipes, backticks, or traversal
    if [[ "$p" == *'$('* || "$p" == *'`'* || "$p" == *';'* || "$p" == *'|'* || "$p" == *'&'* || "$p" == *".."* ]]; then
        echo "Error: backupPath contains unsafe characters: $p"
        exit 1
    fi
    # Must start with ~ or / (absolute or home-relative)
    if ! [[ "$p" =~ ^[~/] ]]; then
        echo "Error: backupPath must be absolute or home-relative (~): $p"
        exit 1
    fi
}

while IFS= read -r path_raw; do
    validate_path "$path_raw"
done < <(jq -r '.backupPaths[]' "$CONFIG")

# --- Begin backup ---
TIMESTAMP="$(date +%Y-%m-%d)"
BACKUP_DIR="$MOUNT/backups"
SNAP_DIR="$BACKUP_DIR/$TIMESTAMP"

# Ensure mount
if ! mountpoint -q "$MOUNT"; then
    mkdir -p "$MOUNT"
    mount -t cifs "//${HOST}/${SHARE}" "$MOUNT" \
        -o "credentials=${CREDS},vers=${SMB_VER}"
    echo "Mounted //${HOST}/${SHARE} → $MOUNT"
fi

mkdir -p "$SNAP_DIR"

# Backup configured paths
while IFS= read -r path_raw; do
    path="$(echo "$path_raw" | sed "s|^~|$HOME|")"

    if [[ ! -e "$path" ]]; then
        echo "⚠️  Skipping (not found): $path"
        continue
    fi

    name="$(basename "$path")"

    if [[ -d "$path" ]]; then
        rsync -a --delete "${path}/" "${SNAP_DIR}/${name}/"
    else
        cp -- "$path" "${SNAP_DIR}/${name}"
    fi
    echo "✓ $name"
done < <(jq -r '.backupPaths[]' "$CONFIG")

# Backup sub-agent workspaces
if [[ "$INCLUDE_SUBAGENT" == "true" ]]; then
    for ws in "$HOME"/.openclaw/workspace-*/; do
        [[ -d "$ws" ]] || continue
        name="$(basename "$ws")"
        if [[ "$name" == *".."* || "$name" == *"/"* ]]; then continue; fi
        rsync -a --delete "${ws}" "${SNAP_DIR}/${name}/"
        echo "✓ $name"
    done
fi

# Prune old snapshots (move to .trash for safety, then clean)
TRASH_DIR="$BACKUP_DIR/.trash"
mkdir -p "$TRASH_DIR"
if [[ -d "$BACKUP_DIR" ]]; then
    while IFS= read -r old_snap; do
        [[ -z "$old_snap" ]] && continue
        if [[ "$old_snap" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
            mv -- "${BACKUP_DIR}/${old_snap}" "${TRASH_DIR}/${old_snap}" 2>/dev/null && echo "Pruned: $old_snap"
        fi
    done < <(ls -1 "$BACKUP_DIR" | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' | sort -r | tail -n +"$((RETENTION + 1))")
fi
# Clean trash older than 3 days
find "$TRASH_DIR" -maxdepth 1 -mindepth 1 -mtime +3 -exec rm -rf {} + 2>/dev/null

# Write manifest
cat > "${SNAP_DIR}/manifest.json" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "snapshot": "$TIMESTAMP",
  "host": "$(hostname)"
}
EOF

TOTAL_SIZE="$(du -sh "$SNAP_DIR" 2>/dev/null | cut -f1)"
SNAP_COUNT="$(ls -1 "$BACKUP_DIR" | grep -cE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' 2>/dev/null || echo 0)"
echo ""
echo "Backup complete: $SNAP_DIR ($TOTAL_SIZE)"
echo "Snapshots: $SNAP_COUNT (keeping last $RETENTION)"
