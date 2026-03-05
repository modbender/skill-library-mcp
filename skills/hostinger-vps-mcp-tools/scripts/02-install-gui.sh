#!/bin/bash
# Install XFCE Desktop + XRDP for Remote Desktop Access
# Run as root

set -e

echo "🖥️  Installing GUI (XFCE + XRDP)"
echo "================================"

# Install XFCE desktop (lightweight)
echo "[1/4] Installing XFCE desktop environment..."
DEBIAN_FRONTEND=noninteractive apt-get install -y \
    xfce4 \
    xfce4-goodies \
    xfce4-terminal \
    dbus-x11 \
    x11-xserver-utils \
    firefox \
    --no-install-recommends

# Install XRDP (Windows Remote Desktop Protocol)
echo "[2/4] Installing XRDP..."
apt-get install -y xrdp

# Configure XRDP to use XFCE
echo "[3/4] Configuring XRDP for XFCE..."
cat > /etc/xrdp/startwm.sh << 'EOF'
#!/bin/sh
if [ -r /etc/default/locale ]; then
    . /etc/default/locale
    export LANG LANGUAGE
fi
exec startxfce4
EOF
chmod +x /etc/xrdp/startwm.sh

# Add xrdp user to ssl-cert group
usermod -a -G ssl-cert xrdp

# Configure XRDP settings for better performance
cat > /etc/xrdp/xrdp.ini.custom << 'EOF'
[Globals]
; Better color depth
max_bpp=24
; Enable compression
bulk_compression=true
EOF

# Enable and start XRDP
echo "[4/4] Starting XRDP service..."
systemctl enable xrdp
systemctl restart xrdp

# Create .xsession for koda user
if [ -d /home/koda ]; then
    echo "startxfce4" > /home/koda/.xsession
    chown koda:koda /home/koda/.xsession
fi

# Get server IP
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

echo ""
echo "✅ GUI installation complete!"
echo ""
echo "Connect via Remote Desktop (RDP):"
echo "  Address: $SERVER_IP:3389"
echo "  Username: koda"
echo "  Password: (the one you set)"
echo ""
echo "From Windows: Open 'Remote Desktop Connection' and enter the address"
echo "From Mac: Use 'Microsoft Remote Desktop' app"
echo "From Linux: Use 'Remmina' or 'rdesktop'"
echo ""
echo "Next: Run 03-install-docker.sh to install Docker"
