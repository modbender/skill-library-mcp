#!/bin/bash
set -e

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ Error: This skill is macOS-only"
    echo "   Menu bar apps are not supported on Windows or Linux"
    exit 1
fi

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_DIR="$SKILL_DIR/assets/openclaw-menubar"

# Check if already running
if pgrep -f "openclaw-menubar.*electron" > /dev/null; then
    echo "⚠️  OpenClaw Menu Bar is already running"
    echo "   Use 'scripts/stop.sh' to stop it first"
    exit 1
fi

# Check if OpenClaw Gateway is running
if ! curl -s http://localhost:18789/health > /dev/null 2>&1; then
    echo "⚠️  Warning: OpenClaw Gateway doesn't seem to be running"
    echo "   Start it with: openclaw gateway start"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "🚀 Launching OpenClaw Menu Bar..."

cd "$APP_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Dependencies not installed. Run 'scripts/install.sh' first"
    exit 1
fi

# Launch in background
npm start > /dev/null 2>&1 &

sleep 2

if pgrep -f "openclaw-menubar.*electron" > /dev/null; then
    echo "✅ OpenClaw Menu Bar is running!"
    echo "   Look for the 🦀 icon in your menu bar"
    echo "   Click it to open the chat popup"
    echo "   Keyboard shortcut: Cmd+Shift+O"
else
    echo "❌ Failed to start. Check the logs:"
    echo "   cd $APP_DIR && npm start"
fi
