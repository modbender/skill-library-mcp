#!/usr/bin/env bash
# Stop litd / lnd — delegates to Docker by default.
#
# Usage:
#   stop-lnd.sh                    # Docker stop (auto-detect)
#   stop-lnd.sh --clean            # Docker stop + remove volumes
#   stop-lnd.sh --watchonly        # Docker stop watch-only mode
#   stop-lnd.sh --native           # Stop native lnd process
#   stop-lnd.sh --native --force   # SIGTERM native process
#   stop-lnd.sh --container sam    # Stop specific container
#   stop-lnd.sh --rpcserver remote:10009 --tlscertpath ~/tls.cert --macaroonpath ~/admin.macaroon
#
# By default, this script delegates to docker-stop.sh. Use --native for
# stopping a local lnd process.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NATIVE=false

# Check for --native flag before parsing other args.
PASS_ARGS=()
for arg in "$@"; do
    if [ "$arg" = "--native" ]; then
        NATIVE=true
    else
        PASS_ARGS+=("$arg")
    fi
done

# If not native mode, delegate to docker-stop.sh.
if [ "$NATIVE" = false ]; then
    # Check if we have Docker-specific args or a running container.
    HAS_CONTAINER_ARG=false
    for arg in "${PASS_ARGS[@]}"; do
        if [ "$arg" = "--container" ]; then
            HAS_CONTAINER_ARG=true
            break
        fi
    done

    # If --container is specified, use the old container-specific stop logic.
    if [ "$HAS_CONTAINER_ARG" = true ]; then
        NATIVE=true
    elif command -v docker &>/dev/null; then
        # Check if any litd containers are running.
        if docker ps --format '{{.Names}}' 2>/dev/null | grep -qE '^litd'; then
            exec "$SCRIPT_DIR/docker-stop.sh" "${PASS_ARGS[@]}"
        fi
        # No litd containers found, fall through to native.
        NATIVE=true
    else
        NATIVE=true
    fi
fi

# --- Native / container-specific stop logic ---

LND_DIR="${LND_DIR:-}"
NETWORK="${NETWORK:-testnet}"
FORCE=false
CONTAINER=""
RPCSERVER=""
TLSCERTPATH=""
MACAROONPATH=""

# Parse arguments.
set -- "${PASS_ARGS[@]}"
while [[ $# -gt 0 ]]; do
    case $1 in
        --force)
            FORCE=true
            shift
            ;;
        --network)
            NETWORK="$2"
            shift 2
            ;;
        --container)
            CONTAINER="$2"
            shift 2
            ;;
        --rpcserver)
            RPCSERVER="$2"
            shift 2
            ;;
        --tlscertpath)
            TLSCERTPATH="$2"
            shift 2
            ;;
        --macaroonpath)
            MACAROONPATH="$2"
            shift 2
            ;;
        --clean|-v|--watchonly|--regtest|--all)
            # These are docker-stop.sh flags; pass through.
            echo "Forwarding to docker-stop.sh (flag: $1)..."
            exec "$SCRIPT_DIR/docker-stop.sh" "${PASS_ARGS[@]}"
            ;;
        -h|--help)
            echo "Usage: stop-lnd.sh [options]"
            echo ""
            echo "Stop litd / lnd."
            echo ""
            echo "Docker options (default):"
            echo "  --clean, -v       Remove volumes (clean state)"
            echo "  --watchonly        Stop watch-only + signer containers"
            echo "  --regtest          Stop regtest containers"
            echo "  --all              Stop all litd containers"
            echo ""
            echo "Native options (--native):"
            echo "  --native               Stop native lnd process"
            echo "  --force                Send SIGTERM immediately"
            echo "  --container NAME       Stop lnd in a specific container"
            echo "  --rpcserver HOST:PORT  Remote lnd node"
            echo "  --tlscertpath PATH     TLS certificate for remote"
            echo "  --macaroonpath PATH    Macaroon for remote"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Apply default lnddir if not set.
if [ -z "$LND_DIR" ]; then
    if [ -n "$CONTAINER" ]; then
        LND_DIR="/root/.lnd"
    else
        LND_DIR="$HOME/.lnd"
    fi
fi

if [ -n "$CONTAINER" ]; then
    # Docker container mode.
    if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
        echo "Container '$CONTAINER' is not running."
        exit 0
    fi

    echo "Stopping lnd in container '$CONTAINER'..."

    if [ "$FORCE" = true ]; then
        docker stop "$CONTAINER"
        echo "Container stopped."
    else
        if docker exec "$CONTAINER" lncli --network="$NETWORK" --lnddir="$LND_DIR" stop 2>/dev/null; then
            echo "Graceful shutdown initiated."
        else
            echo "lncli stop failed, stopping container..."
            docker stop "$CONTAINER"
            echo "Container stopped."
        fi
    fi
    exit 0
fi

# Build connection flags for lncli.
CONN_FLAGS=(--network="$NETWORK" --lnddir="$LND_DIR")
if [ -n "$RPCSERVER" ]; then
    CONN_FLAGS+=("--rpcserver=$RPCSERVER")
fi
if [ -n "$TLSCERTPATH" ]; then
    CONN_FLAGS+=("--tlscertpath=$TLSCERTPATH")
fi
if [ -n "$MACAROONPATH" ]; then
    CONN_FLAGS+=("--macaroonpath=$MACAROONPATH")
fi

# Remote mode — stop via lncli only (no PID access).
if [ -n "$RPCSERVER" ]; then
    echo "Stopping remote lnd at $RPCSERVER..."
    if lncli "${CONN_FLAGS[@]}" stop; then
        echo "Graceful shutdown initiated."
    else
        echo "Error: lncli stop failed for remote node." >&2
        exit 1
    fi
    exit 0
fi

# Local mode — check if lnd is running.
LND_PID=$(pgrep -x lnd 2>/dev/null || true)
if [ -z "$LND_PID" ]; then
    echo "lnd is not running."
    exit 0
fi

echo "Stopping lnd (PID: $LND_PID)..."

if [ "$FORCE" = true ]; then
    kill "$LND_PID"
    echo "Sent SIGTERM."
else
    # Try graceful shutdown via lncli.
    if lncli "${CONN_FLAGS[@]}" stop 2>/dev/null; then
        echo "Graceful shutdown initiated."
    else
        echo "lncli stop failed, sending SIGTERM..."
        kill "$LND_PID"
    fi
fi

# Wait for process to exit.
echo "Waiting for lnd to exit..."
for i in {1..15}; do
    if ! kill -0 "$LND_PID" 2>/dev/null; then
        echo "lnd stopped."
        exit 0
    fi
    sleep 1
done

echo "Warning: lnd did not exit within 15 seconds." >&2
echo "Use --force or kill -9 $LND_PID" >&2
exit 1
