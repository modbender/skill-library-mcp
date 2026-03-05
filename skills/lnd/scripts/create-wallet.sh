#!/usr/bin/env bash
# Create an encrypted lnd / litd wallet with secure credential storage.
#
# Container mode (default — auto-detects litd container):
#   create-wallet.sh                                      # Auto-detect litd
#   create-wallet.sh --container litd                     # Explicit container
#   create-wallet.sh --container litd --mode standalone   # Standalone in container
#   create-wallet.sh --container litd-signer              # Signer container
#
# Native mode:
#   create-wallet.sh --native                             # Local lnd
#   create-wallet.sh --native --signer-host 10.0.0.5:10012  # Watch-only native
#   create-wallet.sh --native --mode standalone           # Standalone native
#   create-wallet.sh --native --recover --seed-file ~/seed.txt
#
# Remote mode:
#   create-wallet.sh --rest-host remote.host --rest-port 8080
#
# Modes:
#   watchonly   (default) — imports accounts from signer, no seed on this machine.
#              Requires signer credentials imported via import-credentials.sh.
#   standalone  — generates seed locally (keys on disk, less secure)
#
# Stores credentials at:
#   ~/.lnget/lnd/wallet-password.txt  (mode 0600)
#   ~/.lnget/lnd/seed.txt             (mode 0600, standalone mode only)

set -e

LNGET_LND_DIR="${LNGET_LND_DIR:-$HOME/.lnget/lnd}"
LND_DIR="${LND_DIR:-$HOME/.lnd}"
NETWORK="testnet"
PASSWORD=""
RECOVER=false
SEED_FILE=""
REST_PORT=8080
REST_HOST="localhost"
MODE="watchonly"
SIGNER_HOST="${LND_SIGNER_HOST:-}"
CONTAINER=""
NATIVE=false

# Parse arguments.
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
        --password)
            PASSWORD="$2"
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
        --recover)
            RECOVER=true
            shift
            ;;
        --seed-file)
            SEED_FILE="$2"
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
            echo "Usage: create-wallet.sh [options]"
            echo ""
            echo "Create an encrypted lnd / litd wallet."
            echo ""
            echo "Connection options:"
            echo "  --container NAME    Create wallet in a Docker container"
            echo "  --native            Create wallet on local lnd process"
            echo "  --rest-host HOST    REST API host (default: localhost)"
            echo "  --rest-port PORT    REST API port (default: 8080)"
            echo ""
            echo "Wallet options:"
            echo "  --mode MODE         Wallet mode: watchonly (default) or standalone"
            echo "  --signer-host HOST  Signer RPC address (required for watchonly native)"
            echo "  --password PASS     Wallet passphrase (auto-generated if omitted)"
            echo "  --network NETWORK   Bitcoin network (default: testnet)"
            echo "  --lnddir DIR        lnd data directory (default: ~/.lnd)"
            echo "  --recover           Recover wallet from existing seed (standalone only)"
            echo "  --seed-file FILE    Path to seed file for recovery (standalone only)"
            echo ""
            echo "Modes:"
            echo "  watchonly    Import accounts from remote signer (no keys on this machine)"
            echo "  standalone   Generate seed locally (keys on disk, use for testing)"
            echo ""
            echo "Container auto-detection order: litd > litd-shared > lnd > lnd-shared"
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

    # If no container found and no explicit native flag, fall back to native.
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

# Watch-only mode validations (native only — container mode gets credentials
# from the signer container via Docker network).
if [ "$MODE" = "watchonly" ] && [ "$NATIVE" = true ]; then
    CREDS_DIR="$LNGET_LND_DIR/signer-credentials"

    if [ -z "$SIGNER_HOST" ]; then
        echo "Error: --signer-host is required in watchonly native mode." >&2
        echo "Example: create-wallet.sh --native --signer-host 10.0.0.5:10012" >&2
        echo "For container mode, signer credentials are managed via Docker." >&2
        exit 1
    fi

    if [ ! -f "$CREDS_DIR/accounts.json" ]; then
        echo "Error: Signer credentials not found at $CREDS_DIR/accounts.json" >&2
        echo "Run import-credentials.sh first to import the signer's credentials bundle." >&2
        exit 1
    fi

    if [ ! -f "$CREDS_DIR/tls.cert" ] || [ ! -f "$CREDS_DIR/admin.macaroon" ]; then
        echo "Error: Signer TLS cert or macaroon not found in $CREDS_DIR" >&2
        echo "Run import-credentials.sh first." >&2
        exit 1
    fi
