#!/bin/bash
# Install LuLu Monitor service

set -e

REPO_URL="https://github.com/EasonC13-agent/lulu-monitor.git"
INSTALL_DIR="$HOME/.openclaw/lulu-monitor"
PLIST_NAME="com.openclaw.lulu-monitor.plist"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

echo "🚀 Installing LuLu Monitor..."
echo ""

# Check prerequisites first
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$SCRIPT_DIR/check-prerequisites.sh" ]; then
    bash "$SCRIPT_DIR/check-prerequisites.sh" || {
        echo ""
        echo "❌ Prerequisites check failed. Please resolve the issues above."
        exit 1
    }
fi

echo ""
echo "📦 Cloning repository..."
if [ -d "$INSTALL_DIR" ]; then
    echo "   Directory exists, pulling latest..."
    cd "$INSTALL_DIR"
    git pull origin main
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

echo ""
echo "📥 Installing dependencies..."
npm install --production

echo ""
echo "📝 Setting up launchd service..."
mkdir -p "$LAUNCH_AGENTS"

# Create launchd plist
cat > "$LAUNCH_AGENTS/$PLIST_NAME" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.lulu-monitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>$(which node)</string>
        <string>$INSTALL_DIR/src/index.js</string>
        <string>--verbose</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$INSTALL_DIR/logs/stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$INSTALL_DIR/logs/stderr.log</string>
    <key>WorkingDirectory</key>
    <string>$INSTALL_DIR</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$(dirname $(which node))</string>
    </dict>
</dict>
</plist>
EOF

echo ""
echo "🔄 Starting service..."
mkdir -p "$INSTALL_DIR/logs"
launchctl unload "$LAUNCH_AGENTS/$PLIST_NAME" 2>/dev/null || true
launchctl load "$LAUNCH_AGENTS/$PLIST_NAME"

# Verify service is running
sleep 2
if curl -s http://127.0.0.1:4441/status | grep -q '"running":true'; then
    echo ""
    echo "✅ LuLu Monitor installed and running!"
    echo ""
    echo "📍 Install location: $INSTALL_DIR"
    echo "📡 Status endpoint:  http://127.0.0.1:4441/status"
    echo "📋 Logs:             $INSTALL_DIR/logs/"
    echo ""
    echo "🔔 When a LuLu alert appears, you'll receive a Telegram notification"
    echo "   with Allow/Block buttons."
    echo ""
    echo "To uninstall: bash $INSTALL_DIR/skill/scripts/uninstall.sh"
else
    echo ""
    echo "⚠️  Service may not have started correctly."
    echo "   Check logs: tail -f $INSTALL_DIR/logs/stderr.log"
    exit 1
fi
