#!/usr/bin/env bash
# Unlock lnd / litd wallet using stored passphrase via REST API.
#
# Container mode (default — auto-detects litd container):
#   unlock-wallet.sh                              # Auto-detect litd container
#   unlock-wallet.sh --container litd             # Explicit container
#   unlock-wallet.sh --container litd-signer      # Signer container
#
# Native mode:
#   unlock-wallet.sh --native                     # Local lnd
#   unlock-wallet.sh --native --rest-port 8080    # Custom REST port
#
# Remote mode:
#   unlock-wallet.sh --rest-host remote.host --rest-port 8080

set -e

LNGET_LND_DIR="${LNGET_LND_DIR:-$HOME/.lnget/lnd}"
PASSWORD_FILE="$LNGET_LND_DIR/wallet-password.txt"
REST_PORT=8080
REST_HOST="localhost"
CONTAINER=""
NATIVE=false

# Parse arguments.
while [[ $# -gt 0 ]]; do
    case $1 in
        --password-file)
            PASSWORD_FILE="$2"
            shift 2
            ;;
        --rest-port)
            REST_PORT="$2"
            shift 2
            ;;
        --rest-host)
            REST_HOST="$2"
            shift 2
            ;;
        --container)
            CONTAINER="$2"
            shift 2
            ;;
        --native)
            NATIVE=true
            shift
            ;;
        -h|--help)
            echo "Usage: unlock-wallet.sh [options]"
            echo ""
            echo "Unlock lnd / litd wallet using stored passphrase."
            echo ""
            echo "Connection options:"
            echo "  --container NAME    Unlock wallet in a Docker container"
            echo "  --native            Unlock wallet on local lnd process"
            echo "  --rest-host HOST    REST API host (default: localhost)"
            echo "  --rest-port PORT    REST API port (default: 8080)"
            echo ""
            echo "Wallet options:"
            echo "  --password-file FILE  Path to password file"
            echo "                        (default: ~/.lnget/lnd/wallet-password.txt)"
            echo ""
            echo "Container auto-detection order: litd > litd-shared > lnd > lnd-shared"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Auto-detect container if not native and no container specified.
if [ "$NATIVE" = false ] && [ -z "$CONTAINER" ] && [ "$REST_HOST" = "localhost" ]; then
    if command -v docker &>/dev/null; then
        for candidate in litd litd-shared lnd lnd-shared; do
            if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "$candidate"; then
                CONTAINER="$candidate"
                break
            fi
        done
    fi

    # If no container found, fall back to native.
    if [ -z "$CONTAINER" ]; then
        NATIVE=true
    fi
fi

# Container mode: verify container is running.
if [ -n "$CONTAINER" ]; then
    if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "$CONTAINER"; then
        echo "Error: Container '$CONTAINER' is not running." >&2
        echo "Start it with: skills/lnd/scripts/docker-start.sh" >&2
        exit 1
    fi
fi

# Verify password file exists on the host.
if [ ! -f "$PASSWORD_FILE" ]; then
    echo "Error: Password file not found: $PASSWORD_FILE" >&2
    echo "Run create-wallet.sh first to create the wallet." >&2
    exit 1
fi

PASSWORD=$(cat "$PASSWORD_FILE")

if [ -n "$CONTAINER" ]; then
    echo "Unlocking wallet in container '$CONTAINER' via REST API..."
else
    echo "Unlocking wallet via REST API (port $REST_PORT)..."
fi

# Source shared REST helpers.
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../../lib/rest.sh"

# Build the unlock payload.
PAYLOAD=$(jq -n --arg pass "$(echo -n "$PASSWORD" | base64)" \
    '{wallet_password: $pass}')

RESPONSE=$(rest_call POST "/v1/unlockwallet" "$PAYLOAD")

# Check for errors.
ERROR=$(echo "$RESPONSE" | jq -r '.message // empty' 2>/dev/null)
if [ -n "$ERROR" ]; then
    if echo "$ERROR" | grep -q "already unlocked"; then
        echo "Wallet is already unlocked."
        exit 0
    fi
    echo "Error unlocking wallet: $ERROR" >&2
    exit 1
fi

echo "Wallet unlocked successfully."