fi

# Watch-only mode in container mode: check for accounts.json on host or in
# the signer container.
if [ "$MODE" = "watchonly" ] && [ -n "$CONTAINER" ]; then
    CREDS_DIR="$LNGET_LND_DIR/signer-credentials"

    if [ ! -f "$CREDS_DIR/accounts.json" ]; then
        echo "Error: Signer accounts not found at $CREDS_DIR/accounts.json" >&2
        echo "" >&2
        echo "Export credentials from the signer container first:" >&2
        echo "  skills/lightning-security-module/scripts/export-credentials.sh" >&2
        exit 1
    fi
fi

echo "=== Wallet Setup ==="
echo ""
if [ -n "$CONTAINER" ]; then
    echo "Container:  $CONTAINER"
else
    echo "Mode:       native"
fi
echo "Wallet:     $MODE"
echo "Network:    $NETWORK"
if [ "$NATIVE" = true ]; then
    echo "lnd dir:    $LND_DIR"
fi
echo "Creds dir:  $LNGET_LND_DIR"
if [ "$MODE" = "watchonly" ] && [ -n "$SIGNER_HOST" ]; then
    echo "Signer:     $SIGNER_HOST"
fi
echo ""

if [ "$MODE" = "standalone" ]; then
    echo "WARNING: Running in standalone mode. Private keys will be stored on this machine."
    echo "For production use, set up a remote signer with the lightning-security-module skill."
    echo ""
fi

# Create credential storage directory with restricted permissions.
mkdir -p "$LNGET_LND_DIR"
chmod 700 "$LNGET_LND_DIR"

PASSWORD_FILE="$LNGET_LND_DIR/wallet-password.txt"
SEED_OUTPUT="$LNGET_LND_DIR/seed.txt"

# Generate or use provided passphrase.
if [ -n "$PASSWORD" ]; then
    echo "Using provided passphrase."
else
    echo "Generating secure passphrase..."
    PASSWORD=$(openssl rand -base64 32 | tr -d '/+=' | head -c 32)
fi

# Store passphrase with restricted permissions on host.
echo -n "$PASSWORD" > "$PASSWORD_FILE"
chmod 600 "$PASSWORD_FILE"
echo "Passphrase saved to $PASSWORD_FILE (mode 0600)"
echo ""

# Copy password file into container if applicable.
if [ -n "$CONTAINER" ]; then
    docker cp "$PASSWORD_FILE" "$CONTAINER:/root/.lnd/wallet-password.txt"
    echo "Password file copied into container."
fi

# Container port for docker port mapping (litd exposes REST on 8080).
CONTAINER_PORT=8080
source "$SCRIPT_DIR/../../lib/rest.sh"

