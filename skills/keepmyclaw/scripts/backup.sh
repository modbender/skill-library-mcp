#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="$HOME/.keepmyclaw"
CONFIG_FILE="$CONFIG_DIR/config"
PASSPHRASE_FILE="$CONFIG_DIR/passphrase"
OPENCLAW_DIR="$HOME/.openclaw"

# Load config
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: Config not found. Run setup.sh first." >&2; exit 1
fi
source "$CONFIG_FILE"

if [[ ! -f "$PASSPHRASE_FILE" ]]; then
    echo "Error: Passphrase not found. Run setup.sh first." >&2; exit 1
fi

PASSPHRASE="$(cat "$PASSPHRASE_FILE")"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

echo "=== ClawKeeper Backup ==="
echo "Agent: ${CLAWKEEPER_AGENT_NAME}"
echo

# Build file list
FILE_LIST="$TMPDIR/files.txt"
: > "$FILE_LIST"

for f in SOUL.md AGENTS.md USER.md IDENTITY.md TOOLS.md HEARTBEAT.md MEMORY.md; do
    [[ -f "$OPENCLAW_DIR/workspace/$f" ]] && echo "workspace/$f" >> "$FILE_LIST"
done
[[ -d "$OPENCLAW_DIR/workspace/memory" ]] && echo "workspace/memory" >> "$FILE_LIST"
[[ -f "$OPENCLAW_DIR/openclaw.json" ]] && echo "openclaw.json" >> "$FILE_LIST"
[[ -d "$OPENCLAW_DIR/credentials" ]] && echo "credentials" >> "$FILE_LIST"

if [[ ! -s "$FILE_LIST" ]]; then
    echo "Error: No files found to back up." >&2; exit 1
fi

echo "Files to back up:"
sed 's/^/  /' "$FILE_LIST"
echo

# Create tarball
TAR_FILE="$TMPDIR/backup.tar.gz"
tar -czf "$TAR_FILE" -C "$OPENCLAW_DIR" -T "$FILE_LIST" 2>/dev/null
TAR_SIZE="$(wc -c < "$TAR_FILE" | tr -d ' ')"
echo "✓ Archive created (${TAR_SIZE} bytes)"

# Encrypt
ENC_FILE="$TMPDIR/backup.tar.gz.enc"
openssl enc -aes-256-cbc -salt -pbkdf2 -iter 100000 \
    -in "$TAR_FILE" -out "$ENC_FILE" -pass "pass:${PASSPHRASE}"
ENC_SIZE="$(wc -c < "$ENC_FILE" | tr -d ' ')"
echo "✓ Encrypted (${ENC_SIZE} bytes)"

# Upload via API
echo "Uploading..."
HTTP_CODE="$(curl -s -o "$TMPDIR/response.json" -w '%{http_code}' \
    -X POST \
    -H "Authorization: Bearer ${CLAWKEEPER_API_KEY}" \
    -H "Content-Type: application/octet-stream" \
    --data-binary @"$ENC_FILE" \
    "${CLAWKEEPER_API_URL}/v1/agents/${CLAWKEEPER_AGENT_NAME}/backups")"

if [[ "$HTTP_CODE" -ge 200 && "$HTTP_CODE" -lt 300 ]]; then
    BACKUP_ID="$(python3 -c "import sys,json; print(json.load(open('$TMPDIR/response.json')).get('id','unknown'))" 2>/dev/null || echo "unknown")"
    echo "✓ Uploaded (id: ${BACKUP_ID})"
else
    echo "✗ Upload failed (HTTP ${HTTP_CODE})" >&2
    cat "$TMPDIR/response.json" >&2 2>/dev/null
    exit 1
fi

echo
echo "=== Backup complete ==="
