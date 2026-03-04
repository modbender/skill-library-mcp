#!/bin/bash
# Alert poller wrapper - runs Python script, sends alerts to Telegram
# No model involved, just curl and Python

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
POLLER="$SCRIPT_DIR/alert_poller.py"
STATE_FILE="$SCRIPT_DIR/../references/alert_state.json"

# Run the poller, capture stdout
OUTPUT=$(python3 "$POLLER" 2>/dev/null)

# If output exists (alerts were found), send to Telegram
if [ -n "$OUTPUT" ]; then
    # Get Telegram config from OpenClaw
    OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
    
    if [ -f "$OPENCLAW_CONFIG" ]; then
        BOT_TOKEN=$(cat "$OPENCLAW_CONFIG" | jq -r '.channels.telegram.botToken // empty')
        CHAT_ID=$(cat "$OPENCLAW_CONFIG" | jq -r '.channels.telegram.chatId // empty')
        
        # Fallback to environment variables if not in config
        if [ -z "$BOT_TOKEN" ]; then
            BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
        fi
        if [ -z "$CHAT_ID" ]; then
            CHAT_ID="${TELEGRAM_CHAT_ID:-}"
        fi
    fi
    
    if [ -n "$BOT_TOKEN" ] && [ -n "$CHAT_ID" ]; then
        # URL encode the message
        MESSAGE=$(echo "$OUTPUT" | jq -sRr @uri)
        
        # Send to Telegram
        curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
            -d "chat_id=${CHAT_ID}" \
            -d "text=${MESSAGE}" \
            -d "parse_mode=Markdown" \
            -d "disable_notification=false" > /dev/null
        
        echo "Alerts sent: $(echo "$OUTPUT" | wc -l)" >&2
    else
        echo "Error: No Telegram bot token or chat ID found" >&2
        echo "Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables"
        exit 1
    fi
else
    echo "No alerts at $(date '+%Y-%m-%d %H:%M')" >&2
fi
