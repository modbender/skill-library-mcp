#!/bin/bash
# Comprehensive Server Security Hardening
# Run as root

set -e

echo "🛡️  Server Security Hardening"
echo "=============================="

# 1. SSH Hardening
echo "[1/8] Hardening SSH..."
cat >> /etc/ssh/sshd_config << 'EOF'

# Security Hardening
Protocol 2
MaxAuthTries 3
MaxSessions 3
LoginGraceTime 30
ClientAliveInterval 300
ClientAliveCountMax 2
X11Forwarding no
AllowAgentForwarding no
AllowTcpForwarding no
PermitEmptyPasswords no
EOF
systemctl restart sshd

# 2. Disable unused services
echo "[2/8] Disabling unused services..."
systemctl disable --now cups 2>/dev/null || true
systemctl disable --now avahi-daemon 2>/dev/null || true
systemctl disable --now bluetooth 2>/dev/null || true

# 3. Kernel hardening
echo "[3/8] Applying kernel hardening..."
cat > /etc/sysctl.d/99-security.conf << 'EOF'
# Disable IP forwarding (unless needed for VPN)
# net.ipv4.ip_forward = 0

# Disable ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0
net.ipv4.conf.all.send_redirects = 0
net.ipv4.conf.default.send_redirects = 0

# Enable SYN flood protection
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_max_syn_backlog = 2048
net.ipv4.tcp_synack_retries = 2

# Ignore ICMP broadcasts
net.ipv4.icmp_echo_ignore_broadcasts = 1

# Disable source routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0

# Log martian packets
net.ipv4.conf.all.log_martians = 1
net.ipv4.conf.default.log_martians = 1

# Ignore bogus ICMP errors
net.ipv4.icmp_ignore_bogus_error_responses = 1

# Enable reverse path filtering
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Disable IPv6 if not needed
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1
EOF
sysctl -p /etc/sysctl.d/99-security.conf

# 4. Install and configure auditd
echo "[4/8] Installing audit daemon..."
apt-get install -y auditd audispd-plugins
systemctl enable auditd
systemctl start auditd

# 5. Setup automatic security updates
echo "[5/8] Configuring automatic security updates..."
apt-get install -y unattended-upgrades
cat > /etc/apt/apt.conf.d/50unattended-upgrades << 'EOF'
Unattended-Upgrade::Allowed-Origins {
    "${distro_id}:${distro_codename}-security";
};
Unattended-Upgrade::AutoFixInterruptedDpkg "true";
Unattended-Upgrade::Remove-Unused-Dependencies "true";
Unattended-Upgrade::Automatic-Reboot "false";
EOF

cat > /etc/apt/apt.conf.d/20auto-upgrades << 'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
EOF

# 6. Configure logrotate
echo "[6/8] Configuring log rotation..."
cat > /etc/logrotate.d/koda << 'EOF'
/home/koda/koda/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 koda koda
}
EOF

# 7. Set file permissions
echo "[7/8] Setting secure file permissions..."
chmod 700 /root
chmod 700 /home/koda
chmod 600 /etc/ssh/sshd_config

# 8. Install rkhunter (rootkit hunter)
echo "[8/8] Installing rootkit hunter..."
apt-get install -y rkhunter
rkhunter --update
rkhunter --propupd

echo ""
echo "✅ Server hardening complete!"
echo ""
echo "Security measures applied:"
echo "  ✓ SSH hardened (max 3 attempts, timeouts)"
echo "  ✓ Kernel security parameters"
echo "  ✓ Audit logging enabled"
echo "  ✓ Automatic security updates"
echo "  ✓ Rootkit hunter installed"
echo ""
echo "Run periodic security checks:"
echo "  rkhunter --check        # Rootkit scan"
echo "  lynis audit system      # Full audit (install: apt install lynis)"