# For native mode, check if lnd is running; start it temporarily if needed.
if [ "$NATIVE" = true ]; then
    if ! lncli --network="$NETWORK" --lnddir="$LND_DIR" getinfo &>/dev/null 2>&1; then
        # Check if lnd is at least responding on REST (running but wallet not
        # created).
        if rest_call GET "/v1/state" &>/dev/null; then
            echo "lnd is running, waiting for wallet creation."
        elif pgrep -x lnd &>/dev/null; then
            echo "lnd is running but wallet is locked or not yet created."
        else
            echo "Starting lnd temporarily for wallet creation..."

            # Build launch args based on mode.
            LND_ARGS=(
                --lnddir="$LND_DIR"
                --bitcoin.active
                "--bitcoin.$NETWORK"
                --bitcoin.node=neutrino
                --neutrino.addpeer=btcd0.lightning.computer
                --neutrino.addpeer=mainnet1-btcd.zaphq.io
                --db.backend=sqlite
                "--restlisten=localhost:$REST_PORT"
                --rpclisten=localhost:10009
                --wallet-unlock-password-file="$PASSWORD_FILE"
                --wallet-unlock-allow-create
            )

            # Watch-only mode: must enable remote signer before wallet
            # creation. lnd requires remotesigner config to be present at
            # startup to accept a watch-only wallet via initwallet.
            if [ "$MODE" = "watchonly" ]; then
                CREDS_DIR="$LNGET_LND_DIR/signer-credentials"
                LND_ARGS+=(
                    --remotesigner.enable
                    "--remotesigner.rpchost=$SIGNER_HOST"
                    "--remotesigner.tlscertpath=$CREDS_DIR/tls.cert"
                    "--remotesigner.macaroonpath=$CREDS_DIR/admin.macaroon"
                )
            fi

            lnd "${LND_ARGS[@]}" &
            LND_PID=$!

            echo "Waiting for lnd to start (PID: $LND_PID)..."
            for i in {1..30}; do
                if rest_call GET "/v1/state" &>/dev/null; then
                    break
                fi
                if ! kill -0 "$LND_PID" 2>/dev/null; then
                    echo "Error: lnd exited unexpectedly." >&2
                    exit 1
                fi
                sleep 2
                echo "  Waiting... ($i/30)"
            done
            echo ""
        fi
    fi
else
    # Container mode: wait for REST API to be available inside container.
    wait_for_rest
fi

