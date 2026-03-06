#!/bin/bash
#
# Telnyx Network - Add Public IP
# Creates an Internet Gateway for public exposure
#
# Usage: ./add-public-ip.sh [--yes]
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
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: No config found. Run ./setup.sh first"
    exit 1
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

# Check if already has IGW
EXISTING=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c.get('internet_gateway',{}).get('id',''))" 2>/dev/null)
if [ -n "$EXISTING" ]; then
    PUBLIC_IP=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c['internet_gateway']['public_ip'])")
    echo "Internet Gateway already exists."
    echo "Public IP: $PUBLIC_IP"
    exit 0
fi

# Warning
if [ "$SKIP_CONFIRM" = false ]; then
    echo ""
    echo -e "${YELLOW}⚠️  WARNING: This will expose your network to the internet.${NC}"
    echo ""
    echo "   - Adds Internet Gateway (\$50/month)"
    echo "   - Assigns a public IP address"
    echo "   - Only explicitly exposed ports will be accessible"
    echo ""
    read -p "Continue? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Cancelled."
        exit 0
    fi
fi

# Get network info
NETWORK_ID=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c['network_id'])")
REGION=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c['region'])")
NAME=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c['network_name'])")

echo ""
echo "Creating Internet Gateway..."

IGW_RESP=$(curl -s -X POST "$API_BASE/public_internet_gateways" \
    -H "Authorization: Bearer $TELNYX_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"network_id\": \"$NETWORK_ID\", \"name\": \"$NAME-igw\", \"region_code\": \"$REGION\"}")

IGW_ID=$(echo "$IGW_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('id',''))" 2>/dev/null)
PUBLIC_IP=$(echo "$IGW_RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('public_ip',''))" 2>/dev/null)

if [ -z "$IGW_ID" ]; then
    echo -e "${RED}Failed to create Internet Gateway${NC}"
    echo "$IGW_RESP"
    exit 1
fi

# Update config
python3 << EOF
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)
config['internet_gateway'] = {
    'id': '$IGW_ID',
    'public_ip': '$PUBLIC_IP'
}
with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
EOF

echo ""
echo -e "${GREEN}✅ Internet Gateway created!${NC}"
echo ""
echo "Public IP: $PUBLIC_IP"
echo ""
echo "Note: Gateway takes ~10 min to provision."
echo ""
echo "Next: ./expose.sh <port> to open ports"
echo ""
echo -e "${YELLOW}Cost: \$50/month${NC}"
