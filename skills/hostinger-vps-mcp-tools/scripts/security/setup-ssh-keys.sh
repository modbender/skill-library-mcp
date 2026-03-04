#!/bin/bash
# Configure SSH Key-Only Authentication
# Usage: ./setup-ssh-keys.sh "ssh-rsa AAAA... user@host"
# Run as root

set -e

PUBLIC_KEY="${1:?Usage: $0 \"ssh-rsa AAAA... user@host\"}"

echo "🔐 Setting up SSH Key Authentication"
echo "====================================="

# Add key to root
mkdir -p /root/.ssh
chmod 700 /root/.ssh
echo "$PUBLIC_KEY" >> /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys

# Add key to koda user
mkdir -p /home/koda/.ssh
chmod 700 /home/koda/.ssh
echo "$PUBLIC_KEY" >> /home/koda/.ssh/authorized_keys
chmod 600 /home/koda/.ssh/authorized_keys
chown -R koda:koda /home/koda/.ssh

# Disable password authentication
echo "[*] Disabling password authentication..."
sed -i 's/^#*PasswordAuthentication .*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#*ChallengeResponseAuthentication .*/ChallengeResponseAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#*UsePAM .*/UsePAM no/' /etc/ssh/sshd_config
sed -i 's/^#*PermitRootLogin .*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config

# Restart SSH
systemctl restart sshd

echo ""
echo "✅ SSH key authentication configured!"
echo ""
echo "⚠️  Password login is now DISABLED"
echo "⚠️  Make sure your key works before disconnecting!"
echo ""
echo "Test with: ssh -i ~/.ssh/your_key koda@SERVER_IP"
