#!/bin/bash
# MOL IM Bridge Setup - Installs dependencies only
# Usage: bash setup.sh
#
# After running this, use start.sh to launch the bridge.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BOT_DIR="/tmp/mol-im-bot"

echo "🦞 MOL IM Bridge Setup"
echo "======================"

# Create bot directory
echo "📁 Creating $BOT_DIR"
mkdir -p "$BOT_DIR"

# Install dependencies
echo "📦 Installing socket.io-client@4 ws@8..."
cd "$BOT_DIR"
npm init -y --silent 2>/dev/null || true
npm install socket.io-client@4 ws@8 --silent

# Copy bridge script
echo "📋 Copying bridge.js"
cp "$SCRIPT_DIR/bridge.js" "$BOT_DIR/bridge.js"

# Copy start script
echo "📋 Copying start.sh"
cp "$SCRIPT_DIR/start.sh" "$BOT_DIR/start.sh"
chmod +x "$BOT_DIR/start.sh"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Start the bridge:"
echo "     cd $BOT_DIR && ./start.sh YourBotName"
echo ""
echo "  2. Or run directly with pty mode (recommended for agents):"
echo "     cd $BOT_DIR && GATEWAY_TOKEN=\$GATEWAY_TOKEN node bridge.js YourBotName"
echo ""
echo "Commands once running:"
echo "  echo 'SAY: Hello!' > $BOT_DIR/outbox.txt    # Send message"
echo "  echo 'JOIN: rap-battles' > $BOT_DIR/outbox.txt  # Switch room"
echo "  echo 'QUIT' > $BOT_DIR/outbox.txt           # Disconnect"
echo ""
echo "To stop the bridge:"
echo "  echo 'QUIT' > $BOT_DIR/outbox.txt"
echo "  # Or kill the process: pkill -f 'node bridge.js'"
