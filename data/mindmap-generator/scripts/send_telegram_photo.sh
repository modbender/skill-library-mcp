#!/usr/bin/env bash
# send_telegram_photo.sh — Sends a PNG mindmap image to a Telegram chat
#
# Usage: ./send_telegram_photo.sh <image_path> <caption> <chat_id> [bot_token]
#
# The image appears INLINE in the Telegram conversation — no download required.
# Users see the mindmap directly in their chat, on mobile or desktop.
#
# Dependencies:
#   - curl
#   - TELEGRAM_BOT_TOKEN env var (or pass as 4th argument)
#
# Telegram Bot API limits:
#   - Photos: max 10MB
#   - Caption: max 1024 characters
#   - Supported formats: JPEG, PNG, GIF (PNG is best for mindmaps)

set -euo pipefail

IMAGE_PATH="${1:?Usage: send_telegram_photo.sh <image_path> <caption> <chat_id> [bot_token]}"
CAPTION="${2:?Usage: send_telegram_photo.sh <image_path> <caption> <chat_id> [bot_token]}"
CHAT_ID="${3:?Usage: send_telegram_photo.sh <image_path> <caption> <chat_id> [bot_token]}"
BOT_TOKEN="${4:-${TELEGRAM_BOT_TOKEN:?Set TELEGRAM_BOT_TOKEN env var or pass as 4th argument}}"

# Validate image exists
if [[ ! -f "$IMAGE_PATH" ]]; then
    echo "Error: Image file not found: $IMAGE_PATH" >&2
    exit 1
fi

# Validate image is a PNG or JPEG
FILE_EXT="${IMAGE_PATH##*.}"
FILE_EXT_LOWER=$(echo "$FILE_EXT" | tr '[:upper:]' '[:lower:]')
if [[ "$FILE_EXT_LOWER" != "png" && "$FILE_EXT_LOWER" != "jpg" && "$FILE_EXT_LOWER" != "jpeg" ]]; then
    echo "Warning: File is not PNG/JPEG ($FILE_EXT). Telegram may not display it inline." >&2
fi

# Check file size (Telegram limit: 10MB for photos)
FILE_SIZE=$(wc -c < "$IMAGE_PATH" | tr -d ' ')
if [[ "$FILE_SIZE" -gt 10485760 ]]; then
    echo "Error: File exceeds Telegram's 10MB photo limit ($FILE_SIZE bytes)" >&2
    exit 1
fi

# Truncate caption if too long (Telegram limit: 1024 chars)
if [[ ${#CAPTION} -gt 1024 ]]; then
    CAPTION="${CAPTION:0:1021}..."
    echo "Warning: Caption truncated to 1024 characters" >&2
fi

TELEGRAM_API="https://api.telegram.org/bot${BOT_TOKEN}/sendPhoto"

echo "Sending mindmap to Telegram chat $CHAT_ID..."

RESPONSE=$(curl -s -X POST "$TELEGRAM_API" \
    -F "chat_id=$CHAT_ID" \
    -F "photo=@$IMAGE_PATH" \
    -F "caption=$CAPTION" \
    -F "parse_mode=HTML" \
    2>&1)

# Check if the API call succeeded
if echo "$RESPONSE" | grep -q '"ok":true'; then
    echo "✅ Mindmap sent successfully to Telegram"
    # Extract message_id for reference
    MSG_ID=$(echo "$RESPONSE" | grep -o '"message_id":[0-9]*' | head -1 | cut -d: -f2)
    if [[ -n "$MSG_ID" ]]; then
        echo "Message ID: $MSG_ID"
    fi
else
    echo "❌ Failed to send mindmap to Telegram" >&2
    echo "Response: $RESPONSE" >&2

    # Parse common errors
    if echo "$RESPONSE" | grep -q "chat not found"; then
        echo "Hint: Check that chat_id ($CHAT_ID) is correct and the bot has access" >&2
    elif echo "$RESPONSE" | grep -q "bot was blocked"; then
        echo "Hint: The user has blocked the bot. They need to unblock and /start again" >&2
    elif echo "$RESPONSE" | grep -q "Unauthorized"; then
        echo "Hint: Bot token is invalid. Check TELEGRAM_BOT_TOKEN" >&2
    fi

    exit 1
fi
