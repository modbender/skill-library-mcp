#!/usr/bin/env bash
# Bake, inspect, and manage lnd macaroons for least-privilege agent access.
#
# Usage:
#   bake.sh --role pay-only                    # Bake a preset role
#   bake.sh --role invoice-only                # Invoice-only agent
#   bake.sh --role read-only                   # Read-only agent
#   bake.sh --role channel-admin               # Channel management agent
#   bake.sh --role signer-only                 # Remote signer scoped macaroon
#   bake.sh --custom uri:/lnrpc.Lightning/...  # Custom permissions
#   bake.sh --inspect <macaroon-path>          # Inspect a macaroon
#   bake.sh --list-permissions                 # List all available permissions
#   bake.sh --container sam --role pay-only     # Bake inside a Docker container
#   bake.sh --rpcserver remote:10009 \          # Bake on a remote node
#           --tlscertpath ~/tls.cert \
#           --macaroonpath ~/admin.macaroon --role pay-only

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LND_DIR="${LND_DIR:-}"
NETWORK="${NETWORK:-testnet}"
RPC_PORT=""
SAVE_TO=""
ROLE=""
INSPECT=""
LIST_PERMS=false
CUSTOM_PERMS=()
CONTAINER=""
RPCSERVER=""
TLSCERTPATH=""
MACAROONPATH=""

# Parse arguments.
while [[ $# -gt 0 ]]; do
    case $1 in
        --role)
            ROLE="$2"
            shift 2
            ;;
        --custom)
            shift
            # Collect all remaining non-flag args as permissions.
            while [[ $# -gt 0 ]] && [[ ! "$1" =~ ^-- ]]; do
                CUSTOM_PERMS+=("$1")
                shift
            done
            ;;
        --inspect)
            INSPECT="$2"
            shift 2
            ;;
        --list-permissions)
            LIST_PERMS=true
            shift
            ;;
        --save-to)
            SAVE_TO="$2"
            shift 2
            ;;
        --network)
            NETWORK="$2"
            shift 2
            ;;
        --lnddir)
            LND_DIR="$2"
            shift 2
            ;;
        --rpc-port)
            RPC_PORT="$2"
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
        -h|--help)
            echo "Usage: bake.sh [options]"
            echo ""
            echo "Bake, inspect, and manage lnd macaroons."
            echo ""
            echo "Actions:"
            echo "  --role ROLE            Bake a preset role macaroon"
            echo "  --custom URI [URI...]  Bake with custom permission URIs"
            echo "  --inspect PATH         Inspect a macaroon file"
            echo "  --list-permissions     List all available permission URIs"
            echo ""
            echo "Preset roles: pay-only, invoice-only, read-only, channel-admin, signer-only"
            echo ""
            echo "Options:"
            echo "  --save-to PATH         Output path (default: auto-generated)"
            echo "  --network NETWORK      Bitcoin network (default: testnet)"
            echo "  --lnddir DIR           lnd data directory (default: ~/.lnd)"
            echo "  --rpc-port PORT        lnd RPC port (for non-default setups)"
            echo "  --container NAME       Run lncli inside a Docker container"
            echo "  --rpcserver HOST:PORT  Connect to a remote lnd node"
            echo "  --tlscertpath PATH     TLS certificate for remote connection"
            echo "  --macaroonpath PATH    Macaroon for remote authentication"
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

# Build lncli base command as an array (preserves paths with spaces).
LNCLI_CMD=()
if [ -n "$CONTAINER" ]; then
    LNCLI_CMD+=(docker exec "$CONTAINER")
fi
LNCLI_CMD+=(lncli "--network=$NETWORK" "--lnddir=$LND_DIR")
if [ -n "$RPCSERVER" ]; then
    LNCLI_CMD+=("--rpcserver=$RPCSERVER")
elif [ -n "$RPC_PORT" ]; then
    LNCLI_CMD+=("--rpcserver=localhost:$RPC_PORT")
fi
if [ -n "$TLSCERTPATH" ]; then
    LNCLI_CMD+=("--tlscertpath=$TLSCERTPATH")
fi
if [ -n "$MACAROONPATH" ]; then
    LNCLI_CMD+=("--macaroonpath=$MACAROONPATH")
