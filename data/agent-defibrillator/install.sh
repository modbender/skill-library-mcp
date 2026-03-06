#!/bin/bash
# ============================================================
#  🫀⚡ Agent Defibrillator - Installer
#  
#  Installs the watchdog script and launchd service.
#  Your agent will never flatline for long again!
# ============================================================

set -e

echo ""
echo "  🫀⚡ Agent Defibrillator Installer"
echo "  =================================="
echo ""

# Configuration
INSTALL_DIR="${HOME}/.openclaw/scripts"
PLIST_DIR="${HOME}/Library/LaunchAgents"
LOG_DIR="${HOME}/.openclaw/logs"
SCRIPT_NAME="defibrillator.sh"
PLIST_NAME="com.openclaw.defibrillator.plist"

# Default settings (can be overridden)
GATEWAY_LABEL="${1:-ai.openclaw.gateway}"
CHECK_INTERVAL="${2:-600}"  # 10 minutes default

echo "📋 Configuration:"
echo "   Gateway label: $GATEWAY_LABEL"
echo "   Check interval: ${CHECK_INTERVAL}s ($(( CHECK_INTERVAL / 60 )) min)"
echo ""

# Verify gateway exists
if ! launchctl list 2>/dev/null | grep -q "$GATEWAY_LABEL"; then
    echo "⚠️  Warning: Gateway '$GATEWAY_LABEL' not found in launchctl."
    echo "   Available OpenClaw services:"
    launchctl list 2>/dev/null | grep -i openclaw | awk '{print "   - " $3}'
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Create directories
mkdir -p "$INSTALL_DIR" "$LOG_DIR"

# Download or copy script
SCRIPT_URL="https://raw.githubusercontent.com/hazy2go/agent-defibrillator/main/defibrillator.sh"
echo "📥 Installing defibrillator script..."

if command -v curl &> /dev/null; then
    curl -fsSL "$SCRIPT_URL" -o "$INSTALL_DIR/$SCRIPT_NAME" 2>/dev/null || {
        # Fallback: copy from local if curl fails (for local installs)
        if [ -f "$(dirname "$0")/defibrillator.sh" ]; then
            cp "$(dirname "$0")/defibrillator.sh" "$INSTALL_DIR/$SCRIPT_NAME"
        else
            echo "❌ Failed to download script"
            exit 1
        fi
    }
else
    cp "$(dirname "$0")/defibrillator.sh" "$INSTALL_DIR/$SCRIPT_NAME"
fi

chmod +x "$INSTALL_DIR/$SCRIPT_NAME"
echo "✅ Script installed at $INSTALL_DIR/$SCRIPT_NAME"

# Create launchd plist
echo "📝 Creating launchd service..."
cat > "$PLIST_DIR/$PLIST_NAME" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.openclaw.defibrillator</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>${INSTALL_DIR}/${SCRIPT_NAME}</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>DEFIB_GATEWAY_LABEL</key>
        <string>${GATEWAY_LABEL}</string>
        <key>DEFIB_LOG_DIR</key>
        <string>${LOG_DIR}</string>
    </dict>
    <key>StartInterval</key>
    <integer>${CHECK_INTERVAL}</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>Nice</key>
    <integer>10</integer>
    <key>StandardOutPath</key>
    <string>${LOG_DIR}/defibrillator.log</string>
    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/defibrillator.log</string>
</dict>
</plist>
EOF
echo "✅ Launchd plist created"

# Load service
echo "🚀 Starting defibrillator service..."
launchctl bootout "gui/$(id -u)/com.openclaw.defibrillator" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DIR/$PLIST_NAME"

# Verify
if launchctl list 2>/dev/null | grep -q "defibrillator"; then
    echo "✅ Service is running!"
else
    echo "⚠️  Service may not have started. Check: launchctl list | grep defib"
fi

echo ""
echo "  🎉 Installation complete!"
echo ""
echo "  Your agent now has a defibrillator! If it flatlines,"
echo "  it will be shocked back to life within ~$(( CHECK_INTERVAL / 60 )) minutes."
echo ""
echo "  📊 Commands:"
echo "     View logs:    tail -f ~/.openclaw/logs/defibrillator.log"
echo "     Check status: launchctl list | grep defib"
echo "     Uninstall:    ~/.openclaw/scripts/defibrillator.sh --uninstall"
echo ""
echo "  🫀⚡ Stay alive out there!"
echo ""
