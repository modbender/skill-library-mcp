#!/usr/bin/env bash
set -euo pipefail

CONFIG_DIR="$HOME/.keepmyclaw"
CONFIG_FILE="$CONFIG_DIR/config"
PASSPHRASE_FILE="$CONFIG_DIR/passphrase"
OPENCLAW_DIR="$HOME/.openclaw"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "Error: Config not found. Run setup.sh first." >&2; exit 1
fi
source "$CONFIG_FILE"

if [[ ! -f "$PASSPHRASE_FILE" ]]; then
    echo "Error: Passphrase not found at $PASSPHRASE_FILE" >&2; exit 1
fi

PASSPHRASE="$(cat "$PASSPHRASE_FILE")"
TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

# Determine backup endpoint
BACKUP_ID="${1:-latest}"
ENDPOINT="${CLAWKEEPER_API_URL}/v1/agents/${CLAWKEEPER_AGENT_NAME}/backups/${BACKUP_ID}"

echo "=== ClawKeeper Restore ==="
echo "Agent: ${CLAWKEEPER_AGENT_NAME}"
echo "Backup: ${BACKUP_ID}"
echo

# Download
ENC_FILE="$TMPDIR/backup.tar.gz.enc"
echo "Downloading..."
HTTP_CODE="$(curl -s -o "$ENC_FILE" -w '%{http_code}' \
    -H "Authorization: Bearer ${CLAWKEEPER_API_KEY}" \
    "$ENDPOINT")"

if [[ "$HTTP_CODE" -lt 200 || "$HTTP_CODE" -ge 300 ]]; then
    echo "✗ Download failed (HTTP ${HTTP_CODE})" >&2
    cat "$ENC_FILE" >&2 2>/dev/null
    exit 1
fi
echo "✓ Downloaded"

# Decrypt
TAR_FILE="$TMPDIR/backup.tar.gz"
echo "Decrypting..."
openssl enc -aes-256-cbc -d -salt -pbkdf2 -iter 100000 \
    -in "$ENC_FILE" -out "$TAR_FILE" -pass "pass:${PASSPHRASE}"
echo "✓ Decrypted"

# Extract
echo "Restoring to ${OPENCLAW_DIR}..."
mkdir -p "$OPENCLAW_DIR"
tar -xzf "$TAR_FILE" -C "$OPENCLAW_DIR"
echo "✓ Restored"

echo
echo "=== Restore complete ==="
