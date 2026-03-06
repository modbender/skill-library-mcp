#!/usr/bin/env bash
# Setup LAN Media Server as a systemd user service
set -euo pipefail

PORT="${MEDIA_PORT:-18801}"
MEDIA_ROOT="${MEDIA_ROOT:-$HOME/projects/shared-media}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SERVER_SCRIPT="$SKILL_DIR/scripts/server.js"
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="$SERVICE_DIR/media-server.service"

# Detect node
NODE_BIN="$(command -v node 2>/dev/null || echo '/usr/bin/node')"
if [[ ! -x "$NODE_BIN" ]]; then
  echo "❌ Node.js not found. Install it first." >&2
  exit 1
fi

# Create shared media directory
mkdir -p "$MEDIA_ROOT"
echo "📁 Media directory: $MEDIA_ROOT"

# Create systemd user service
mkdir -p "$SERVICE_DIR"
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=LAN Media Server (port $PORT)
After=network.target

[Service]
ExecStart=$NODE_BIN $SERVER_SCRIPT
Restart=always
RestartSec=3
Environment=NODE_ENV=production
Environment="MEDIA_PORT=$PORT"
Environment="MEDIA_ROOT=$MEDIA_ROOT"

[Install]
WantedBy=default.target
EOF

echo "📝 Created service: $SERVICE_FILE"

# Enable and start
systemctl --user daemon-reload
systemctl --user enable media-server.service
systemctl --user restart media-server.service

echo ""
echo "✅ LAN Media Server running!"
echo "   Port: $PORT"
echo "   Directory: $MEDIA_ROOT"

# Detect LAN IP
LAN_IP=$(hostname -I 2>/dev/null | awk '{print $1}' || echo "localhost")
echo "   URL: http://$LAN_IP:$PORT/"
echo ""
echo "💡 Drop files into $MEDIA_ROOT and share links like:"
echo "   http://$LAN_IP:$PORT/my-screenshot.jpg"

# Check lingering (needed for services to survive logout)
if ! loginctl show-user "$(whoami)" 2>/dev/null | grep -q 'Linger=yes'; then
  echo ""
  echo "⚠️  User lingering not enabled. Run this to survive reboots:"
  echo "   sudo loginctl enable-linger $(whoami)"
fi
