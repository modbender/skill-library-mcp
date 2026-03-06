#!/bin/bash
# SSH Batch Manager - Post Install Script
# Automatically configure and start Web UI service

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="ssh-batch-ui"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
USER=$(whoami)

echo "🔧 SSH Batch Manager - Post Installation"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Error: Do not run as root. This script will use sudo when needed."
    exit 1
fi

# Check if systemd is available
if ! command -v systemctl &> /dev/null; then
    echo "⚠️  Warning: systemctl not found. Skipping systemd service configuration."
    echo "You can manually start the Web UI with: python3 ${SKILL_DIR}/serve-ui.py"
    exit 0
fi

echo "📝 Configuring systemd service..."
echo ""

# Create service file
sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=SSH Batch Manager Web UI
Documentation=https://gitee.com/subline/onepeace/tree/develop/src/skills/ssh-batch-manager
After=network.target

[Service]
Type=simple
User=${USER}
Group=${USER}
WorkingDirectory=${SKILL_DIR}
ExecStart=/usr/bin/python3 ${SKILL_DIR}/serve-ui.py
Restart=on-failure
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=ssh-batch-ui

# Security settings
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created: ${SERVICE_FILE}"
echo ""

# Reload systemd
echo "🔄 Reloading systemd daemon..."
sudo systemctl daemon-reload

# Enable service (start on boot)
echo "⚙️  Enabling service (auto-start on boot)..."
sudo systemctl enable ${SERVICE_NAME}

# Start service
echo "🚀 Starting service..."
sudo systemctl start ${SERVICE_NAME}

# Wait for service to start
sleep 2

# Check status
echo ""
echo "📊 Service Status:"
sudo systemctl status ${SERVICE_NAME} --no-pager | head -10

echo ""
echo "========================================"
echo "✅ Installation Complete!"
echo ""
echo "🌐 Web UI is now running at:"
echo "   http://localhost:8765"
echo ""
echo "📋 Management Commands:"
echo "   sudo systemctl status ${SERVICE_NAME}    # Check status"
echo "   sudo systemctl stop ${SERVICE_NAME}      # Stop service"
echo "   sudo systemctl restart ${SERVICE_NAME}   # Restart service"
echo "   sudo systemctl disable ${SERVICE_NAME}   # Disable auto-start"
echo ""
echo "📖 Documentation:"
echo "   cat ${SKILL_DIR}/WEB-UI-GUIDE.md"
echo ""
