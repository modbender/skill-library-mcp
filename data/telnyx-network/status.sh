#!/bin/bash
#
# Telnyx Network - Status
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.json"
API_BASE="https://api.telnyx.com/v2"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: No config found. Run ./setup.sh first"
    exit 1
fi

if [ -z "$TELNYX_API_KEY" ]; then
    if [ -f "$SCRIPT_DIR/.env" ]; then
        source "$SCRIPT_DIR/.env"
    fi
fi

echo ""
echo "📊 Telnyx Network Status"
echo "========================"
echo ""

# Parse config
python3 << EOF
import json

with open('$CONFIG_FILE') as f:
    c = json.load(f)

print(f"Network:    {c['network_name']} ({c['network_id'][:8]}...)")
print(f"Region:     {c['region']}")
print()

wg = c['wireguard_gateway']
print("WireGuard Gateway:")
print(f"  Endpoint: {wg['endpoint']}")
print(f"  Subnet:   {wg['subnet']}")
print()

igw = c.get('internet_gateway')
if igw:
    print("Internet Gateway:")
    print(f"  Public IP: {igw['public_ip']}")
    print()
else:
    print("Internet Gateway: Not configured")
    print("  (Run ./add-public-ip.sh to get a public IP)")
    print()

peers = c.get('peers', [])
print(f"Peers: {len(peers)}")
for p in peers:
    print(f"  - {p['name']}: {p['ip']}")
print()

exposed = c.get('exposed_ports', [])
if exposed:
    print(f"Exposed Ports: {', '.join(map(str, exposed))}")
else:
    print("Exposed Ports: None")
print()
EOF

# Check local WireGuard status
echo "Local WireGuard:"
if command -v wg &> /dev/null; then
    if sudo wg show 2>/dev/null | grep -q "interface"; then
        echo -e "  Status: ${GREEN}Connected${NC}"
        sudo wg show | grep -E "interface|endpoint|latest handshake" | sed 's/^/  /'
    else
        echo -e "  Status: ${YELLOW}Not connected${NC}"
        echo "  Run: sudo wg-quick up <config-file>"
    fi
else
    echo -e "  Status: ${RED}WireGuard not installed${NC}"
fi
echo ""
