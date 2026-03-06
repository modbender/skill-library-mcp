#!/bin/bash
# =============================================================================
# upload_media_remote.sh
# Transfers an image to a remote server via SCP and imports it into 
# WordPress using WP-CLI executed remotely via SSH.
# =============================================================================

set -euo pipefail

# --- SSH Configuration from Environment Variables ---
SSH_HOST="${WP_SSH_HOST:-}"
SSH_USER="${WP_SSH_USER:-}"
SSH_KEY="${WP_SSH_KEY:-}"
SSH_PORT="${WP_SSH_PORT:-22}"
REMOTE_PATH="${WP_REMOTE_PATH:-/var/www/html/wordpress}"
REMOTE_TMP="${WP_REMOTE_TMP:-/tmp}"

# --- SSH Options ---
# -i: identity file (private key)
# -o StrictHostKeyChecking=no: don't prompt about host keys
# -o BatchMode=yes: fail if password required (force key auth)
# -o ConnectTimeout=15: timeout for connection
# -o PasswordAuthentication=no: explicitly disable password auth
SSH_OPTS="-i $SSH_KEY -p $SSH_PORT \
          -o StrictHostKeyChecking=no \
          -o BatchMode=yes \
          -o ConnectTimeout=15 \
          -o PasswordAuthentication=no"

# --- Input Validation ---
IMAGE_PATH="${1:-}"

if [ -z "$SSH_HOST" ] || [ -z "$SSH_USER" ] || [ -z "$SSH_KEY" ]; then
    echo "ERROR: WP_SSH_HOST, WP_SSH_USER, and WP_SSH_KEY are required" >&2
    exit 1
fi

if [ -z "$IMAGE_PATH" ]; then
    echo "Usage: $0 <image_path>" >&2
    echo "Example: $0 /tmp/cover_optimized.jpg" >&2
    exit 1
fi

if [ ! -f "$SSH_KEY" ]; then
    echo "ERROR: SSH key not found: $SSH_KEY" >&2
    exit 1
fi

if [ ! -f "$IMAGE_PATH" ]; then
    echo "ERROR: Image file not found: $IMAGE_PATH" >&2
    exit 1
fi

# --- Generate unique filename for remote ---
TIMESTAMP=$(date +%s)
REMOTE_FILENAME="wp_cover_${TIMESTAMP}.jpg"
REMOTE_FILE_PATH="${REMOTE_TMP}/${REMOTE_FILENAME}"

# --- Step 1: Transfer image via SCP ---
echo "Transferring image to $SSH_USER@$SSH_HOST:$REMOTE_FILE_PATH ..."

if ! scp $SSH_OPTS "$IMAGE_PATH" "$SSH_USER@$SSH_HOST:$REMOTE_FILE_PATH"; then
    echo "ERROR: SCP transfer failed" >&2
    exit 1
fi

echo "Image transferred successfully"

# --- Step 2: Import media into WordPress via WP-CLI (remote) ---
echo "Importing media into WordPress via WP-CLI ..."

MEDIA_ID=$(ssh $SSH_OPTS "$SSH_USER@$SSH_HOST" \
    "wp media import '$REMOTE_FILE_PATH' \
     --path='$REMOTE_PATH' \
     --porcelain 2>/dev/null")

if [ -z "$MEDIA_ID" ]; then
    echo "ERROR: wp media import returned no ID" >&2
    # Cleanup remote temp file on failure
    ssh $SSH_OPTS "$SSH_USER@$SSH_HOST" "rm -f '$REMOTE_FILE_PATH'" 2>/dev/null || true
    exit 1
fi

# --- Step 3: Cleanup remote temp file ---
ssh $SSH_OPTS "$SSH_USER@$SSH_HOST" "rm -f '$REMOTE_FILE_PATH'" 2>/dev/null || true

# --- Save Media ID for later use ---
echo "$MEDIA_ID" > /tmp/wp_media_id.txt

echo "Media imported to WordPress with ID: $MEDIA_ID"
echo "Media ID saved to: /tmp/wp_media_id.txt"

exit 0
