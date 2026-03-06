#!/bin/bash
# Install desktop-pet: copies app to ~/.openclaw/desktop-pet, installs deps, sets up LaunchAgent
set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
APP_SRC="$SKILL_DIR/assets/app"
APP_DEST="$HOME/.openclaw/desktop-pet"
PLIST="$HOME/Library/LaunchAgents/ai.openclaw.desktop-pet.plist"

echo "🦞 Installing Desktop Pet..."

# Copy app
mkdir -p "$APP_DEST"
cp "$APP_SRC/package.json" "$APP_DEST/"
cp "$APP_SRC/main.js" "$APP_DEST/"
cp "$APP_SRC/index.html" "$APP_DEST/"

# Install deps
cd "$APP_DEST"
npm install --production 2>&1 | tail -3

# Create LaunchAgent
cat > "$PLIST" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>ai.openclaw.desktop-pet</string>
  <key>ProgramArguments</key><array>
    <string>$APP_DEST/node_modules/.bin/electron</string>
    <string>$APP_DEST</string>
  </array>
  <key>WorkingDirectory</key><string>$APP_DEST</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><true/>
  <key>StandardOutPath</key><string>/tmp/desktop-pet.log</string>
  <key>StandardErrorPath</key><string>/tmp/desktop-pet.log</string>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
  </dict>
</dict></plist>
EOF

# Load it
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"

echo "🦞 Desktop Pet installed and running!"
echo "   App: $APP_DEST"
echo "   API: http://127.0.0.1:18891"
echo "   Log: /tmp/desktop-pet.log"
