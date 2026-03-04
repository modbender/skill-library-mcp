#!/bin/bash
# Send notification about sync events via Feishu

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$HOME/.config/openclaw/sync-config.yaml"
SYNC_REPO="${SYNC_REPO:-$HOME/openclaw-sync}"

# Get device name from config
DEVICE_NAME="unknown"
if [[ -f "$CONFIG_FILE" ]]; then
    DEVICE_NAME=$(grep "device_name:" "$CONFIG_FILE" | awk '{print $2}' | tr -d '"')
fi
DEVICE_NAME="${DEVICE_NAME:-$(hostname)}"

NOTIFY_TYPE="${1:-info}"
MESSAGE="${2:-}"

send_feishu_message() {
    local msg="$1"
    
    # Try to use OpenClaw's message tool if available
    # This requires being called from within OpenClaw agent context
    if command -v openclaw &> /dev/null; then
        # We're in a context where openclaw CLI is available
        # But this is rare - usually we're called from shell scripts
        echo "$msg"  # Just print for now
        return 0
    fi
    
    # Alternative: write to a notification file that OpenClaw can read
    local notify_dir="$HOME/.openclaw/notifications"
    mkdir -p "$notify_dir"
    
    local notify_file="$notify_dir/sync-$(date +%s).txt"
    cat > "$notify_file" << EOF
type: sync
device: $DEVICE_NAME
time: $(date '+%Y-%m-%d %H:%M:%S')
message: |
  $msg
EOF
    
    echo "Notification queued: $notify_file"
}

case "$NOTIFY_TYPE" in
    conflict)
        FILES="$MESSAGE"
        MSG="🚨 Sync Conflict on ${DEVICE_NAME}

Conflicting files:
${FILES}

Run to resolve:
  cd ~/openclaw-sync && ./scripts/sync-resolve

Auto-sync paused until resolved."
        send_feishu_message "$MSG"
        ;;
    
    push)
        MSG="📤 Sync Push from ${DEVICE_NAME}
$(date '+%Y-%m-%d %H:%M:%S')
${MESSAGE:-Changes pushed to remote.}"
        send_feishu_message "$MSG"
        ;;
    
    pull)
        MSG="📥 Sync Pull on ${DEVICE_NAME}
$(date '+%Y-%m-%d %H:%M:%S')
${MESSAGE:-Changes pulled from remote.}"
        send_feishu_message "$MSG"
        ;;
    
    error)
        MSG="❌ Sync Error on ${DEVICE_NAME}
$(date '+%Y-%m-%d %H:%M:%S')
${MESSAGE:-Unknown error occurred.}"
        send_feishu_message "$MSG"
        ;;
    
    *)
        MSG="ℹ️ Sync Notification from ${DEVICE_NAME}
$(date '+%Y-%m-%d %H:%M:%S')
${MESSAGE:-}"
        send_feishu_message "$MSG"
        ;;
esac
