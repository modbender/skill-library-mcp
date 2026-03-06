#!/bin/bash
# Hostinger VPS Optimizer
echo "Applying Hostinger optimizations..."
sysctl -w vm.swappiness=10
sysctl -w net.core.somaxconn=65535
apt update && apt install -y nginx ufw fail2ban
ufw allow ssh && ufw --force enable
echo "Optimized! Reboot recommended."
