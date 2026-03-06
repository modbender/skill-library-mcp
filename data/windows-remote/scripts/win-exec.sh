#!/bin/bash
# Execute command on remote Windows via SSH
# Usage: win-exec.sh "<command>"

set -e

# Load config from environment (with defaults)
HOST="${WINDOWS_SSH_HOST:?WINDOWS_SSH_HOST is required}"
PORT="${WINDOWS_SSH_PORT:-22}"
USER="${WINDOWS_SSH_USER:?WINDOWS_SSH_USER is required}"
KEY="${WINDOWS_SSH_KEY:-$HOME/.ssh/id_ed25519}"
TIMEOUT="${WINDOWS_SSH_TIMEOUT:-10}"

if [ -z "$1" ]; then
    echo "Usage: win-exec.sh \"<command>\"" >&2
    exit 1
fi

COMMAND="$1"

# Build SSH options
SSH_OPTS=(
    -o "ConnectTimeout=$TIMEOUT"
    -o "StrictHostKeyChecking=no"
    -o "BatchMode=yes"
    -p "$PORT"
)

# Add key if exists
if [ -f "$KEY" ]; then
    SSH_OPTS+=(-i "$KEY")
fi

# Execute
ssh "${SSH_OPTS[@]}" "${USER}@${HOST}" "$COMMAND"
