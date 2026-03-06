#!/bin/bash
# Setup Cloudflare Tunnel for secure HTTPS access
# Usage: ./setup-cloudflare-tunnel.sh TUNNEL_TOKEN
# Run as root

set -e

TUNNEL_TOKEN="${1:?Usage: $0 TUNNEL_TOKEN}"

echo "☁️  Setting up Cloudflare Tunnel"
echo "================================"

# Install cloudflared
echo "[1/3] Installing cloudflared..."
curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o /tmp/cloudflared.deb
dpkg -i /tmp/cloudflared.deb
rm /tmp/cloudflared.deb

# Install as service with token
echo "[2/3] Configuring tunnel..."
cloudflared service install "$TUNNEL_TOKEN"

# Enable and start
echo "[3/3] Starting tunnel..."
systemctl enable cloudflared
systemctl start cloudflared

echo ""
echo "✅ Cloudflare Tunnel configured!"
echo ""
echo "Your Koda instance is now accessible via your Cloudflare domain."
echo ""
echo "Benefits:"
echo "  • HTTPS encryption (free SSL)"
echo "  • No public ports needed (can remove 18789 from firewall)"
echo "  • DDoS protection"
echo "  • Zero Trust access policies (optional)"
echo ""
echo "To lock down further:"
echo "  ufw delete allow 18789/tcp"
echo ""
echo "Manage tunnel at: https://one.dash.cloudflare.com/"
