#!/bin/bash
# Quick installer for Scout Status Tidbyt integration

set -e

echo "🦅 Scout Status - Tidbyt Integration Installer"
echo "================================================"
echo

# Check if OpenClaw workspace exists
if [ ! -d "$HOME/.openclaw/workspace" ]; then
    echo "❌ Error: OpenClaw workspace not found at ~/.openclaw/workspace"
    exit 1
fi

SKILL_DIR="$HOME/.openclaw/workspace/skills/tidbyt-status"

# Check if skill already exists
if [ -d "$SKILL_DIR" ]; then
    echo "✅ Skill already installed at $SKILL_DIR"
else
    echo "❌ Skill not found. Please install the tidbyt-status skill first."
    exit 1
fi

echo
echo "Setup Options:"
echo "1. Start status API server (foreground)"
echo "2. Start status API server (background)"
echo "3. Install as systemd service (Linux)"
echo "4. Show network info (IP address)"
echo "5. Test API"
echo "6. Exit"
echo

read -p "Select option [1-6]: " choice

case $choice in
    1)
        echo "Starting status API server..."
        cd "$SKILL_DIR"
        python3 scripts/status_server.py
        ;;
    2)
        echo "Starting status API server in background..."
        cd "$SKILL_DIR"
        nohup python3 scripts/status_server.py > /tmp/scout-status.log 2>&1 &
        echo "✅ Server started. PID: $!"
        echo "   Logs: /tmp/scout-status.log"
        echo "   Stop with: kill $!"
        ;;
    3)
        if [ ! -f /bin/systemctl ]; then
            echo "❌ systemd not found. Use option 2 for manual background start."
            exit 1
        fi
        
        USERNAME=$(whoami)
        SERVICE_FILE="/tmp/scout-status.service"
        
        cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Scout Status API for Tidbyt
After=network.target

[Service]
Type=simple
User=$USERNAME
WorkingDirectory=$SKILL_DIR
ExecStart=/usr/bin/python3 scripts/status_server.py
Restart=always
Environment="PORT=8765"

[Install]
WantedBy=multi-user.target
EOF
        
        echo "Service file created at $SERVICE_FILE"
        echo
        echo "To install, run:"
        echo "  sudo cp $SERVICE_FILE /etc/systemd/system/"
        echo "  sudo systemctl daemon-reload"
        echo "  sudo systemctl enable scout-status"
        echo "  sudo systemctl start scout-status"
        ;;
    4)
        echo "Network Information:"
        echo "===================="
        IP=$(hostname -I 2>/dev/null | awk '{print $1}' || ifconfig | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | head -1)
        echo "Local IP: $IP"
        echo
        echo "Update scout_status.star line 10 with:"
        echo "DEFAULT_API_URL = \"http://$IP:8765/status\""
        ;;
    5)
        echo "Testing API..."
        curl -s http://localhost:8765/status | python3 -m json.tool || echo "❌ API not responding. Start the server first."
        ;;
    6)
        echo "Bye! 🦅"
        exit 0
        ;;
    *)
        echo "Invalid option"
        exit 1
        ;;
esac
