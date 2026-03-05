#!/bin/bash
# Uninstall LuLu Monitor service

set -e

INSTALL_DIR="$HOME/.openclaw/lulu-monitor"
PLIST_NAME="com.openclaw.lulu-monitor.plist"
LAUNCH_AGENTS="$HOME/Library/LaunchAgents"

echo "🗑️  Uninstalling LuLu Monitor..."
echo ""

# Stop service
echo "⏹️  Stopping service..."
launchctl unload "$LAUNCH_AGENTS/$PLIST_NAME" 2>/dev/null || true

# Remove launchd plist
if [ -f "$LAUNCH_AGENTS/$PLIST_NAME" ]; then
    rm "$LAUNCH_AGENTS/$PLIST_NAME"
    echo "✅ Removed launchd plist"
fi

# Ask before removing install directory
if [ -d "$INSTALL_DIR" ]; then
    echo ""
    read -p "Remove install directory ($INSTALL_DIR)? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$INSTALL_DIR"
        echo "✅ Removed install directory"
    else
        echo "⏭️  Kept install directory"
    fi
fi

echo ""
echo "✅ LuLu Monitor uninstalled!"
echo ""
echo "Note: LuLu Firewall itself was not modified."
