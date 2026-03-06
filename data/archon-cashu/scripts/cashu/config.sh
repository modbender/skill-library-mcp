#!/bin/bash
# Archon Cashu Wallet — Configuration
# Usage: config.sh [--set KEY VALUE]
set -e

CONFIG_FILE="${ARCHON_CASHU_CONFIG:-$HOME/.config/archon/cashu.env}"

# Source standard Archon env if available (for passphrase)
if [ -f "$HOME/.archon.env" ]; then
    source "$HOME/.archon.env"
fi

# Defaults — auto-discover cashu binary, inherit from environment
DEFAULT_CASHU_BIN="$(command -v cashu 2>/dev/null || echo "cashu")"
DEFAULT_MINT_URL="https://mint.minibits.cash/Bitcoin"
DEFAULT_LNBITS_ENV=""
DEFAULT_ARCHON_WALLET_PATH="${ARCHON_WALLET_PATH:-$HOME/.archon.wallet.json}"
# SECURITY: No default passphrase - must be set via ~/.archon.env or environment

create_default_config() {
    mkdir -p "$(dirname "$CONFIG_FILE")"
    
    # Check if passphrase is available
    if [ -z "$ARCHON_PASSPHRASE" ]; then
        echo "ERROR: ARCHON_PASSPHRASE not set."
        echo "Either:"
        echo "  1. Source ~/.archon.env first: source ~/.archon.env"
        echo "  2. Or set ARCHON_PASSPHRASE environment variable"
        echo ""
        echo "Run scripts/identity/create-id.sh to set up Archon identity."
        exit 1
    fi
    
    cat > "$CONFIG_FILE" << EOF
# Archon Cashu Wallet Configuration
# Created: $(date -Iseconds)
# CASHU_BIN — path to cashu CLI (auto-detected if on PATH, or: pip install cashu)
CASHU_BIN="${DEFAULT_CASHU_BIN}"
# CASHU_MINT_URL — default Cashu mint
CASHU_MINT_URL="${DEFAULT_MINT_URL}"
# LNBITS_ENV — optional, for LNbits integration
LNBITS_ENV=""
# ARCHON_WALLET_PATH — path to wallet.json
ARCHON_WALLET_PATH="${DEFAULT_ARCHON_WALLET_PATH}"
# SECURITY: Passphrase sourced from ~/.archon.env, not stored here
# ARCHON_PASSPHRASE is inherited from environment
EOF
    chmod 600 "$CONFIG_FILE"
    echo "Created config at $CONFIG_FILE"
}

load_config() {
    # Source archon env first for passphrase
    if [ -f "$HOME/.archon.env" ]; then
        source "$HOME/.archon.env"
    fi
    
    if [ ! -f "$CONFIG_FILE" ]; then
        create_default_config
    fi
    source "$CONFIG_FILE"
    
    # Verify passphrase is set
    if [ -z "$ARCHON_PASSPHRASE" ]; then
        echo "ERROR: ARCHON_PASSPHRASE not set."
        echo "Run: source ~/.archon.env"
        exit 1
    fi
    
    # Export for archon scripts
    export ARCHON_WALLET_PATH ARCHON_PASSPHRASE
    export MINT_URL="$CASHU_MINT_URL"
    
    # Load LNbits if available
    if [ -n "$LNBITS_ENV" ] && [ -f "$LNBITS_ENV" ]; then
        source "$LNBITS_ENV"
    fi
}

if [ "$1" = "--set" ] && [ -n "$2" ] && [ -n "$3" ]; then
    load_config
    sed -i "s|^$2=.*|$2=\"$3\"|" "$CONFIG_FILE"
    echo "Set $2=$3"
elif [ "$1" = "--create" ]; then
    create_default_config
else
    load_config
    echo "Archon Cashu Wallet Config"
    echo "========================="
    echo "Config:     $CONFIG_FILE"
    echo "Cashu CLI:  ${CASHU_BIN:-$DEFAULT_CASHU_BIN}"
    echo "Mint:       $CASHU_MINT_URL"
    echo "LNbits:     ${LNBITS_ENV:-<not set>}"
    echo "Wallet:     $ARCHON_WALLET_PATH"
fi
