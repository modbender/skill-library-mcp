#!/usr/bin/env bash
# Start litd (Lightning Terminal) — delegates to Docker by default.
#
# Usage:
#   start-lnd.sh                                         # Docker (default)
#   start-lnd.sh --watchonly                             # Watch-only + signer
#   start-lnd.sh --regtest                               # Regtest with bitcoind
#   start-lnd.sh --network mainnet                       # Override network
#   start-lnd.sh --profile taproot                       # Load profile
#   start-lnd.sh --native                                # Native lnd (no Docker)
#   start-lnd.sh --native --mode standalone              # Native standalone
#   start-lnd.sh --native --signer-host 10.0.0.5:10012  # Native watch-only
#
# By default, this script delegates to docker-start.sh. Use --native to
# run lnd as a local process (requires lnd built from source).

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

# If not native mode, delegate to docker-start.sh.
if [ "$NATIVE" = false ]; then
    if command -v docker &>/dev/null; then
        exec "$SCRIPT_DIR/docker-start.sh" "${PASS_ARGS[@]}"
    else
        echo "Docker not available. Falling back to native mode." >&2
        echo "Install Docker or use --native explicitly." >&2
        echo ""
        NATIVE=true
    fi
fi

# --- Native mode: original lnd startup logic ---

LNGET_LND_DIR="${LNGET_LND_DIR:-$HOME/.lnget/lnd}"
LND_DIR="${LND_DIR:-$HOME/.lnd}"
NETWORK="testnet"
FOREGROUND=false
EXTRA_ARGS=""
CONF_FILE="$LNGET_LND_DIR/lnd.conf"
MODE="watchonly"
SIGNER_HOST="${LND_SIGNER_HOST:-}"

# Parse arguments.
set -- "${PASS_ARGS[@]}"
while [[ $# -gt 0 ]]; do
    case $1 in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --signer-host)
            SIGNER_HOST="$2"
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
        --foreground)
            FOREGROUND=true
            shift
            ;;
        --extra-args)
            EXTRA_ARGS="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: start-lnd.sh [options]"
            echo ""
            echo "Start lnd natively (without Docker)."
            echo ""
            echo "Options:"
            echo "  --native             Run lnd as a local process (required)"
            echo "  --mode MODE          Node mode: watchonly (default) or standalone"
            echo "  --signer-host HOST   Signer RPC address (e.g., 10.0.0.5:10012)"
            echo "  --network NETWORK    Bitcoin network (default: testnet)"
            echo "  --lnddir DIR         lnd data directory (default: ~/.lnd)"
            echo "  --foreground         Run in foreground (default: background)"
            echo "  --extra-args ARGS    Additional lnd arguments"
            echo ""
            echo "Modes:"
            echo "  watchonly    Connect to remote signer (no keys on this machine)"
            echo "  standalone   Full lnd with local keys (for testing)"
            echo ""
            echo "Environment:"
            echo "  LND_SIGNER_HOST     Default signer host (overridden by --signer-host)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Validate mode.
if [ "$MODE" != "watchonly" ] && [ "$MODE" != "standalone" ]; then
    echo "Error: Invalid mode '$MODE'. Use 'watchonly' or 'standalone'." >&2
    exit 1
fi

# Verify lnd is installed.
if ! command -v lnd &>/dev/null; then
    echo "Error: lnd not found. Run install.sh --source first." >&2
    exit 1
fi

# Check if lnd is already running.
if pgrep -x lnd &>/dev/null; then
    echo "lnd is already running (PID: $(pgrep -x lnd))."
    echo "Use stop-lnd.sh to stop it first."
    exit 1
fi

