#!/bin/bash
# Lock down public access - VPN/Tunnel only mode
# Run AFTER setting up Tailscale, WireGuard, or Cloudflare Tunnel
# Run as root

set -e

echo "🔒 Locking Down Public Access"
echo "=============================="
echo ""
echo "⚠️  WARNING: This will remove public access to Koda webchat!"
echo "⚠️  Make sure VPN/Tunnel is working before running this!"
echo ""
read -p "Continue? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "Aborted."
    exit 1
fi

# Remove Koda port from firewall
echo "[1/3] Removing Koda webchat from public firewall..."
ufw delete allow 18789/tcp 2>/dev/null || true

# Get all custom Koda ports from config
if [ -f /etc/koda/config ]; then
    source /etc/koda/config
    if [ -n "$KODA_PORT" ] && [ "$KODA_PORT" != "18789" ]; then
        ufw delete allow ${KODA_PORT}/tcp 2>/dev/null || true
    fi
fi

# Remove RDP from public (keep for Tailscale)
echo "[2/3] Removing RDP from public firewall..."
ufw delete allow 3389/tcp 2>/dev/null || true

# Update Docker to only listen on localhost/VPN
echo "[3/3] Reconfiguring Docker networking..."
KODA_DIR="/home/koda/koda"
if [ -f "$KODA_DIR/docker-compose.yml" ]; then
    # Backup original
    cp "$KODA_DIR/docker-compose.yml" "$KODA_DIR/docker-compose.yml.bak"
    
    # Update to localhost only (Tailscale/WireGuard will still work)
    sed -i 's/"[0-9]*:18789"/"127.0.0.1:18789:18789"/' "$KODA_DIR/docker-compose.yml"
    
    cd "$KODA_DIR"
    docker compose down
    docker compose up -d
fi

echo ""
echo "✅ Public access locked down!"
echo ""
echo "Koda is now ONLY accessible via:"
echo ""
if command -v tailscale &>/dev/null; then
    TS_IP=$(tailscale ip -4 2>/dev/null || echo "not connected")
    echo "  🔒 Tailscale: http://$TS_IP:18789"
fi
if [ -f /etc/wireguard/wg0.conf ]; then
    echo "  🔒 WireGuard: http://10.200.200.1:18789"
fi
echo "  🔒 Cloudflare Tunnel: (your configured domain)"
echo ""
echo "To restore public access:"
echo "  ufw allow 18789/tcp"
echo "  # And update docker-compose.yml ports"
