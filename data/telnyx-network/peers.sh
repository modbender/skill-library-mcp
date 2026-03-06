#!/bin/bash
#
# Telnyx Network - List Peers
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.json"
API_BASE="https://api.telnyx.com/v2"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: No config found. Run ./setup.sh first"
    exit 1
fi

if [ -z "$TELNYX_API_KEY" ]; then
    if [ -f "$SCRIPT_DIR/.env" ]; then
        source "$SCRIPT_DIR/.env"
    fi
fi

WG_ID=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c['wireguard_gateway']['id'])")

echo ""
echo "🔗 Telnyx Network Peers"
echo "======================="
echo ""

# Fetch live peer data
PEERS=$(curl -s "$API_BASE/wireguard_peers?filter[wireguard_interface_id]=$WG_ID" \
    -H "Authorization: Bearer $TELNYX_API_KEY")

echo "$PEERS" | python3 << 'EOF'
import sys, json
from datetime import datetime

data = json.load(sys.stdin)
peers = data.get('data', [])

if not peers:
    print("No peers found.")
    print("")
    print("Add one with: ./join.sh --name my-machine")
else:
    print(f"{'NAME':<20} {'IP':<18} {'STATUS':<10} {'LAST SEEN'}")
    print("-" * 70)
    for p in peers:
        name = p.get('name', 'unknown')[:20]
        # Get peer IP from config endpoint
        last_seen = p.get('last_seen')
        if last_seen:
            status = "online"
            seen = last_seen[:19].replace('T', ' ')
        else:
            status = "never"
            seen = "-"
        # IP would need separate lookup, show placeholder
        print(f"{name:<20} {'(see config)':<18} {status:<10} {seen}")
EOF

echo ""
