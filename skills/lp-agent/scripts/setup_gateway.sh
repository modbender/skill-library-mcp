#!/bin/bash
#
# Setup Gateway for LP operations
#
# Starts Gateway via hummingbot-api and optionally configures custom RPC endpoints.
# Requires Hummingbot API to be running (deploy-hummingbot-api).
#
# Usage:
#   # Start Gateway with defaults
#   bash scripts/setup_gateway.sh
#
#   # Start Gateway with custom image
#   bash scripts/setup_gateway.sh --image hummingbot/gateway:development
#
#   # Start Gateway with custom RPC
#   bash scripts/setup_gateway.sh --rpc-url https://your-rpc-endpoint.com
#
#   # Configure RPC for a specific network
#   bash scripts/setup_gateway.sh --network ethereum-mainnet --rpc-url https://your-eth-rpc.com
#
#   # Start with custom passphrase
#   bash scripts/setup_gateway.sh --passphrase mypassword
#
#   # Check Gateway status only
#   bash scripts/setup_gateway.sh --status
#
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load .env
for f in hummingbot-api/.env ~/.hummingbot/.env .env; do
    if [ -f "$f" ]; then
        set -a; source "$f"; set +a
        break
    fi
done

API_URL="${HUMMINGBOT_API_URL:-http://localhost:8000}"
API_USER="${API_USER:-admin}"
API_PASS="${API_PASS:-admin}"

# Defaults
PASSPHRASE="hummingbot"
IMAGE="hummingbot/gateway:development"
RPC_URL=""
STATUS_ONLY=false
NETWORK="solana-mainnet-beta"
PORT=15888

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --passphrase) PASSPHRASE="$2"; shift 2 ;;
        --image)      IMAGE="$2"; shift 2 ;;
        --rpc-url)    RPC_URL="$2"; shift 2 ;;
        --network)    NETWORK="$2"; shift 2 ;;
        --port)       PORT="$2"; shift 2 ;;
        --status)     STATUS_ONLY=true; shift ;;
        -h|--help)
            echo "Usage: setup_gateway.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --passphrase TEXT   Gateway passphrase (default: hummingbot)"
            echo "  --image IMAGE       Docker image (default: hummingbot/gateway:development)"
            echo "  --rpc-url URL       Custom RPC endpoint for --network"
            echo "  --network ID        Network ID (default: solana-mainnet-beta)"
            echo "  --port PORT         Gateway port (default: 15888)"
            echo "  --status            Check status only"
            echo "  -h, --help          Show this help"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# Colors
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
else
    GREEN='' RED='' YELLOW='' NC=''
fi

ok()   { echo -e "${GREEN}✓${NC} $*"; }
fail() { echo -e "${RED}✗${NC} $*"; }
warn() { echo -e "${YELLOW}!${NC} $*"; }

# Auth header
AUTH=$(echo -n "$API_USER:$API_PASS" | base64)

api_get() {
    curl -s -H "Authorization: Basic $AUTH" -H "Content-Type: application/json" "$API_URL$1" 2>/dev/null
}

api_post() {
    curl -s -X POST -H "Authorization: Basic $AUTH" -H "Content-Type: application/json" -d "$2" "$API_URL$1" 2>/dev/null
}

# Poll Gateway status until running (max 30s)
wait_for_gateway() {
    local max_attempts=15
    local attempt=0
    while [ $attempt -lt $max_attempts ]; do
        local status running
        status=$(api_get "/gateway/status")
        running=$(echo "$status" | python3 -c "import sys,json; print(json.load(sys.stdin).get('running', False))" 2>/dev/null || echo "False")
        if [ "$running" = "True" ]; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 2
    done
    return 1
}

# --- Check prerequisite: Hummingbot API ---
echo "Gateway Setup"
echo "============="
echo ""

source "$SCRIPT_DIR/check_api.sh"
if ! check_api; then
    fail "Cannot connect to Hummingbot API at $API_URL"
    echo ""
    echo "Please deploy Hummingbot API first:"
    echo "  /lp-agent deploy-hummingbot-api"
    exit 1
fi
ok "Hummingbot API is running at $API_URL"

# --- Check Gateway status ---
GW_STATUS=$(api_get "/gateway/status")
GW_RUNNING=$(echo "$GW_STATUS" | python3 -c "import sys,json; print(json.load(sys.stdin).get('running', False))" 2>/dev/null || echo "False")

if [ "$STATUS_ONLY" = "true" ]; then
    if [ "$GW_RUNNING" = "True" ]; then
        ok "Gateway is running"
        echo "$GW_STATUS" | python3 -c "
import sys, json
d = json.load(sys.stdin)
if d.get('container_id'): print(f\"  Container: {d['container_id'][:12]}\")
if d.get('image'): print(f\"  Image: {d['image']}\")
if d.get('port'): print(f\"  Port: {d['port']}\")
" 2>/dev/null || true
    else
        fail "Gateway is not running"
    fi
    exit 0
fi

# --- Start Gateway if not running ---
if [ "$GW_RUNNING" = "True" ]; then
    ok "Gateway is already running"
else
    echo "Starting Gateway (image: $IMAGE)..."
    RESULT=$(api_post "/gateway/start" "{\"passphrase\": \"$PASSPHRASE\", \"image\": \"$IMAGE\", \"port\": $PORT, \"dev_mode\": true}")

    SUCCESS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null || echo "False")
    if [ "$SUCCESS" = "True" ]; then
        ok "Gateway started"
    else
        MSG=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('message', 'Unknown error'))" 2>/dev/null || echo "$RESULT")
        fail "Failed to start Gateway: $MSG"
        exit 1
    fi

    # Wait for Gateway to be ready
    echo "Waiting for Gateway to initialize..."
    if wait_for_gateway; then
        ok "Gateway is ready"
    else
        warn "Gateway may still be starting. Check status with: bash scripts/setup_gateway.sh --status"
    fi
fi

# --- Configure custom RPC if provided ---
if [ -n "$RPC_URL" ]; then
    echo ""
    echo "Configuring custom RPC for $NETWORK..."
    RESULT=$(api_post "/gateway/networks/$NETWORK" "{\"nodeURL\": \"$RPC_URL\"}")

    SUCCESS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin).get('success', False))" 2>/dev/null || echo "False")
    if [ "$SUCCESS" = "True" ]; then
        ok "RPC configured: $RPC_URL"
        warn "Restarting Gateway for changes to take effect..."
        api_post "/gateway/restart" "{\"passphrase\": \"$PASSPHRASE\", \"image\": \"$IMAGE\", \"port\": $PORT, \"dev_mode\": true}" >/dev/null
        if wait_for_gateway; then
            ok "Gateway restarted with custom RPC"
        else
            warn "Gateway may still be restarting"
        fi
    else
        fail "Failed to configure RPC"
    fi
fi

echo ""
ok "Gateway setup complete"
echo ""
echo "Next steps:"
echo "  - Add a wallet:  /lp-agent add-wallet"
echo "  - Explore pools:  /lp-agent explore-pools"
