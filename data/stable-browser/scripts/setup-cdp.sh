#!/bin/bash
# stable-browser: Set up Chrome CDP for reliable OpenClaw browser automation
# Replaces the flaky extension relay with a direct DevTools Protocol connection

set -e

CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE_DIR="$HOME/.chrome-debug-profile"
CDP_PORT=9222
OPENCLAW_CONFIG="$HOME/.openclaw/openclaw.json"
PLIST_PATH="$HOME/Library/LaunchAgents/com.openclaw.chrome-cdp.plist"

echo "🔧 Setting up Chrome CDP for OpenClaw..."
echo ""

# 1. Check Chrome exists
if [ ! -f "$CHROME_PATH" ]; then
    echo "❌ Google Chrome not found at $CHROME_PATH"
    echo "   Install Chrome first: https://www.google.com/chrome/"
    exit 1
fi
echo "✅ Chrome found"

# 2. Create profile directory
mkdir -p "$PROFILE_DIR"
echo "✅ Profile directory: $PROFILE_DIR"

# 3. Kill any existing debug Chrome
if lsof -i :$CDP_PORT >/dev/null 2>&1; then
    echo "⚠️  Port $CDP_PORT in use — killing existing process..."
    pkill -f "remote-debugging-port=$CDP_PORT" 2>/dev/null || true
    sleep 2
fi

# 4. Launch Chrome with CDP
echo "🚀 Launching Chrome with CDP on port $CDP_PORT..."
"$CHROME_PATH" \
    --remote-debugging-port=$CDP_PORT \
    --user-data-dir="$PROFILE_DIR" \
    --no-first-run \
    --no-default-browser-check \
    --disable-background-timer-throttling \
    --disable-backgrounding-occluded-windows \
    --disable-renderer-backgrounding \
    &>/dev/null &

CHROME_PID=$!
sleep 3

# 5. Verify CDP is responding
if curl -s "http://127.0.0.1:$CDP_PORT/json/version" >/dev/null 2>&1; then
    echo "✅ CDP responding on port $CDP_PORT"
else
    echo "❌ CDP not responding. Chrome may have failed to start."
    echo "   Try launching manually:"
    echo "   \"$CHROME_PATH\" --remote-debugging-port=$CDP_PORT --user-data-dir=\"$PROFILE_DIR\""
    exit 1
fi

# 6. Update OpenClaw config
if [ -f "$OPENCLAW_CONFIG" ]; then
    if python3 -c "
import json, sys
with open('$OPENCLAW_CONFIG') as f:
    config = json.load(f)
if config.get('browser', {}).get('cdpUrl') == 'http://127.0.0.1:$CDP_PORT':
    sys.exit(0)
config.setdefault('browser', {})['cdpUrl'] = 'http://127.0.0.1:$CDP_PORT'
with open('$OPENCLAW_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
print('updated')
" 2>/dev/null | grep -q "updated"; then
        echo "✅ OpenClaw config updated (browser.cdpUrl)"
    else
        echo "✅ OpenClaw config already set"
    fi
else
    echo "⚠️  OpenClaw config not found at $OPENCLAW_CONFIG"
    echo "   Add manually: \"browser\": { \"cdpUrl\": \"http://127.0.0.1:$CDP_PORT\" }"
fi

# 7. Create LaunchAgent for auto-start (macOS only)
if [ "$(uname)" = "Darwin" ]; then
    mkdir -p "$(dirname "$PLIST_PATH")"
    cat > "$PLIST_PATH" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.chrome-cdp</string>
    <key>ProgramArguments</key>
    <array>
        <string>$CHROME_PATH</string>
        <string>--remote-debugging-port=$CDP_PORT</string>
        <string>--user-data-dir=$PROFILE_DIR</string>
        <string>--no-first-run</string>
        <string>--no-default-browser-check</string>
        <string>--disable-background-timer-throttling</string>
        <string>--disable-backgrounding-occluded-windows</string>
        <string>--disable-renderer-backgrounding</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <dict>
        <key>Crashed</key>
        <true/>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/chrome-cdp.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/chrome-cdp.err</string>
</dict>
</plist>
PLIST
    launchctl unload "$PLIST_PATH" 2>/dev/null || true
    launchctl load "$PLIST_PATH" 2>/dev/null || true
    echo "✅ LaunchAgent created (auto-starts on login, restarts on crash)"
fi

# 8. Print summary
VERSION=$(curl -s "http://127.0.0.1:$CDP_PORT/json/version" | python3 -c "import sys,json; print(json.load(sys.stdin).get('Browser','unknown'))" 2>/dev/null)
echo ""
echo "═══════════════════════════════════════════════════"
echo "  ✅ Chrome CDP ready!"
echo "  Browser: $VERSION"
echo "  CDP URL: http://127.0.0.1:$CDP_PORT"
echo "  Profile: $PROFILE_DIR"
echo ""
echo "  Use in OpenClaw: profile=\"openclaw\""
echo "  NOT: profile=\"chrome\" (that's the old relay)"
echo "═══════════════════════════════════════════════════"
echo ""
echo "💡 First time? Log into your accounts in the CDP"
echo "   Chrome window (it's the one without your extensions)."