fi

# Verify lncli is available.
if [ -n "$CONTAINER" ]; then
    if ! docker exec "$CONTAINER" which lncli &>/dev/null; then
        echo "Error: lncli not found in container '$CONTAINER'." >&2
        exit 1
    fi
elif ! command -v lncli &>/dev/null; then
    echo "Error: lncli not found. Run the lnd skill's install.sh first." >&2
    exit 1
fi

# --- Inspect mode ---
if [ -n "$INSPECT" ]; then
    if [ -n "$CONTAINER" ]; then
        # The macaroon may be on the host or inside the container. If it
        # exists on the host, copy it into the container for inspection.
        if [ -f "$INSPECT" ]; then
            CONTAINER_TMP="/tmp/inspect-$(date +%s).macaroon"
            docker cp "$INSPECT" "$CONTAINER:$CONTAINER_TMP"
            INSPECT_PATH="$CONTAINER_TMP"
        elif docker exec "$CONTAINER" test -f "$INSPECT" 2>/dev/null; then
            INSPECT_PATH="$INSPECT"
        else
            echo "Error: Macaroon file not found: $INSPECT" >&2
            exit 1
        fi
    elif [ ! -f "$INSPECT" ]; then
        echo "Error: Macaroon file not found: $INSPECT" >&2
        exit 1
    else
        INSPECT_PATH="$INSPECT"
    fi
    echo "=== Macaroon: $(basename "$INSPECT") ==="
    echo "Path: $INSPECT"
    if [ -n "$CONTAINER" ]; then
        echo "Container: $CONTAINER"
    fi
    echo ""
    "${LNCLI_CMD[@]}" printmacaroon --macaroon_file "$INSPECT_PATH"
    # Clean up temporary copy if we created one.
    if [ -n "$CONTAINER" ] && [ -f "$INSPECT" ]; then
        docker exec "$CONTAINER" rm -f "$INSPECT_PATH" 2>/dev/null || true
    fi
    exit 0
fi

# --- List permissions mode ---
if [ "$LIST_PERMS" = true ]; then
    echo "=== Available Macaroon Permissions ==="
    echo ""
    "${LNCLI_CMD[@]}" listpermissions | jq -r '.method_permissions | to_entries[] | .key' | sort
    exit 0
fi

# --- Bake mode ---

# Resolve permissions from role or custom.
PERMS=()

if [ -n "$ROLE" ]; then
    case $ROLE in
        pay-only)
            PERMS=(
                "uri:/lnrpc.Lightning/SendPaymentSync"
                "uri:/routerrpc.Router/SendPaymentV2"
                "uri:/lnrpc.Lightning/DecodePayReq"
                "uri:/lnrpc.Lightning/GetInfo"
                "uri:/verrpc.Versioner/GetVersion"
            )
            ;;
        invoice-only)
            PERMS=(
                "uri:/lnrpc.Lightning/AddInvoice"
                "uri:/invoicesrpc.Invoices/AddHoldInvoice"
                "uri:/lnrpc.Lightning/LookupInvoice"
                "uri:/lnrpc.Lightning/ListInvoices"
                "uri:/lnrpc.Lightning/GetInfo"
                "uri:/verrpc.Versioner/GetVersion"
            )
            ;;
        read-only)
            PERMS=(
                "uri:/lnrpc.Lightning/GetInfo"
                "uri:/lnrpc.Lightning/WalletBalance"
                "uri:/lnrpc.Lightning/ChannelBalance"
                "uri:/lnrpc.Lightning/ListChannels"
                "uri:/lnrpc.Lightning/ListPeers"
                "uri:/lnrpc.Lightning/ListPayments"
                "uri:/lnrpc.Lightning/ListInvoices"
                "uri:/lnrpc.Lightning/GetNodeInfo"
                "uri:/lnrpc.Lightning/GetChanInfo"
                "uri:/verrpc.Versioner/GetVersion"
            )
            ;;
        channel-admin)
            PERMS=(
                "uri:/lnrpc.Lightning/GetInfo"
                "uri:/lnrpc.Lightning/WalletBalance"
                "uri:/lnrpc.Lightning/ChannelBalance"
                "uri:/lnrpc.Lightning/ListChannels"
                "uri:/lnrpc.Lightning/ListPeers"
                "uri:/lnrpc.Lightning/ConnectPeer"
                "uri:/lnrpc.Lightning/DisconnectPeer"
                "uri:/lnrpc.Lightning/OpenChannelSync"
                "uri:/lnrpc.Lightning/CloseChannel"
                "uri:/lnrpc.Lightning/ClosedChannels"
                "uri:/lnrpc.Lightning/GetNodeInfo"
                "uri:/lnrpc.Lightning/GetChanInfo"
                "uri:/verrpc.Versioner/GetVersion"
            )
            ;;
        signer-only)
            PERMS=(
                "uri:/signrpc.Signer/SignOutputRaw"
                "uri:/signrpc.Signer/ComputeInputScript"
                "uri:/signrpc.Signer/MuSig2Sign"
                "uri:/signrpc.Signer/MuSig2Cleanup"
                "uri:/signrpc.Signer/MuSig2CreateSession"
                "uri:/signrpc.Signer/MuSig2RegisterNonces"
                "uri:/signrpc.Signer/MuSig2CombineSig"
                "uri:/walletrpc.WalletKit/DeriveKey"
                "uri:/walletrpc.WalletKit/DeriveNextKey"
                "uri:/lnrpc.Lightning/GetInfo"
                "uri:/verrpc.Versioner/GetVersion"
            )
            ;;
        *)
            echo "Error: Unknown role '$ROLE'." >&2
            echo "Available roles: pay-only, invoice-only, read-only, channel-admin, signer-only" >&2
            exit 1
            ;;
    esac
