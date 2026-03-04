#!/bin/bash
# Signal Send - Send message with typing indicator and conversation logging
# Usage: signal-send.sh <recipient> <message>
# Recipient can be a phone number (+1234567890) or UUID

# ============ CONFIGURATION ============
SIGNAL_NUMBER="+YOUR_NUMBER_HERE"
SIGNAL_CLI="signal-cli"  # or full path
STATE_DIR="$HOME/.signal-state"
HISTORY_DIR="$STATE_DIR/conversations"
# =======================================

recipient="$1"
message="$2"

if [[ -z "$recipient" || -z "$message" ]]; then
    echo "Usage: signal-send.sh <recipient> <message>"
    exit 1
fi

mkdir -p "$HISTORY_DIR"

# Send typing indicator
$SIGNAL_CLI -a "$SIGNAL_NUMBER" sendTyping "$recipient" 2>/dev/null

# Brief pause for typing indicator to register
sleep 0.5

# Send the message
$SIGNAL_CLI -a "$SIGNAL_NUMBER" send -m "$message" "$recipient"

# Stop typing indicator
$SIGNAL_CLI -a "$SIGNAL_NUMBER" sendTyping -s "$recipient" 2>/dev/null

# Log to conversation history
history_file="$HISTORY_DIR/${recipient}.log"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Bot: $message" >> "$history_file"

# Note: Permissions are managed via permissions.json, not auto-added
# To grant access: edit $STATE_DIR/permissions.json

echo "Sent and logged to $history_file"
