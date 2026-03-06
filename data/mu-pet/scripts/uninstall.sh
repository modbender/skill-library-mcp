#!/bin/bash
# Uninstall desktop-pet
set -e
PLIST="$HOME/Library/LaunchAgents/ai.openclaw.desktop-pet.plist"
APP_DEST="$HOME/.openclaw/desktop-pet"

echo "🦞 Uninstalling Desktop Pet..."
launchctl unload "$PLIST" 2>/dev/null || true
rm -f "$PLIST"
pkill -f "desktop-pet/node_modules/electron" 2>/dev/null || true
rm -rf "$APP_DEST"
echo "🦞 Desktop Pet removed. Goodbye!"
