#!/bin/bash
#
# Telnyx Network - Teardown
# Removes all resources
#
# Usage: ./teardown.sh [--yes]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.json"
API_BASE="https://api.telnyx.com/v2"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SKIP_CONFIRM=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --yes|-y) SKIP_CONFIRM=true; shift ;;
        *) shift ;;
    esac
done

if [ ! -f "$CONFIG_FILE" ]; then
    echo "No config found. Nothing to tear down."
    exit 0
fi

if [ -z "$TELNYX_API_KEY" ]; then
    if [ -f "$SCRIPT_DIR/.env" ]; then
        source "$SCRIPT_DIR/.env"
    fi
fi

if [ -z "$TELNYX_API_KEY" ]; then
    echo -e "${RED}Error: TELNYX_API_KEY not set${NC}"
    exit 1
fi

# Show what will be deleted
echo ""
echo -e "${YELLOW}⚠️  This will delete:${NC}"
echo ""
python3 << EOF
import json
with open('$CONFIG_FILE') as f:
    c = json.load(f)
print(f"  Network:          {c['network_name']}")
print(f"  WireGuard Gateway: {c['wireguard_gateway']['id'][:8]}...")
if c.get('internet_gateway'):
    print(f"  Internet Gateway:  {c['internet_gateway']['id'][:8]}...")
    print(f"  Public IP:         {c['internet_gateway']['public_ip']}")
print(f"  Peers:             {len(c.get('peers', []))}")
EOF
echo ""

if [ "$SKIP_CONFIRM" = false ]; then
    read -p "Are you sure? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

echo ""
echo "Tearing down..."

# Disconnect local WireGuard
for conf in "$SCRIPT_DIR"/wg-*.conf; do
    if [ -f "$conf" ]; then
        echo -n "Disconnecting $(basename "$conf")... "
        sudo wg-quick down "$conf" 2>/dev/null || true
        echo "done"
    fi
done

# Delete Internet Gateway
IGW_ID=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c.get('internet_gateway',{}).get('id',''))" 2>/dev/null)
if [ -n "$IGW_ID" ]; then
    echo -n "Deleting Internet Gateway... "
    curl -s -X DELETE "$API_BASE/public_internet_gateways/$IGW_ID" \
        -H "Authorization: Bearer $TELNYX_API_KEY" > /dev/null
    echo "done"
fi

# Delete peers
PEER_IDS=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(' '.join([p['id'] for p in c.get('peers',[])]))" 2>/dev/null)
for PEER_ID in $PEER_IDS; do
    echo -n "Deleting peer $PEER_ID... "
    curl -s -X DELETE "$API_BASE/wireguard_peers/$PEER_ID" \
        -H "Authorization: Bearer $TELNYX_API_KEY" > /dev/null
    echo "done"
done

# Delete WireGuard Gateway
WG_ID=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c['wireguard_gateway']['id'])")
echo -n "Deleting WireGuard Gateway... "
curl -s -X DELETE "$API_BASE/wireguard_interfaces/$WG_ID" \
    -H "Authorization: Bearer $TELNYX_API_KEY" > /dev/null
echo "done"

# Delete Network
NETWORK_ID=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c['network_id'])")
echo -n "Deleting Network... "
curl -s -X DELETE "$API_BASE/networks/$NETWORK_ID" \
    -H "Authorization: Bearer $TELNYX_API_KEY" > /dev/null
echo "done"

# Clean up local files
rm -f "$SCRIPT_DIR"/wg-*.conf
rm -f "$CONFIG_FILE"

echo ""
echo -e "${GREEN}✅ Teardown complete${NC}"
