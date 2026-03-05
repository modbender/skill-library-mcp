#!/usr/bin/env bash
# Start litd (Lightning Terminal) containers.
#
# Usage:
#   docker-start.sh                          # Standalone litd, testnet (default)
#   docker-start.sh --watchonly              # Watch-only + signer (production)
#   docker-start.sh --regtest                # Regtest with bitcoind (dev)
#   docker-start.sh --watchonly --regtest    # Watch-only + signer on regtest
#   docker-start.sh --network mainnet        # Override network
#   docker-start.sh --profile taproot        # Load profile
#   docker-start.sh --foreground             # Run in foreground (show logs)
#   docker-start.sh --args "--lnd.foo=bar"   # Extra litd arguments
#
# Profiles: default, taproot, wumbo, debug, regtest

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/../templates"
PROFILE_DIR="$SCRIPT_DIR/../profiles"
VERSIONS_FILE="$SCRIPT_DIR/../../../versions.env"
LIB_DIR="$SCRIPT_DIR/../../lib"

MODE="standalone"
REGTEST=false
BUILD=false
DETACH=true
PROFILE=""
CUSTOM_ARGS=""
CUSTOM_NETWORK=""
DOCKER_NETWORK=""

# Source pinned versions so compose files pick them up as env vars.
if [ -f "$VERSIONS_FILE" ]; then
    source "$VERSIONS_FILE"
    export LITD_VERSION LITD_IMAGE LND_VERSION LND_IMAGE
    export BITCOIN_CORE_VERSION BITCOIN_CORE_IMAGE
fi

# Source config generation functions.
source "$LIB_DIR/config-gen.sh"

