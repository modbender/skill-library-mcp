#!/bin/bash
# macOS Screenshot to Telegram
# Usage: ./screenshot-telegram.sh <chat-id> <profile>
# Example: ./screenshot-telegram.sh 123456789 main

CHAT_ID="${1}"
PROFILE="${2}"

if [ -z "$CHAT_ID" ] || [ -z "$PROFILE" ]; then
    echo "Usage: $0 <chat-id> <profile>"
    echo "Example: $0 123456789 main"
    exit 1
fi

CONFIG_PATH="$HOME/.openclaw-${PROFILE}/openclaw.json"
WORKSPACE="$HOME/.openclaw/workspace-${PROFILE}"

# Get bot token from config
BOT_TOKEN=$(grep botToken "$CONFIG_PATH" 2>/dev/null | sed 's/.*"botToken": *"\([^"]*\)".*/\1/')

if [ -z "$BOT_TOKEN" ]; then
    echo "ERROR: Could not find botToken in $CONFIG_PATH"
    exit 1
fi

# Capture screenshot
echo "Capturing screenshot..."
/usr/sbin/screencapture -x "${WORKSPACE}/screen.png"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to capture screenshot"
    exit 1
fi

# Send via Telegram Bot API
echo "Sending to Telegram chat $CHAT_ID..."
RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendPhoto" \
    -F "chat_id=${CHAT_ID}" \
    -F "photo=@${WORKSPACE}/screen.png")

if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo "SUCCESS: Screenshot sent!"
    echo "$RESPONSE" | grep -o '"message_id":[0-9]*' | head -1
else
    echo "ERROR: Failed to send"
    echo "$RESPONSE"
    exit 1
fi
