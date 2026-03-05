#!/bin/bash
# CHAOS Memory - Systemd service setup script

set -e

CHAOS_HOME="${CHAOS_HOME:-$HOME/.chaos}"
SERVICE_NAME="chaos-consolidator.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "Setting up CHAOS Memory systemd service..."
echo ""

# Check if template exists
if [ ! -f "$CHAOS_HOME/config/chaos-consolidator.service.template" ]; then
    echo -e "${RED}Error: Service template not found at $CHAOS_HOME/config/chaos-consolidator.service.template${NC}"
    exit 1
fi

# Get user
USER=$(whoami)
HOME_PATH=$(eval echo ~)

# Create service file from template
echo "Creating service file..."
cat > "/tmp/$SERVICE_NAME" << EOF
[Unit]
Description=CHAOS Memory Auto-Capture Consolidator
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME_PATH/.chaos
ExecStart=$HOME_PATH/.chaos/bin/chaos-consolidator --config $HOME_PATH/.chaos/config/consolidator.yaml
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Environment
Environment="HOME=$HOME_PATH"
Environment="CHAOS_HOME=$HOME_PATH/.chaos"
Environment="PATH=$HOME_PATH/.chaos/bin:/usr/local/bin:/usr/bin:/bin"

[Install]
WantedBy=multi-user.target
EOF

# Install service
echo "Installing service (requires sudo)..."
sudo cp "/tmp/$SERVICE_NAME" "$SERVICE_FILE"
sudo systemctl daemon-reload

echo ""
echo -e "${GREEN}✓ Service installed${NC}"
echo ""
echo "Next steps:"
echo "  1. Review the service file: sudo nano $SERVICE_FILE"
echo "  2. Enable service: sudo systemctl enable $SERVICE_NAME"
echo "  3. Start service: sudo systemctl start $SERVICE_NAME"
echo "  4. Check status: sudo systemctl status $SERVICE_NAME"
echo "  5. View logs: sudo journalctl -u $SERVICE_NAME -f"
echo ""