# Parse arguments.
while [[ $# -gt 0 ]]; do
    case $1 in
        --watchonly)
            MODE="watchonly"
            shift
            ;;
        --regtest)
            REGTEST=true
            shift
            ;;
        --build)
            BUILD=true
            shift
            ;;
        --foreground|-f)
            DETACH=false
            shift
            ;;
        --profile|-p)
            PROFILE="$2"
            shift 2
            ;;
        --network)
            CUSTOM_NETWORK="$2"
            shift 2
            ;;
        --docker-network)
            DOCKER_NETWORK="$2"
            shift 2
            ;;
        --args|-a)
            CUSTOM_ARGS="$2"
            shift 2
            ;;
        --list-profiles)
            echo "Available profiles:"
            echo ""
            for f in "$PROFILE_DIR"/*.env; do
                name=$(basename "$f" .env)
                desc=$(head -1 "$f" | sed 's/^# //')
                printf "  %-15s %s\n" "$name" "$desc"
            done
            echo ""
            echo "Usage: docker-start.sh --profile <name>"
            exit 0
            ;;
        -h|--help)
            echo "Usage: docker-start.sh [options]"
            echo ""
            echo "Start litd (Lightning Terminal) containers."
            echo ""
            echo "Modes:"
            echo "  (default)              Standalone litd with neutrino (testnet)"
            echo "  --watchonly            Watch-only litd + remote signer"
            echo "  --regtest              litd + bitcoind for local development"
            echo "  --watchonly --regtest  Watch-only + signer on regtest"
            echo ""
            echo "Configuration:"
            echo "  --profile, -p         Load profile (taproot, wumbo, debug, regtest)"
            echo "  --network NET         Override network (testnet, mainnet, signet)"
            echo "  --docker-network NET  Docker network to join (for external bitcoind)"
            echo "  --args, -a            Extra litd arguments (quoted string)"
            echo "  --list-profiles       Show available profiles"
            echo ""
            echo "Options:"
            echo "  --build               Rebuild images before starting"
            echo "  --foreground, -f      Run in foreground (show logs)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# Handle --regtest flag: if MODE is still standalone, set to regtest.
# If MODE is watchonly, keep it as watchonly but set network to regtest.
if [ "$REGTEST" = true ] && [ "$MODE" = "standalone" ]; then
    MODE="regtest"
fi

# Load profile if specified.
if [ -n "$PROFILE" ]; then
    PROFILE_FILE="$PROFILE_DIR/$PROFILE.env"
    if [ -f "$PROFILE_FILE" ]; then
        echo "Loading profile: $PROFILE"
        source "$PROFILE_FILE"
    else
        echo "Error: Profile '$PROFILE' not found." >&2
        echo "Available profiles:"
        ls -1 "$PROFILE_DIR"/*.env 2>/dev/null | xargs -n1 basename | sed 's/.env$//'
        exit 1
    fi
fi

# Override network if specified on command line.
if [ -n "$CUSTOM_NETWORK" ]; then
    NETWORK="$CUSTOM_NETWORK"
fi

# Append custom args to profile extra args.
if [ -n "$CUSTOM_ARGS" ]; then
    if [ -n "$LITD_EXTRA_ARGS" ]; then
        LITD_EXTRA_ARGS="$LITD_EXTRA_ARGS $CUSTOM_ARGS"
    else
        LITD_EXTRA_ARGS="$CUSTOM_ARGS"
    fi
fi

# Select compose file based on mode.
case "$MODE" in
    standalone)
        COMPOSE_FILE="docker-compose.yml"
        ;;
    watchonly)
        COMPOSE_FILE="docker-compose-watchonly.yml"
        ;;
    regtest)
        COMPOSE_FILE="docker-compose-regtest.yml"
        ;;
esac

# Determine effective network (regtest flag overrides for watchonly mode).
if [ "$REGTEST" = true ]; then
    EFFECTIVE_NETWORK="regtest"
else
    EFFECTIVE_NETWORK="${NETWORK:-testnet}"
fi

# --- Generate runtime config from template ---

LNGET_LND_DIR="${LNGET_LND_DIR:-$HOME/.lnget/lnd}"
mkdir -p "$LNGET_LND_DIR"

case "$MODE" in
    standalone)
        generate_litd_config \
            "$TEMPLATE_DIR/litd.conf.template" \
            "$LNGET_LND_DIR/litd.conf" \
            "${NETWORK:-testnet}" \
            "${LND_DEBUG:-info}" \
            "${NODE_ALIAS:-litd-agent}" \
            "${UI_PASSWORD:-agent-litd-password}" \
            "$LITD_EXTRA_ARGS"
        ;;
    regtest)
        generate_litd_config \
            "$TEMPLATE_DIR/litd-regtest.conf.template" \
            "$LNGET_LND_DIR/litd.conf" \
            "regtest" \
            "${LND_DEBUG:-debug}" \
            "${NODE_ALIAS:-litd-agent}" \
            "${UI_PASSWORD:-agent-litd-password}" \
            "$LITD_EXTRA_ARGS"
        ;;
    watchonly)
        generate_litd_config \
            "$TEMPLATE_DIR/litd-watchonly.conf.template" \
            "$LNGET_LND_DIR/litd.conf" \
            "$EFFECTIVE_NETWORK" \
            "${LND_DEBUG:-info}" \
            "${NODE_ALIAS:-litd-agent}" \
            "${UI_PASSWORD:-agent-litd-password}" \
            "$LITD_EXTRA_ARGS"

        SIGNER_TEMPLATE_DIR="$SCRIPT_DIR/../../lightning-security-module/templates"
        generate_lnd_config \
            "$SIGNER_TEMPLATE_DIR/signer-lnd.conf.template" \
            "$LNGET_LND_DIR/signer-lnd.conf" \
            "$EFFECTIVE_NETWORK" \
            "${SIGNER_DEBUG:-info}" \
            ""

        export SIGNER_CONF_PATH="$LNGET_LND_DIR/signer-lnd.conf"
        ;;
esac

export LITD_CONF_PATH="$LNGET_LND_DIR/litd.conf"

# --- Start containers ---

cd "$TEMPLATE_DIR"

echo "=== Starting litd ($MODE mode$([ "$REGTEST" = true ] && [ "$MODE" = "watchonly" ] && echo " + regtest")) ==="
echo "  Compose:  $COMPOSE_FILE"
echo "  Config:   $LITD_CONF_PATH"
echo "  Network:  $EFFECTIVE_NETWORK"
if [ -n "$PROFILE" ]; then
    echo "  Profile:  $PROFILE"
fi
if [ -n "$LITD_EXTRA_ARGS" ]; then
    echo "  Extra:    $LITD_EXTRA_ARGS"
fi
echo ""

# Build the docker-compose command.
CMD="docker compose -f $COMPOSE_FILE"

if [ "$BUILD" = true ]; then
    CMD="$CMD up --build"
else
    CMD="$CMD up"
fi

if [ "$DETACH" = true ]; then
    CMD="$CMD -d"
fi

echo "Running: $CMD"
eval "$CMD"

# When watchonly + regtest, join the regtest Docker network so the signer and
# litd can reach the existing bitcoind container.
if [ "$REGTEST" = true ] && [ "$MODE" = "watchonly" ]; then
    REGTEST_NETWORK="${DOCKER_NETWORK:-$(docker network ls --filter name=regtest --format '{{.Name}}' | head -1)}"
    if [ -n "$REGTEST_NETWORK" ]; then
        echo "Connecting containers to regtest network: $REGTEST_NETWORK"
        docker network connect "$REGTEST_NETWORK" litd-signer 2>/dev/null || true
        docker network connect "$REGTEST_NETWORK" litd 2>/dev/null || true
    else
        echo "Warning: No regtest Docker network found." >&2
        echo "Start regtest bitcoind first, or use --docker-network to specify." >&2
    fi
fi

if [ "$DETACH" = true ]; then
    echo ""
    echo "litd started in background."
    echo ""
    echo "Check logs:"
    echo "  docker logs -f litd"
    echo ""
    echo "Run commands:"
    echo "  skills/lnd/scripts/lncli.sh getinfo"
    echo ""

    if [ "$MODE" = "standalone" ] || [ "$MODE" = "regtest" ]; then
        echo "Next: create a wallet (if first run):"
        echo "  skills/lnd/scripts/create-wallet.sh --container litd"
    elif [ "$MODE" = "watchonly" ]; then
        echo "Next steps:"
        echo "  1. Set up signer wallet:"
        echo "     skills/lightning-security-module/scripts/setup-signer.sh --container litd-signer"
        echo "  2. Export credentials:"
        echo "     skills/lightning-security-module/scripts/export-credentials.sh --container litd-signer"
        echo "  3. Import credentials into litd and create watch-only wallet"
    fi
fi
