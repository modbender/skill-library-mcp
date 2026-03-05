#!/bin/bash
#
# Glitch Dashboard macOS Installer
#

set -e

REPO_URL="https://github.com/chris6970barbarian-hue/glitch-skills"
INSTALL_DIR="/usr/local/lib/glitch-dashboard"

echo "=== Glitch Dashboard macOS Installer ==="
echo ""

# Check for Homebrew
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install Node.js if needed
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    brew install node
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "Upgrading Node.js..."
    brew upgrade node
fi

echo "Node.js: $(node -v)"

# Create directories
echo "Creating directories..."
sudo mkdir -p "$INSTALL_DIR"
mkdir -p "$HOME/.glitch-dashboard"

# Download
echo "Downloading Glitch Dashboard..."
cd /tmp
rm -rf glitch-skills 2>/dev/null || true
git clone --depth 1 "$REPO_URL" glitch-skills
sudo cp -r glitch-skills/dashboard/* "$INSTALL_DIR/"

# Create LaunchAgent plist
echo "Creating LaunchAgent..."
PLIST_PATH="$HOME/Library/LaunchAgents/com.glitch.dashboard.plist"

cat > "$PLIST_PATH" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.glitch.dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/node</string>
        <string>$INSTALL_DIR/main.js</string>
    </array>
    <key>WorkingDirectory</key>
    <string>$INSTALL_DIR</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$HOME/.glitch-dashboard/output.log</string>
    <key>StandardErrorPath</key>
    <string>$HOME/.glitch-dashboard/error.log</string>
</dict>
</plist>
EOF

# Install ZeroTier if needed
if ! command -v zerotier-cli &> /dev/null; then
    echo "Installing ZeroTier..."
    brew install --cask zerotier-one
    open -a "ZeroTier One"
fi

# Load service
launchctl load "$PLIST_PATH"

# Create CLI
echo "Creating CLI shortcut..."
sudo tee /usr/local/bin/glitch-dashboard > /dev/null <<'EOF'
#!/bin/bash
PLIST="$HOME/Library/LaunchAgents/com.glitch.dashboard.plist"

case "$1" in
    start)
        launchctl load "$PLIST"
        echo "Started"
        ;;
    stop)
        launchctl unload "$PLIST"
        echo "Stopped"
        ;;
    restart)
        launchctl unload "$PLIST" 2>/dev/null
        launchctl load "$PLIST"
        echo "Restarted"
        ;;
    status)
        launchctl list | grep com.glitch.dashboard || echo "Not running"
        ;;
    logs)
        tail -f "$HOME/.glitch-dashboard/output.log"
        ;;
    *)
        echo "Usage: glitch-dashboard {start|stop|restart|status|logs}"
        ;;
esac
EOF
sudo chmod +x /usr/local/bin/glitch-dashboard

echo ""
echo "=== Installation Complete ==="
echo "Dashboard URL: http://localhost:3853"
echo ""
echo "Commands:"
echo "  glitch-dashboard start    - Start service"
echo "  glitch-dashboard stop     - Stop service"
echo "  glitch-dashboard logs     - View logs"
echo ""
