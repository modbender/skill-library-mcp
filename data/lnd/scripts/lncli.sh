#!/usr/bin/env bash
# Wrapper for lncli (and other litd CLIs) with container auto-detection.
#
# Auto-detects a running litd container and routes commands through it.
# Falls back to local lncli if no container is found.
#
# Usage:
#   lncli.sh getinfo                                    # Auto-detect container
#   lncli.sh walletbalance
#   lncli.sh --container litd getinfo                   # Explicit container
#   lncli.sh --cli loop quote out 100000                # Use loop CLI
#   lncli.sh --cli tapcli assets list                   # Use tapcli
#   lncli.sh --cli litcli getinfo                       # Use litcli
#   lncli.sh --network testnet getinfo                  # Override network
#   lncli.sh --rpcserver remote:10009 \                 # Remote node
#            --tlscertpath ~/tls.cert \
#            --macaroonpath ~/admin.macaroon getinfo

set -e

LND_DIR="${LND_DIR:-}"
NETWORK="${NETWORK:-testnet}"
CONTAINER=""
CLI="lncli"
RPCSERVER=""
TLSCERTPATH=""
MACAROONPATH=""
LNCLI_ARGS=()

# Parse our arguments (pass everything else to the CLI).
while [[ $# -gt 0 ]]; do
    case $1 in
        --network)
            NETWORK="$2"
            shift 2
            ;;
        --lnddir)
            LND_DIR="$2"
            shift 2
            ;;
        --container)
            CONTAINER="$2"
            shift 2
            ;;
        --cli)
            CLI="$2"
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
        -h|--help)
            echo "Usage: lncli.sh [options] <command> [args]"
            echo ""
            echo "Wrapper for lncli with container auto-detection."
            echo ""
            echo "Options:"
            echo "  --network NETWORK      Bitcoin network (default: testnet)"
            echo "  --lnddir DIR           lnd data directory (default: ~/.lnd)"
            echo "  --container NAME       Run CLI inside a specific Docker container"
            echo "  --cli CLI              CLI to use (default: lncli)"
            echo "                         Available: lncli, litcli, loop, pool, tapcli, frcli"
            echo "  --rpcserver HOST:PORT  Connect to a remote lnd node"
            echo "  --tlscertpath PATH     TLS certificate for remote connection"
            echo "  --macaroonpath PATH    Macaroon for remote authentication"
            echo ""
            echo "Container auto-detection order:"
            echo "  litd > litd-shared > lnd > lnd-shared"
            echo ""
            echo "All other arguments are passed directly to the CLI."
            exit 0
            ;;
        *)
            LNCLI_ARGS+=("$1")
            shift
            ;;
    esac
done

if [ ${#LNCLI_ARGS[@]} -eq 0 ]; then
    echo "Error: No command specified." >&2
    echo "Usage: lncli.sh <command> [args]" >&2
    exit 1
fi

# Auto-detect container if not explicitly specified.
if [ -z "$CONTAINER" ] && [ -z "$RPCSERVER" ] && command -v docker &>/dev/null; then
    for candidate in litd litd-shared lnd lnd-shared; do
        if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "$candidate"; then
            CONTAINER="$candidate"
            break
        fi
    done
fi

# Apply default lnddir if not set.
if [ -z "$LND_DIR" ]; then
    if [ -n "$CONTAINER" ]; then
        LND_DIR="/root/.lnd"
    else
        LND_DIR="$HOME/.lnd"
    fi
fi

# Build connection flags (only for lncli, not other CLIs).
CONN_FLAGS=()
if [ "$CLI" = "lncli" ]; then
    CONN_FLAGS+=("--network=$NETWORK" "--lnddir=$LND_DIR")
    if [ -n "$RPCSERVER" ]; then
        CONN_FLAGS+=("--rpcserver=$RPCSERVER")
    fi
    if [ -n "$TLSCERTPATH" ]; then
        CONN_FLAGS+=("--tlscertpath=$TLSCERTPATH")
    fi
    if [ -n "$MACAROONPATH" ]; then
        CONN_FLAGS+=("--macaroonpath=$MACAROONPATH")
    fi
fi

# Execute the command.
if [ -n "$CONTAINER" ]; then
    # Container mode: run CLI inside the container.
    if ! docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "$CONTAINER"; then
        echo "Error: Container '$CONTAINER' is not running." >&2
        echo "Start it with: skills/lnd/scripts/docker-start.sh" >&2
        exit 1
    fi

    exec docker exec "$CONTAINER" "$CLI" "${CONN_FLAGS[@]}" "${LNCLI_ARGS[@]}"
else
    # Local mode: run CLI on the host.
    if ! command -v "$CLI" &>/dev/null; then
        echo "Error: $CLI not found locally and no litd container detected." >&2
        echo "" >&2
        echo "Either:" >&2
        echo "  1. Start a litd container: skills/lnd/scripts/docker-start.sh" >&2
        echo "  2. Install from source: skills/lnd/scripts/install.sh --source" >&2
        exit 1
    fi
    exec "$CLI" "${CONN_FLAGS[@]}" "${LNCLI_ARGS[@]}"
fi
