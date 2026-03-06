#!/bin/bash
# Mount a RunPod pod's filesystem via SSHFS
# Usage: mount_pod.sh <pod_id> [base_dir]
# Default base_dir: $HOME/pods

POD_ID="$1"
BASE_DIR="${2:-$HOME/pods}"
MOUNT_PATH="$BASE_DIR/$POD_ID"
SSH_KEY="${RUNPOD_SSH_KEY:-$HOME/.ssh/runpod_key}"
RUNPOD_KNOWN_HOSTS="${RUNPOD_KNOWN_HOSTS:-$HOME/.runpod/ssh/known_hosts}"

# Fallback to runpodctl-generated key if default doesn't exist
if [ ! -f "$SSH_KEY" ] && [ -f "$HOME/.runpod/ssh/RunPod-Key" ]; then
    SSH_KEY="$HOME/.runpod/ssh/RunPod-Key"
fi

if [ -z "$POD_ID" ]; then
    echo "Usage: $0 <pod_id> [base_dir]"
    exit 1
fi

if [ ! -f "$SSH_KEY" ]; then
    echo "Error: SSH key not found"
    echo "Generate with runpodctl: runpodctl ssh add-key"
    echo "Or set custom path: export RUNPOD_SSH_KEY=\"\$HOME/.runpod/ssh/Your-Key\""
    exit 1
fi

mkdir -p "$BASE_DIR"
mkdir -p "$MOUNT_PATH"

if mount | grep -q "$MOUNT_PATH"; then
    echo "Already mounted at $MOUNT_PATH"
    exit 0
fi

echo "Getting SSH info for pod $POD_ID..."
SSH_CMD=$(runpodctl ssh connect "$POD_ID" 2>/dev/null | grep "ssh -p")

if [ -z "$SSH_CMD" ]; then
    echo "Error: Could not get SSH info. Is the pod running?"
    exit 1
fi

PORT=$(echo "$SSH_CMD" | grep -oP '(?<=-p )[0-9]+')
IP=$(echo "$SSH_CMD" | grep -oP '(?<=root@)[^ ]+')

echo "Mounting $POD_ID ($IP:$PORT) to $MOUNT_PATH..."

# Ensure known_hosts directory exists
mkdir -p "$(dirname "$RUNPOD_KNOWN_HOSTS")"

sshfs -p "$PORT" "root@$IP:/" "$MOUNT_PATH" \
  -o IdentityFile="$SSH_KEY" \
  -o UserKnownHostsFile="$RUNPOD_KNOWN_HOSTS" \
  -o StrictHostKeyChecking=accept-new \
  -o reconnect,ServerAliveInterval=15,ServerAliveCountMax=3

if [ $? -eq 0 ]; then
    echo "✅ Mounted at $MOUNT_PATH"
else
    echo "❌ Failed to mount"
    exit 1
fi
