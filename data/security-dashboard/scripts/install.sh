#!/bin/bash
# Install Security Dashboard skill

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_NAME="security-dashboard.service"
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME"
DASHBOARD_USER="${DASHBOARD_USER:-openclaw-dashboard}"

echo "Installing Security Dashboard skill..."

# Ask user preference
read -p "Run as dedicated user '$DASHBOARD_USER' (recommended) or root? [user/root] (default: user): " RUN_AS
RUN_AS=${RUN_AS:-user}

if [ "$RUN_AS" = "user" ]; then
    # Create dedicated user if it doesn't exist
    if ! id "$DASHBOARD_USER" &>/dev/null; then
        echo "Creating dedicated user: $DASHBOARD_USER"
        useradd -r -s /bin/false -M -d /nonexistent "$DASHBOARD_USER"
    fi
    
    # Set ownership of skill directory
    chown -R "$DASHBOARD_USER:$DASHBOARD_USER" "$SKILL_DIR"
    
    # Create sudoers file for limited privileges
    SUDOERS_FILE="/etc/sudoers.d/openclaw-dashboard"
    cat > "$SUDOERS_FILE" << 'SUDOEOF'
# Allow openclaw-dashboard to check security status without password
Cmnd_Alias DASHBOARD_CMDS = /usr/bin/systemctl is-active *, \
                            /usr/bin/systemctl status *, \
                            /usr/bin/fail2ban-client status *, \
                            /usr/sbin/ufw status, \
                            /usr/bin/firewall-cmd --state, \
                            /usr/bin/journalctl *, \
                            /usr/bin/ss *, \
                            /usr/bin/tailscale status *

openclaw-dashboard ALL=(ALL) NOPASSWD: DASHBOARD_CMDS
SUDOEOF
    chmod 440 "$SUDOERS_FILE"
    
    SERVICE_USER="$DASHBOARD_USER"
    echo "✓ Created user: $DASHBOARD_USER with limited sudo privileges"
else
    SERVICE_USER="root"
    echo "⚠️  Running as root (not recommended for production)"
fi

# Create systemd service file
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=OpenClaw Security Dashboard
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$SKILL_DIR
ExecStart=/usr/bin/node $SKILL_DIR/server.js
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=security-dashboard

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$SKILL_DIR

[Install]
WantedBy=multi-user.target
EOF

echo "Created systemd service: $SERVICE_FILE"

# Update server.js to use sudo for privileged commands
if [ "$SERVICE_USER" != "root" ]; then
    echo "Note: Dashboard will use 'sudo' for security checks"
fi

# Reload systemd
systemctl daemon-reload

# Enable and start service
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

# Check status
sleep 2
if systemctl is-active --quiet $SERVICE_NAME; then
    echo ""
    echo "✅ Security Dashboard installed and running on port 18791"
    echo ""
    echo "User: $SERVICE_USER"
    echo "Security: Localhost-only binding (127.0.0.1)"
    echo ""
    echo "Access via:"
    echo "  ssh -L 18791:localhost:18791 root@YOUR_SERVER_IP"
    echo "  Then visit: http://localhost:18791"
    echo ""
    echo "Manage service:"
    echo "  sudo systemctl status $SERVICE_NAME"
    echo "  sudo systemctl restart $SERVICE_NAME"
    echo "  sudo systemctl stop $SERVICE_NAME"
else
    echo ""
    echo "❌ Installation failed. Check logs:"
    echo "  sudo journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi
