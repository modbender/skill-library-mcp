#!/bin/bash
# MOL IM Bridge Start Script - Runs bridge with auto-reconnect
# Usage: ./start.sh [BotName]
#
# Environment:
#   GATEWAY_TOKEN - Required. Your OpenClaw gateway token.
#   GATEWAY_URL   - Optional. Default: ws://127.0.0.1:18789
#
# To stop: echo 'QUIT' > /tmp/mol-im-bot/outbox.txt
#      or: pkill -f 'node bridge.js'

BOT_DIR="/tmp/mol-im-bot"
SCREEN_NAME="${1:-MoltBot}"

# Check for gateway token
if [ -z "$GATEWAY_TOKEN" ]; then
    CONFIG_FILE="$HOME/.openclaw/openclaw.json"
    if [ -f "$CONFIG_FILE" ]; then
        echo "⚠️  GATEWAY_TOKEN not set. Reading from $CONFIG_FILE"
        GATEWAY_TOKEN=$(grep -o '"token":"[^"]*"' "$CONFIG_FILE" | head -1 | cut -d'"' -f4)
        if [ -z "$GATEWAY_TOKEN" ]; then
            echo "❌ Could not extract token from config. Set GATEWAY_TOKEN manually."
            exit 1
        fi
        export GATEWAY_TOKEN
        echo "✓ Token found"
    else
        echo "❌ GATEWAY_TOKEN not set and no config file found."
        echo "   Set it with: export GATEWAY_TOKEN='your-token'"
        exit 1
    fi
else
    echo "✓ Using GATEWAY_TOKEN from environment"
fi

# Check if bridge.js exists
if [ ! -f "$BOT_DIR/bridge.js" ]; then
    echo "❌ bridge.js not found in $BOT_DIR"
    echo "   Run setup.sh first!"
    exit 1
fi

echo "🦞 Starting MOL IM bridge as $SCREEN_NAME"
echo "   Stop with: echo 'QUIT' > $BOT_DIR/outbox.txt"
echo "          or: pkill -f 'node bridge.js'"
echo ""

cd "$BOT_DIR"

# Auto-reconnect loop
while true; do
    GATEWAY_TOKEN="$GATEWAY_TOKEN" node bridge.js "$SCREEN_NAME"
    EXIT_CODE=$?
    
    # Exit code 0 = clean quit (user sent QUIT command)
    if [ $EXIT_CODE -eq 0 ]; then
        echo "🦞 Bridge stopped cleanly. Goodbye!"
        exit 0
    fi
    
    # Any other exit = unexpected, reconnect
    echo "⚠️  Bridge exited with code $EXIT_CODE, reconnecting in 5s..."
    sleep 5
done
