#!/bin/bash
#
# Glitch Dashboard Linux Installer
# Supports: Ubuntu, Debian, CentOS, RHEL, Arch
#

set -e

REPO_URL="https://github.com/chris6970barbarian-hue/glitch-skills"
INSTALL_DIR="/opt/glitch-dashboard"
USER="${SUDO_USER:-$USER}"

echo "=== Glitch Dashboard Linux Installer ==="
echo ""

# Detect distro
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    DISTRO=$(uname -s)
fi

echo "Detected: $DISTRO"

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "Installing Node.js..."
    
    case $DISTRO in
        ubuntu|debian)
            curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
            apt-get install -y nodejs
            ;;
        centos|rhel|fedora)
            curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
            yum install -y nodejs
            ;;
        arch|manjaro)
            pacman -Sy --noconfirm nodejs npm
            ;;
        *)
            echo "Please install Node.js 18+ manually"
            exit 1
            ;;
    esac
fi

# Check Node version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "Error: Node.js 18+ required"
    exit 1
fi

echo "Node.js: $(node -v)"

# Create install directory
echo "Creating installation directory..."
sudo mkdir -p "$INSTALL_DIR"
sudo chown "$USER:$USER" "$INSTALL_DIR"

# Download dashboard
echo "Downloading Glitch Dashboard..."
cd /tmp
rm -rf glitch-skills 2>/dev/null || true
git clone --depth 1 "$REPO_URL" glitch-skills
cp -r glitch-skills/dashboard/* "$INSTALL_DIR/"

# Create config directory
mkdir -p "$HOME/.glitch-dashboard"

# Create systemd service
echo "Creating systemd service..."
sudo tee /etc/systemd/system/glitch-dashboard.service > /dev/null <<EOF
[Unit]
Description=Glitch Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/node main.js
Restart=always
RestartSec=10
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

# Install ZeroTier if not present
if ! command -v zerotier-cli &> /dev/null; then
    echo "Installing ZeroTier..."
    curl -s https://install.zerotier.com | sudo bash
fi

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable glitch-dashboard
sudo systemctl start glitch-dashboard

# Create CLI shortcut
sudo tee /usr/local/bin/glitch-dashboard > /dev/null <<EOF
#!/bin/bash
case "\$1" in
    start)
        sudo systemctl start glitch-dashboard
        ;;
    stop)
        sudo systemctl stop glitch-dashboard
        ;;
    restart)
        sudo systemctl restart glitch-dashboard
        ;;
    status)
        sudo systemctl status glitch-dashboard
        ;;
    logs)
        sudo journalctl -u glitch-dashboard -f
        ;;
    *)
        echo "Usage: glitch-dashboard {start|stop|restart|status|logs}"
        exit 1
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