# Branch based on mode.
if [ "$MODE" = "watchonly" ]; then
    # --- Watch-only mode: import accounts from signer ---
    CREDS_DIR="$LNGET_LND_DIR/signer-credentials"
    ACCOUNTS_FILE="$CREDS_DIR/accounts.json"

    echo "=== Creating Watch-Only Wallet ==="
    echo "Importing accounts from: $ACCOUNTS_FILE"
    echo ""

    # Transform accounts from lncli format to initwallet format.
    # lncli outputs: {accounts: [{name, address_type, extended_public_key,
    # derivation_path, ...}]}
    # initwallet expects: {watch_only: {accounts: [{purpose, coin_type,
    # account, xpub}]}}
    WO_ACCOUNTS=$(jq '[.accounts[] | {
        purpose: (.derivation_path | split("/")[1] | rtrimstr("'"'"'") | tonumber),
        coin_type: (.derivation_path | split("/")[2] | rtrimstr("'"'"'") | tonumber),
        account: (.derivation_path | split("/")[3] | rtrimstr("'"'"'") | tonumber),
        xpub: .extended_public_key
    }]' "$ACCOUNTS_FILE")

    ACCOUNT_COUNT=$(echo "$WO_ACCOUNTS" | jq 'length')
    echo "Importing $ACCOUNT_COUNT accounts..."

    PAYLOAD=$(jq -n \
        --arg pass "$(echo -n "$PASSWORD" | base64)" \
        --argjson accounts "$WO_ACCOUNTS" \
        '{wallet_password: $pass, watch_only: {master_key_birthday_timestamp: "0", accounts: $accounts}}')

    RESPONSE=$(rest_call POST "/v1/initwallet" "$PAYLOAD")

    # Check for errors.
    ERROR=$(echo "$RESPONSE" | jq -r '.message // empty' 2>/dev/null)
    if [ -n "$ERROR" ]; then
        echo "Error creating watch-only wallet: $ERROR" >&2
        exit 1
    fi

    echo "Watch-only wallet created successfully!"
    echo "No seed or private keys stored on this machine."
    echo ""
    echo "=== Credential Locations ==="
    echo "  Passphrase:  $PASSWORD_FILE"
    echo "  Accounts:    $ACCOUNTS_FILE"
    echo ""
    echo "Next steps:"
    if [ -n "$CONTAINER" ]; then
        echo "  1. Check status: skills/lnd/scripts/lncli.sh getinfo"
        echo "  2. Fund wallet: skills/lnd/scripts/lncli.sh newaddress p2tr"
    else
        echo "  1. Start lnd: skills/lnd/scripts/start-lnd.sh --native --signer-host $SIGNER_HOST"
        echo "  2. Fund wallet: skills/lnd/scripts/lncli.sh newaddress p2tr"
    fi

elif [ "$MODE" = "standalone" ]; then
    # --- Standalone mode: generate seed locally ---

    if [ "$RECOVER" = true ]; then
        echo "=== Recovering Wallet ==="
        if [ -z "$SEED_FILE" ]; then
            echo "Error: --seed-file required for recovery" >&2
            exit 1
        fi
        if [ ! -f "$SEED_FILE" ]; then
            echo "Error: Seed file not found: $SEED_FILE" >&2
            exit 1
        fi

        # Read seed words from file.
        SEED_WORDS=$(cat "$SEED_FILE" | tr '\n' ' ' | xargs)
        SEED_JSON=$(echo "$SEED_WORDS" | tr ' ' '\n' | jq -R . | jq -s .)

        # Build recovery request.
        PAYLOAD=$(jq -n \
            --arg pass "$(echo -n "$PASSWORD" | base64)" \
            --argjson seed "$SEED_JSON" \
            '{wallet_password: $pass, cipher_seed_mnemonic: $seed}')

        RESPONSE=$(rest_call POST "/v1/initwallet" "$PAYLOAD")

        # Check for errors.
        ERROR=$(echo "$RESPONSE" | jq -r '.message // empty' 2>/dev/null)
        if [ -n "$ERROR" ]; then
            echo "Error recovering wallet: $ERROR" >&2
            exit 1
        fi

        echo "Wallet recovered successfully."
    else
        echo "=== Creating New Wallet (Standalone) ==="

        # Generate seed first.
        echo "Generating wallet seed..."
        SEED_RESPONSE=$(rest_call GET "/v1/genseed")

        # Extract mnemonic.
        MNEMONIC=$(echo "$SEED_RESPONSE" | jq -r '.cipher_seed_mnemonic[]' 2>/dev/null)
        if [ -z "$MNEMONIC" ] || [ "$MNEMONIC" = "null" ]; then
            echo "Error: Failed to generate seed." >&2
            echo "Response: $SEED_RESPONSE" >&2
            exit 1
        fi

        # Store seed with restricted permissions on host.
        echo "$MNEMONIC" > "$SEED_OUTPUT"
        chmod 600 "$SEED_OUTPUT"
        echo "Seed mnemonic saved to $SEED_OUTPUT (mode 0600)"
        echo ""

        # Initialize wallet with password and seed.
        SEED_JSON=$(echo "$MNEMONIC" | jq -R . | jq -s .)
        PAYLOAD=$(jq -n \
            --arg pass "$(echo -n "$PASSWORD" | base64)" \
            --argjson seed "$SEED_JSON" \
            '{wallet_password: $pass, cipher_seed_mnemonic: $seed}')

        RESPONSE=$(rest_call POST "/v1/initwallet" "$PAYLOAD")

        # Check for errors.
        ERROR=$(echo "$RESPONSE" | jq -r '.message // empty' 2>/dev/null)
        if [ -n "$ERROR" ]; then
            echo "Error creating wallet: $ERROR" >&2
            exit 1
        fi

        echo "Wallet created successfully!"
    fi

    echo ""
    echo "=== Credential Locations ==="
    echo "  Passphrase: $PASSWORD_FILE"
    if [ "$RECOVER" = false ]; then
        echo "  Seed:       $SEED_OUTPUT"
    fi
    echo ""
    echo "IMPORTANT: Both files are stored with restricted permissions (0600)."
    echo "The seed mnemonic is your wallet backup. Keep it safe."
    echo "For production use, set up a remote signer with the lightning-security-module skill."
    echo ""
    echo "Next steps:"
    if [ -n "$CONTAINER" ]; then
        echo "  1. Check status: skills/lnd/scripts/lncli.sh getinfo"
        echo "  2. Fund wallet: skills/lnd/scripts/lncli.sh newaddress p2tr"
    else
        echo "  1. Start lnd: skills/lnd/scripts/start-lnd.sh --native --mode standalone"
        echo "  2. Fund wallet: skills/lnd/scripts/lncli.sh newaddress p2tr"
    fi
fi
