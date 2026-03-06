#!/bin/bash
# VPS Healthcheck Script
HOST=$1
USER=$2
KEY=$3

ssh -i $KEY -o StrictHostKeyChecking=no $USER@$HOST << EOF
echo "=== CPU ==="
top -bn1 | head -20
echo "=== Memory ==="
free -h
echo "=== Disk ==="
df -h
echo "=== Network ==="
ifconfig || ip addr
echo "=== Uptime ==="
uptime
echo "=== Services ==="
systemctl status ssh nginx mysql --no-pager || service --status-all | head -20
EOF
