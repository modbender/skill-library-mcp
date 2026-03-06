#!/bin/bash
# Check network security context

echo "{"

# Check for VPN interfaces
vpn_detected="false"
vpn_type="none"

if ip link 2>/dev/null | grep -qE "wg[0-9]"; then
    vpn_detected="true"
    vpn_type="wireguard"
elif ip link 2>/dev/null | grep -q "tailscale"; then
    vpn_detected="true"
    vpn_type="tailscale"
elif ip link 2>/dev/null | grep -qE "tun[0-9]"; then
    vpn_detected="true"
    vpn_type="openvpn"
fi

echo '  "vpn_detected": '"$vpn_detected"','
echo '  "vpn_type": "'"$vpn_type"'",'

# Check Tailscale status
if command -v tailscale &>/dev/null; then
    ts_status=$(tailscale status --json 2>/dev/null | jq -r '.BackendState // "unknown"' 2>/dev/null || echo "not_running")
    echo '  "tailscale_status": "'"$ts_status"'",'
else
    echo '  "tailscale_status": "not_installed",'
fi

# Check WireGuard status
if command -v wg &>/dev/null; then
    wg_active=$(wg show 2>/dev/null | grep -c "interface:" || echo "0")
    echo '  "wireguard_interfaces": '"$wg_active"','
else
    echo '  "wireguard_interfaces": 0,'
fi

# Check if gateway port is listening
gateway_port=$(grep -o '"port": [0-9]*' ~/.openclaw/openclaw.json 2>/dev/null | head -1 | grep -o '[0-9]*' || echo "18789")
listening=$(ss -tlnp 2>/dev/null | grep ":$gateway_port " | head -1)
if [ -n "$listening" ]; then
    bind_addr=$(echo "$listening" | awk '{print $4}' | cut -d: -f1)
    echo '  "gateway_listening": true,'
    echo '  "gateway_bind_address": "'"$bind_addr"'",'
else
    echo '  "gateway_listening": false,'
    echo '  "gateway_bind_address": null,'
fi

# Check firewall status
if command -v ufw &>/dev/null; then
    ufw_status=$(sudo ufw status 2>/dev/null | head -1 | awk '{print $2}' || echo "unknown")
    echo '  "firewall": "ufw",'
    echo '  "firewall_status": "'"$ufw_status"'"'
elif command -v firewall-cmd &>/dev/null; then
    fw_status=$(sudo firewall-cmd --state 2>/dev/null || echo "unknown")
    echo '  "firewall": "firewalld",'
    echo '  "firewall_status": "'"$fw_status"'"'
else
    echo '  "firewall": "unknown",'
    echo '  "firewall_status": "unknown"'
fi

echo "}"
