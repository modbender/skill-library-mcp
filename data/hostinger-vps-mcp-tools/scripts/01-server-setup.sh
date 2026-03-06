#!/bin/bash
# Hostinger VPS Initial Setup
# Usage: ./01-server-setup.sh [KODA_PORT] [SSH_PORT]
# Run as root on fresh Ubuntu 22.04/24.04

set -e

KODA_PORT="${1:-18789}"
SSH_PORT="${2:-22}"

echo "🔧 Hostinger VPS Initial Setup"
echo "=============================="
echo "Koda Port: $KODA_PORT"
echo "SSH Port:  $SSH_PORT"
echo ""

# Update system
echo "[1/6] Updating system..."
apt-get update && apt-get upgrade -y

# Install essentials
echo "[2/6] Installing essential packages..."
apt-get install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    ufw \
    fail2ban

# Create koda user
echo "[3/6] Creating 'koda' user..."
if ! id "koda" &>/dev/null; then
    useradd -m -s /bin/bash -G sudo koda
    # Generate random password
    KODA_PASS=$(openssl rand -base64 12)
    echo "koda:$KODA_PASS" | chpasswd
    echo ""
    echo "⚠️  Generated password for 'koda' user: $KODA_PASS"
    echo "⚠️  Save this! Change with: passwd koda"
    echo ""
fi

# Allow koda user to sudo without password (for automation)
echo "koda ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/koda

# Change SSH port if non-default
if [ "$SSH_PORT" != "22" ]; then
    echo "[4/6] Changing SSH port to $SSH_PORT..."
    sed -i "s/^#*Port .*/Port $SSH_PORT/" /etc/ssh/sshd_config
    systemctl restart sshd
else
    echo "[4/6] Keeping default SSH port 22..."
fi

# Configure firewall
echo "[5/6] Configuring firewall..."
ufw default deny incoming
ufw default allow outgoing
ufw allow $SSH_PORT/tcp   # SSH
ufw allow 3389/tcp        # XRDP
ufw allow $KODA_PORT/tcp  # Koda webchat
ufw --force enable

echo "Firewall rules:"
ufw status numbered

# Configure fail2ban
echo "[6/6] Configuring fail2ban..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port = $SSH_PORT
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# Save config for other scripts
mkdir -p /etc/koda
echo "KODA_PORT=$KODA_PORT" > /etc/koda/config
echo "SSH_PORT=$SSH_PORT" >> /etc/koda/config

echo ""
echo "✅ Server setup complete!"
echo ""
echo "Ports configured:"
echo "  SSH:  $SSH_PORT"
echo "  RDP:  3389"
echo "  Koda: $KODA_PORT"
echo ""
echo "Next: Run 02-install-gui.sh to install desktop environment"
