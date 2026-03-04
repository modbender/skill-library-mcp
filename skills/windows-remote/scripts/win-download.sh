#!/bin/bash
# Download file from remote Windows via SCP
# Usage: win-download.sh <remote-path> <local-file>

set -e

HOST="${WINDOWS_SSH_HOST:?WINDOWS_SSH_HOST is required}"
PORT="${WINDOWS_SSH_PORT:-22}"
USER="${WINDOWS_SSH_USER:?WINDOWS_SSH_USER is required}"
KEY="${WINDOWS_SSH_KEY:-$HOME/.ssh/id_ed25519}"
TIMEOUT="${WINDOWS_SSH_TIMEOUT:-10}"

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: win-download.sh <remote-path> <local-file>" >&2
    exit 1
fi

REMOTE="$1"
LOCAL="$2"

SCP_OPTS=(
    -o "ConnectTimeout=$TIMEOUT"
    -o "StrictHostKeyChecking=no"
    -P "$PORT"
)

if [ -f "$KEY" ]; then
    SCP_OPTS+=(-i "$KEY")
fi

scp "${SCP_OPTS[@]}" "${USER}@${HOST}:${REMOTE}" "$LOCAL"
echo "Downloaded: ${HOST}:${REMOTE} -> $LOCAL"
