#!/bin/bash
#
# Telnyx Network - Join
# Add this machine to the mesh network
#
# Usage: ./join.sh --name my-machine [--apply]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.json"
API_BASE="https://api.telnyx.com/v2"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Defaults
NAME=""
APPLY=false

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --name) NAME="$2"; shift 2 ;;
        --apply) APPLY=true; shift ;;
        -h|--help)
            echo "Usage: ./join.sh --name <peer-name> [--apply]"
            echo ""
            echo "Options:"
            echo "  --name     Name for this peer (required)"
            echo "  --apply    Automatically apply WireGuard config"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Check config exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "${RED}Error: No config found. Run ./setup.sh first${NC}"
    exit 1
fi

# Check API key
if [ -z "$TELNYX_API_KEY" ]; then
    if [ -f "$SCRIPT_DIR/.env" ]; then
        source "$SCRIPT_DIR/.env"
    fi
fi

if [ -z "$TELNYX_API_KEY" ]; then
    echo -e "${RED}Error: TELNYX_API_KEY not set${NC}"
    exit 1
fi

# Check name
if [ -z "$NAME" ]; then
    echo -e "${RED}Error: --name required${NC}"
    echo "Example: ./join.sh --name my-laptop"
    exit 1
fi

# Load config
WG_ID=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c['wireguard_gateway']['id'])")
WG_ENDPOINT=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c['wireguard_gateway']['endpoint'])")
WG_PUBKEY=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c['wireguard_gateway']['public_key'])")
WG_SUBNET=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c['wireguard_gateway']['subnet'].split('/')[0].rsplit('.', 1)[0])")

echo ""
echo -e "${GREEN}🔗 Joining Telnyx Network${NC}"
echo "=========================="
echo ""
echo "Peer name: $NAME"
echo ""

# Create peer
echo -n "Creating peer... "
PEER_RESP=$(curl -s -X POST "$API_BASE/wireguard_peers" \
    -H "Authorization: Bearer $TELNYX_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$NAME\", \"wireguard_interface_id\": \"$WG_ID\"}")

PEER_ID=$(echo "$PEER_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('id',''))" 2>/dev/null)
PEER_PRIVKEY=$(echo "$PEER_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('private_key',''))" 2>/dev/null)
PEER_PUBKEY=$(echo "$PEER_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('public_key',''))" 2>/dev/null)

if [ -z "$PEER_ID" ]; then
    echo -e "${RED}FAILED${NC}"
    echo "$PEER_RESP"
    exit 1
fi
echo -e "${GREEN}OK${NC}"

# Get config from API
echo -n "Fetching WireGuard config... "
CONF_RESP=$(curl -s "$API_BASE/wireguard_peers/$PEER_ID/config" \
    -H "Authorization: Bearer $TELNYX_API_KEY")

# The config needs the private key inserted
CONF_FILE="$SCRIPT_DIR/wg-$NAME.conf"
# Use awk instead of sed for macOS compatibility (private key may contain special chars)
echo "$CONF_RESP" | awk -v key="$PEER_PRIVKEY" '/^PrivateKey =/{print "PrivateKey = " key; next} {print}' > "$CONF_FILE"
echo -e "${GREEN}OK${NC}"

# Extract assigned IP
PEER_IP=$(grep "Address" "$CONF_FILE" | cut -d'=' -f2 | tr -d ' ')

# Update config.json with new peer
python3 << EOF
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)
config['peers'].append({
    'id': '$PEER_ID',
    'name': '$NAME',
    'ip': '$PEER_IP',
    'public_key': '$PEER_PUBKEY'
})
with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
EOF

echo ""
echo -e "${GREEN}✅ Peer created!${NC}"
echo ""
echo "Your IP: $PEER_IP"
echo "Config:  $CONF_FILE"
echo ""

if [ "$APPLY" = true ]; then
    echo "Applying WireGuard config..."
    if command -v wg-quick &> /dev/null; then
        sudo wg-quick up "$CONF_FILE"
        echo -e "${GREEN}✅ Connected!${NC}"
    else
        echo -e "${RED}Error: wg-quick not found. Install WireGuard first.${NC}"
        exit 1
    fi
else
    echo "To connect:"
    echo "  sudo wg-quick up $CONF_FILE"
    echo ""
    echo "Or with --apply flag:"
    echo "  ./join.sh --name $NAME --apply"
fi

echo ""
echo -e "${YELLOW}⚠️  Save your private key! It's only shown once.${NC}"
echo "   Config file: $CONF_FILE"
