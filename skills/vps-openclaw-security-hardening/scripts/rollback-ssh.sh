#!/bin/bash
# Emergency SSH Rollback Script - SAFE VERSION
# Usage: ./rollback-ssh.sh
# Only resets SSH port to 22, keeps key-only authentication

set -euo pipefail

RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${RED}╔════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║   EMERGENCY SSH PORT ROLLBACK (SAFE)           ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}WARNING:${NC} This will:"
echo "  1. Restore SSH to port 22"
echo "  2. KEEP key-only authentication (passwords stay disabled)"
echo "  3. KEEP root login disabled"
echo ""
echo "This is safer than full rollback but still reduces security."
echo ""

read -p "Are you sure? Type 'ROLLBACK' to confirm: " confirm
if [[ "$confirm" != "ROLLBACK" ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "Creating backup of current config..."
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.rollback.$(date +%s)

echo "Resetting SSH port to 22 (keeping key-only auth)..."

# Only remove Port setting, keep everything else
sed -i '/^Port /d' /etc/ssh/sshd_config

# Add Port 22
if ! grep -q "^Port 22" /etc/ssh/sshd_config; then
    echo "Port 22" >> /etc/ssh/sshd_config
fi

echo "Testing configuration..."
if /usr/sbin/sshd -t; then
    echo -e "${GREEN}✓ Config valid${NC}"
else
    echo -e "${RED}✗ Config test failed!${NC}"
    echo "Restoring from backup..."
    cp /etc/ssh/sshd_config.bak.* /etc/ssh/sshd_config 2>/dev/null || true
    exit 1
fi

echo "Restarting SSH..."
systemctl restart sshd

echo "Updating firewall..."
ufw allow 22/tcp comment 'SSH port rollback' || true

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   PORT ROLLBACK COMPLETE                       ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════╝${NC}"
echo ""
echo "SSH is now accessible on port 22."
echo "Key-only authentication is still REQUIRED."
echo ""
echo "Test with: ssh -p 22 root@your-server-ip"
echo ""
echo "To re-harden: SSH_PORT=your_port ./scripts/install.sh"
echo "Backup saved to: /etc/ssh/sshd_config.rollback.*"
