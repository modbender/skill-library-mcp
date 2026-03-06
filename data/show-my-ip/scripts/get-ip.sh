#!/usr/bin/env bash
# Get public IP address(es)

echo "=== Public IP ==="

ipv4=$(curl -4 -s --max-time 5 https://ifconfig.me 2>/dev/null)
if [ -n "$ipv4" ]; then
  echo "IPv4: $ipv4"
else
  echo "IPv4: unavailable"
fi

ipv6=$(curl -6 -s --max-time 5 https://ifconfig.me 2>/dev/null)
if [ -n "$ipv6" ]; then
  echo "IPv6: $ipv6"
fi