elif [ ${#CUSTOM_PERMS[@]} -gt 0 ]; then
    PERMS=("${CUSTOM_PERMS[@]}")
else
    echo "Error: Specify --role, --custom, --inspect, or --list-permissions." >&2
    echo "Run bake.sh --help for usage." >&2
    exit 1
fi

# Determine output path.
if [ -z "$SAVE_TO" ]; then
    if [ -n "$CONTAINER" ] || [ -n "$RPCSERVER" ]; then
        # Container/remote mode: save locally, not inside the container or on the remote.
        MACAROON_DIR="$HOME/.lnget/macaroons"
    else
        MACAROON_DIR="$LND_DIR/data/chain/bitcoin/$NETWORK"
    fi
    if [ -n "$ROLE" ]; then
        SAVE_TO="$MACAROON_DIR/${ROLE}.macaroon"
    else
        SAVE_TO="$MACAROON_DIR/custom-$(date +%s).macaroon"
    fi
fi

# Ensure output directory exists.
mkdir -p "$(dirname "$SAVE_TO")"

echo "=== Baking Macaroon ==="
if [ -n "$ROLE" ]; then
    echo "Role:        $ROLE"
fi
echo "Permissions: ${#PERMS[@]}"
echo "Output:      $SAVE_TO"
echo ""

# Bake the macaroon.
if [ -n "$CONTAINER" ]; then
    # Bake inside container, then copy out to local path.
    CONTAINER_TMP="/tmp/baked-$(date +%s).macaroon"
    "${LNCLI_CMD[@]}" bakemacaroon "${PERMS[@]}" --save_to="$CONTAINER_TMP"
    docker cp "$CONTAINER:$CONTAINER_TMP" "$SAVE_TO"
    docker exec "$CONTAINER" rm -f "$CONTAINER_TMP"
else
    "${LNCLI_CMD[@]}" bakemacaroon "${PERMS[@]}" --save_to="$SAVE_TO"
fi

# Set restrictive permissions.
chmod 600 "$SAVE_TO"

echo ""
echo "=== Macaroon Baked ==="
echo "Saved to: $SAVE_TO (mode 0600)"
echo ""
echo "Permissions granted:"
for p in "${PERMS[@]}"; do
    echo "  $p"
done
echo ""
echo "To verify:"
echo "  bake.sh --inspect $SAVE_TO"
echo ""
echo "To use with lnget:"
echo "  ln:"
echo "    lnd:"
echo "      macaroon: $SAVE_TO"
