#!/bin/bash
#
# Telnyx Network - Setup
# Creates network + WireGuard gateway
#
# Usage: ./setup.sh --region ashburn-va [--name my-network]
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
REGION=""
NAME="openclaw-network"

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --region) REGION="$2"; shift 2 ;;
        --name) NAME="$2"; shift 2 ;;
        -h|--help)
            echo "Usage: ./setup.sh --region <region-code> [--name <network-name>]"
            echo ""
            echo "Regions: ashburn-va, chicago-il, frankfurt-de, amsterdam-nl, singapore-sg"
            echo ""
            echo "Creates:"
            echo "  - Network (free)"
            echo "  - WireGuard Gateway (\$10/mo)"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Check API key
if [ -z "$TELNYX_API_KEY" ]; then
    # Try .env file
    if [ -f "$SCRIPT_DIR/.env" ]; then
        source "$SCRIPT_DIR/.env"
    fi
fi

if [ -z "$TELNYX_API_KEY" ]; then
    echo -e "${RED}Error: TELNYX_API_KEY not set${NC}"
    echo "Set it: export TELNYX_API_KEY=\"KEY...\""
    exit 1
fi

# Check region
if [ -z "$REGION" ]; then
    echo -e "${RED}Error: --region required${NC}"
    echo "Example: ./setup.sh --region ashburn-va"
    echo ""
    echo "Available regions:"
    curl -s "$API_BASE/network_coverage?filter[available_services][contains]=cloud_vpn" \
        -H "Authorization: Bearer $TELNYX_API_KEY" | \
        python3 -c "import sys,json; data=json.load(sys.stdin); [print(f\"  {d['location']['code']:20} {d['location']['name']}\") for d in data.get('data',[])]" 2>/dev/null || echo "  (run with API key to see regions)"
    exit 1
fi

echo ""
echo -e "${GREEN}🔧 Telnyx Network Setup${NC}"
echo "========================"
echo ""
echo "Region: $REGION"
echo "Name:   $NAME"
echo ""

# Step 1: Create network
echo -n "Creating network... "
NETWORK_RESP=$(curl -s -X POST "$API_BASE/networks" \
    -H "Authorization: Bearer $TELNYX_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"name\": \"$NAME\"}")

NETWORK_ID=$(echo "$NETWORK_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('id',''))" 2>/dev/null)

if [ -z "$NETWORK_ID" ]; then
    echo -e "${RED}FAILED${NC}"
    echo "$NETWORK_RESP"
    exit 1
fi
echo -e "${GREEN}OK${NC} ($NETWORK_ID)"

# Step 2: Create WireGuard Gateway
echo -n "Creating WireGuard gateway... "
WG_RESP=$(curl -s -X POST "$API_BASE/wireguard_interfaces" \
    -H "Authorization: Bearer $TELNYX_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"network_id\": \"$NETWORK_ID\", \"name\": \"$NAME-wg\", \"region_code\": \"$REGION\"}")

WG_ID=$(echo "$WG_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('id',''))" 2>/dev/null)
WG_ENDPOINT=$(echo "$WG_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('endpoint',''))" 2>/dev/null)
WG_PUBKEY=$(echo "$WG_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('public_key',''))" 2>/dev/null)
WG_SUBNET=$(echo "$WG_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('server_ip_address',''))" 2>/dev/null)

if [ -z "$WG_ID" ]; then
    echo -e "${RED}FAILED${NC}"
    echo "$WG_RESP"
    exit 1
fi
echo -e "${GREEN}OK${NC} ($WG_ID)"

# Save config
cat > "$CONFIG_FILE" << EOF
{
  "network_id": "$NETWORK_ID",
  "network_name": "$NAME",
  "region": "$REGION",
  "wireguard_gateway": {
    "id": "$WG_ID",
    "endpoint": "$WG_ENDPOINT",
    "public_key": "$WG_PUBKEY",
    "subnet": "$WG_SUBNET"
  },
  "internet_gateway": null,
  "peers": [],
  "exposed_ports": []
}
EOF

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "WireGuard Gateway:"
echo "  Endpoint: $WG_ENDPOINT"
echo "  Subnet:   $WG_SUBNET"
echo ""
echo "Next steps:"
echo "  1. Wait ~5 min for gateway to provision"
echo "  2. Run: ./join.sh --name \"my-machine\""
echo ""
echo "Note: WireGuard Gateway costs \$10/month"
