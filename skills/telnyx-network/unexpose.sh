#!/bin/bash
#
# Telnyx Network - Unexpose Ports
#
# Usage: ./unexpose.sh <port> [port2...]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.json"

GREEN='\033[0;32m'
NC='\033[0m'

PORTS=()

while [[ $# -gt 0 ]]; do
    if [[ $1 =~ ^[0-9]+$ ]]; then
        PORTS+=("$1")
    fi
    shift
done

if [ ${#PORTS[@]} -eq 0 ]; then
    echo "Usage: ./unexpose.sh <port> [port2...]"
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: No config found"
    exit 1
fi

# Detect WireGuard interface
WG_IFACE=$(sudo wg show 2>/dev/null | grep "interface:" | awk '{print $2}' | head -1)
if [ -z "$WG_IFACE" ]; then
    WG_IFACE="wg0"
fi

echo ""
echo "Closing ports: ${PORTS[*]}"
echo ""

for PORT in "${PORTS[@]}"; do
    echo -n "Closing port $PORT... "
    if sudo iptables -D INPUT -i "$WG_IFACE" -p tcp --dport "$PORT" -j ACCEPT 2>/dev/null; then
        echo -e "${GREEN}OK${NC}"
    else
        echo "not found"
    fi
done

# Update config
python3 << EOF
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)
existing = set(config.get('exposed_ports', []))
to_remove = set([int(p) for p in "${PORTS[*]}".split()])
config['exposed_ports'] = sorted(list(existing - to_remove))
with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
EOF

echo ""
echo -e "${GREEN}✅ Ports closed${NC}"
