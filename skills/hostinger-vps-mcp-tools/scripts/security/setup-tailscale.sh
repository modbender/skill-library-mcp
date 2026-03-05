#!/bin/bash
# Install and Configure Tailscale VPN
# Usage: ./setup-tailscale.sh [AUTH_KEY]
# Run as root

set -e

AUTH_KEY="$1"

echo "🔒 Installing Tailscale VPN"
echo "==========================="

# Install Tailscale
echo "[1/3] Installing Tailscale..."
curl -fsSL https://tailscale.com/install.sh | sh

# Enable and start
echo "[2/3] Starting Tailscale..."
systemctl enable tailscaled
systemctl start tailscaled

# Authenticate
echo "[3/3] Authenticating..."
if [ -n "$AUTH_KEY" ]; then
    tailscale up --authkey="$AUTH_KEY" --ssh
else
    echo ""
    echo "Run this command to authenticate:"
    echo "  tailscale up --ssh"
    echo ""
    echo "Then visit the URL shown to authorize this device."
    tailscale up --ssh
fi

# Get Tailscale IP
sleep 3
TAILSCALE_IP=$(tailscale ip -4 2>/dev/null || echo "pending...")

echo ""
echo "✅ Tailscale installed!"
echo ""
echo "Tailscale IP: $TAILSCALE_IP"
echo ""
echo "Benefits:"
echo "  • Access Koda via private Tailscale IP (no public exposure)"
echo "  • SSH via Tailscale: ssh koda@$TAILSCALE_IP"
echo "  • Webchat via Tailscale: http://$TAILSCALE_IP:18789"
echo "  • End-to-end encrypted traffic"
echo ""
echo "Optional: Lock down public access"
echo "  ufw delete allow 18789/tcp  # Remove public webchat access"
echo "  # Now only accessible via Tailscale"
