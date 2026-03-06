#!/bin/bash
# Configure LuLu Monitor settings

INSTALL_DIR="$HOME/.openclaw/lulu-monitor"
CONFIG_FILE="$INSTALL_DIR/config.json"

echo "⚙️  LuLu Monitor Configuration"
echo ""

# Check if installed
if [ ! -d "$INSTALL_DIR" ]; then
    echo "❌ LuLu Monitor not installed."
    echo "   Run install.sh first."
    exit 1
fi

# Load existing config or create default
if [ -f "$CONFIG_FILE" ]; then
    CURRENT_TG_ID=$(grep -o '"telegramId":"[^"]*"' "$CONFIG_FILE" 2>/dev/null | cut -d'"' -f4)
else
    CURRENT_TG_ID=""
fi

echo "Current Telegram ID: ${CURRENT_TG_ID:-not set}"
echo ""
read -p "Enter your Telegram user ID (or press Enter to keep current): " NEW_TG_ID

if [ -n "$NEW_TG_ID" ]; then
    # Update config
    cat > "$CONFIG_FILE" << EOF
{
  "telegramId": "$NEW_TG_ID"
}
EOF
    echo ""
    echo "✅ Configuration saved!"
    echo ""
    echo "🔄 Restarting service..."
    launchctl unload "$HOME/Library/LaunchAgents/com.openclaw.lulu-monitor.plist" 2>/dev/null || true
    launchctl load "$HOME/Library/LaunchAgents/com.openclaw.lulu-monitor.plist"
    echo "✅ Service restarted"
else
    echo ""
    echo "⏭️  No changes made"
fi

echo ""
echo "To find your Telegram ID:"
echo "  1. Message @userinfobot on Telegram"
echo "  2. It will reply with your user ID"
