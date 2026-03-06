#!/bin/bash
#
# Telnyx Network - Expose Ports
# Opens ports on the WireGuard interface
#
# Usage: ./expose.sh <port> [port2 port3...] [--force]
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.json"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Dangerous ports that need --force
DANGEROUS_PORTS=(22 23 3306 5432 6379 27017 11211)

FORCE=false
PORTS=()

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --force|-f) FORCE=true; shift ;;
        -h|--help)
            echo "Usage: ./expose.sh <port> [port2...] [--force]"
            echo ""
            echo "Examples:"
            echo "  ./expose.sh 443           # Expose HTTPS"
            echo "  ./expose.sh 80 443        # Expose HTTP and HTTPS"
            echo "  ./expose.sh 22 --force    # Expose SSH (dangerous)"
            echo ""
            echo "Blocked by default (need --force):"
            echo "  22 (SSH), 23 (Telnet), 3306 (MySQL),"
            echo "  5432 (PostgreSQL), 6379 (Redis), 27017 (MongoDB)"
            exit 0
            ;;
        *)
            if [[ $1 =~ ^[0-9]+$ ]]; then
                PORTS+=("$1")
            else
                echo "Invalid port: $1"
                exit 1
            fi
            shift
            ;;
    esac
done

if [ ${#PORTS[@]} -eq 0 ]; then
    echo "Usage: ./expose.sh <port> [port2...] [--force]"
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: No config found. Run ./setup.sh first"
    exit 1
fi

# Check for Internet Gateway
IGW=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c.get('internet_gateway',{}).get('id',''))" 2>/dev/null)
if [ -z "$IGW" ]; then
    echo -e "${YELLOW}Warning: No Internet Gateway configured.${NC}"
    echo "Ports will only be accessible from within the mesh network."
    echo ""
    echo "For public access, run: ./add-public-ip.sh"
    echo ""
fi

# Check for dangerous ports
for PORT in "${PORTS[@]}"; do
    for DPORT in "${DANGEROUS_PORTS[@]}"; do
        if [ "$PORT" -eq "$DPORT" ] && [ "$FORCE" = false ]; then
            echo -e "${RED}🚫 Port $PORT blocked by default.${NC}"
            echo ""
            case $PORT in
                22) echo "SSH exposure is dangerous - consider using mesh-only access." ;;
                3306|5432|6379|27017) echo "Database ports should not be publicly exposed." ;;
                *) echo "This port is considered dangerous." ;;
            esac
            echo ""
            echo "If you must expose it:"
            echo "  ./expose.sh $PORT --force"
            exit 1
        fi
    done
done

# Detect WireGuard interface
WG_IFACE=$(sudo wg show 2>/dev/null | grep "interface:" | awk '{print $2}' | head -1)
if [ -z "$WG_IFACE" ]; then
    WG_IFACE="wg0"
    echo -e "${YELLOW}Note: WireGuard not active, using default interface 'wg0'${NC}"
fi

echo ""
echo "Exposing ports: ${PORTS[*]}"
echo "Interface: $WG_IFACE"
echo ""

# Apply iptables rules
for PORT in "${PORTS[@]}"; do
    echo -n "Opening port $PORT... "
    
    # Check if rule already exists
    if sudo iptables -C INPUT -i "$WG_IFACE" -p tcp --dport "$PORT" -j ACCEPT 2>/dev/null; then
        echo "already open"
    else
        sudo iptables -A INPUT -i "$WG_IFACE" -p tcp --dport "$PORT" -j ACCEPT
        echo -e "${GREEN}OK${NC}"
    fi
done

# Update config
python3 << EOF
import json
with open('$CONFIG_FILE', 'r') as f:
    config = json.load(f)
existing = set(config.get('exposed_ports', []))
existing.update([int(p) for p in "${PORTS[*]}".split()])
config['exposed_ports'] = sorted(list(existing))
with open('$CONFIG_FILE', 'w') as f:
    json.dump(config, f, indent=2)
EOF

PUBLIC_IP=$(python3 -c "import json; c=json.load(open('$CONFIG_FILE')); print(c.get('internet_gateway',{}).get('public_ip','(mesh only)'))" 2>/dev/null)

echo ""
echo -e "${GREEN}✅ Ports exposed!${NC}"
echo ""
echo "Access via: $PUBLIC_IP"
for PORT in "${PORTS[@]}"; do
    echo "  - $PUBLIC_IP:$PORT"
done
echo ""
echo "To close: ./unexpose.sh ${PORTS[*]}"
