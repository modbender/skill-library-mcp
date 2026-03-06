#!/bin/bash
# Setup WireGuard VPN Server
# Usage: ./setup-wireguard.sh [CLIENT_NAME]
# Run as root

set -e

CLIENT_NAME="${1:-client1}"
WG_PORT=51820

echo "🔐 Setting up WireGuard VPN"
echo "==========================="

# Install WireGuard
echo "[1/5] Installing WireGuard..."
apt-get update
apt-get install -y wireguard qrencode

# Generate server keys
echo "[2/5] Generating keys..."
cd /etc/wireguard
umask 077

wg genkey | tee server_private.key | wg pubkey > server_public.key
wg genkey | tee ${CLIENT_NAME}_private.key | wg pubkey > ${CLIENT_NAME}_public.key

SERVER_PRIVATE=$(cat server_private.key)
SERVER_PUBLIC=$(cat server_public.key)
CLIENT_PRIVATE=$(cat ${CLIENT_NAME}_private.key)
CLIENT_PUBLIC=$(cat ${CLIENT_NAME}_public.key)

# Get server public IP
SERVER_IP=$(curl -s ifconfig.me)

# Create server config
echo "[3/5] Creating server configuration..."
cat > /etc/wireguard/wg0.conf << EOF
[Interface]
Address = 10.200.200.1/24
ListenPort = $WG_PORT
PrivateKey = $SERVER_PRIVATE
PostUp = iptables -A FORWARD -i wg0 -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i wg0 -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
# $CLIENT_NAME
PublicKey = $CLIENT_PUBLIC
AllowedIPs = 10.200.200.2/32
EOF

# Create client config
echo "[4/5] Creating client configuration..."
cat > /etc/wireguard/${CLIENT_NAME}.conf << EOF
[Interface]
PrivateKey = $CLIENT_PRIVATE
Address = 10.200.200.2/24
DNS = 1.1.1.1

[Peer]
PublicKey = $SERVER_PUBLIC
AllowedIPs = 10.200.200.0/24
Endpoint = $SERVER_IP:$WG_PORT
PersistentKeepalive = 25
EOF

# Enable IP forwarding
echo "net.ipv4.ip_forward=1" >> /etc/sysctl.conf
sysctl -p

# Configure firewall
echo "[5/5] Configuring firewall..."
ufw allow $WG_PORT/udp

# Start WireGuard
systemctl enable wg-quick@wg0
systemctl start wg-quick@wg0

echo ""
echo "✅ WireGuard VPN configured!"
echo ""
echo "Server public key: $SERVER_PUBLIC"
echo ""
echo "Client config saved to: /etc/wireguard/${CLIENT_NAME}.conf"
echo ""
echo "QR code for mobile:"
qrencode -t ansiutf8 < /etc/wireguard/${CLIENT_NAME}.conf
echo ""
echo "Via VPN, access Koda at: http://10.200.200.1:18789"
echo ""
echo "To add more clients, run:"
echo "  ./setup-wireguard.sh client2"