# Watch-only mode requires signer host.
if [ "$MODE" = "watchonly" ]; then
    if [ -z "$SIGNER_HOST" ]; then
        echo "Error: --signer-host is required in watchonly mode." >&2
        echo "Example: start-lnd.sh --native --signer-host 10.0.0.5:10012" >&2
        echo "Or set LND_SIGNER_HOST environment variable." >&2
        exit 1
    fi

    CREDS_DIR="$LNGET_LND_DIR/signer-credentials"
    if [ ! -f "$CREDS_DIR/tls.cert" ] || [ ! -f "$CREDS_DIR/admin.macaroon" ]; then
        echo "Error: Signer credentials not found at $CREDS_DIR" >&2
        echo "Run import-credentials.sh first." >&2
        exit 1
    fi
fi

# Create config directory if needed.
mkdir -p "$LNGET_LND_DIR"

# Copy config template if no config exists.
if [ ! -f "$CONF_FILE" ]; then
    TEMPLATE="$SCRIPT_DIR/../templates/lnd.conf.template"
    if [ -f "$TEMPLATE" ]; then
        echo "Creating config from template..."
        # Replace network placeholder in template.
        sed "s/bitcoin\.mainnet=true/bitcoin.$NETWORK=true/g" "$TEMPLATE" > "$CONF_FILE"

        # Replace password file path.
        sed -i.bak "s|wallet-unlock-password-file=.*|wallet-unlock-password-file=$LNGET_LND_DIR/wallet-password.txt|g" "$CONF_FILE"
        rm -f "$CONF_FILE.bak"
    else
        echo "Warning: No config template found. lnd will use defaults." >&2
    fi
fi

# Configure remote signer in config if watchonly mode.
if [ "$MODE" = "watchonly" ] && [ -f "$CONF_FILE" ]; then
    CREDS_DIR="$LNGET_LND_DIR/signer-credentials"

    # Remove any existing remotesigner lines.
    sed -i.bak '/^\# \[remotesigner\]/,/^\# remotesigner\./d' "$CONF_FILE"
    rm -f "$CONF_FILE.bak"

    # Append active remotesigner configuration.
    cat >> "$CONF_FILE" <<EOF

[remotesigner]
remotesigner.enable=true
remotesigner.rpchost=$SIGNER_HOST
remotesigner.tlscertpath=$CREDS_DIR/tls.cert
remotesigner.macaroonpath=$CREDS_DIR/admin.macaroon
EOF

    echo "Remote signer configured: $SIGNER_HOST"
fi

echo "=== Starting lnd (native) ==="
echo "Mode:     $MODE"
echo "Network:  $NETWORK"
echo "Data dir: $LND_DIR"
echo "Config:   $CONF_FILE"
if [ "$MODE" = "watchonly" ]; then
    echo "Signer:   $SIGNER_HOST"
fi
echo ""

if [ "$MODE" = "standalone" ]; then
    echo "WARNING: Running in standalone mode. Private keys are on this machine."
    echo "For production use, set up a remote signer with the lightning-security-module skill."
    echo ""
fi

LOG_FILE="$LNGET_LND_DIR/lnd-start.log"

if [ "$FOREGROUND" = true ]; then
    exec lnd \
        --lnddir="$LND_DIR" \
        --configfile="$CONF_FILE" \
        $EXTRA_ARGS
else
    nohup lnd \
        --lnddir="$LND_DIR" \
        --configfile="$CONF_FILE" \
        $EXTRA_ARGS \
        > "$LOG_FILE" 2>&1 &
    LND_PID=$!
    echo "lnd started in background (PID: $LND_PID)"
    echo "Log file: $LOG_FILE"
    echo ""

    # Wait briefly and verify it's running.
    sleep 2
    if kill -0 "$LND_PID" 2>/dev/null; then
        echo "lnd is running."
    else
        echo "Error: lnd exited immediately. Check $LOG_FILE" >&2
        tail -20 "$LOG_FILE" 2>/dev/null
        exit 1
    fi

    echo ""
    echo "Next steps:"
    echo "  # Check status"
    echo "  skills/lnd/scripts/lncli.sh getinfo"
    echo ""
    if [ "$MODE" = "standalone" ]; then
        echo "  # If wallet not yet created"
        echo "  skills/lnd/scripts/create-wallet.sh --mode standalone"
    fi
fi
