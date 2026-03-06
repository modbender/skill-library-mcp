#!/bin/bash
# OpenclawCash CLI Tool
# Usage: ./agentwalletapi.sh <command> [options]
#
# Requirements: curl (jq optional for pretty output)
# Sensitive env var: AGENTWALLETAPI_KEY (in .env)
#
# Commands:
#   wallets                     List all wallets
#   wallet <walletId|publicWalletId|walletLabel> [chain]   Get one wallet detail with balances
#   create <label> [network] <passphraseEnvVar> [--yes]    Create a wallet (default network: sepolia)
#   import <label> <network> [privateKey|-] [--yes]   Import wallet (network: mainnet|solana-mainnet)
#   transactions <walletId|publicWalletId> [chain]     List merged transaction history for a wallet
#   balance <walletId|publicWalletId> [token] [chain]  Check balances for a wallet
#   transfer <walletId|publicWalletId> <to> <amount> [token] [chain] [--yes]   Send native/token transfer
#   tokens [network] [chain]            List supported tokens (default: mainnet)
#   quote <network> <tokenIn> <tokenOut> <amountInBaseUnits> [chain]   Get swap quote
#   swap <walletId|publicWalletId> <tokenIn> <tokenOut> <amountInBaseUnits> [slippage] [chain] [--yes]
#   approve <walletId|publicWalletId> <tokenAddress> <spender> <amountBaseUnits> [chain] [--yes]   Approve ERC-20 allowance

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$SKILL_DIR/.env"

if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found. Run setup first:"
    echo "  bash $SKILL_DIR/scripts/setup.sh"
    exit 1
fi

source "$ENV_FILE"

if [ -z "$AGENTWALLETAPI_KEY" ] || [ "$AGENTWALLETAPI_KEY" = "occ_your_api_key" ]; then
    echo "Error: API key not configured. Edit $ENV_FILE and set AGENTWALLETAPI_KEY."
    exit 1
fi

if ! command -v curl >/dev/null 2>&1; then
    echo "Error: curl is required but not installed."
    exit 1
fi

BASE_URL="${AGENTWALLETAPI_URL:-https://openclawcash.com}"

FORCE_RISKY=0
FILTERED_ARGS=()
for arg in "$@"; do
    if [ "$arg" = "--yes" ]; then
        FORCE_RISKY=1
    else
        FILTERED_ARGS+=("$arg")
    fi
done
set -- "${FILTERED_ARGS[@]}"
COMMAND="$1"

json_escape_var() {
    DEST_VAR="$1"
    VALUE="${2-}"
    VALUE="${VALUE//\\/\\\\}"
    VALUE="${VALUE//\"/\\\"}"
    VALUE="${VALUE//$'\n'/\\n}"
    VALUE="${VALUE//$'\r'/\\r}"
    VALUE="${VALUE//$'\t'/\\t}"
    printf -v "$DEST_VAR" '%s' "$VALUE"
}

url_encode_var() {
    DEST_VAR="$1"
    VALUE="${2-}"
    ENCODED=""
    for (( i=0; i<${#VALUE}; i++ )); do
        CHAR="${VALUE:i:1}"
        case "$CHAR" in
            [a-zA-Z0-9.~_-]) ENCODED+="$CHAR" ;;
            *)
                printf -v HEX '%%%02X' "'$CHAR"
                ENCODED+="$HEX"
                ;;
        esac
    done
    printf -v "$DEST_VAR" '%s' "$ENCODED"
}

append_query_param() {
    DEST_VAR="$1"
    KEY="$2"
    RAW_VALUE="$3"
    URL="${!DEST_VAR}"
    url_encode_var ENCODED_VALUE "$RAW_VALUE"
    if [[ "$URL" == *\?* ]]; then
        URL="${URL}&${KEY}=${ENCODED_VALUE}"
    else
        URL="${URL}?${KEY}=${ENCODED_VALUE}"
    fi
    printf -v "$DEST_VAR" '%s' "$URL"
}

require_uint() {
    NAME="$1"
    VALUE="$2"
    if ! [[ "$VALUE" =~ ^[0-9]+$ ]]; then
        echo "Error: $NAME must be an unsigned integer."
        exit 1
    fi
}

is_uint() {
    VALUE="$1"
    [[ "$VALUE" =~ ^[0-9]+$ ]]
}

is_public_wallet_id() {
    VALUE="$1"
    [[ "$VALUE" =~ ^[A-Za-z0-9]{6,12}$ ]]
}

append_wallet_selector_query() {
    DEST_VAR="$1"
    SELECTOR="$2"
    if is_uint "$SELECTOR" || is_public_wallet_id "$SELECTOR"; then
        append_query_param "$DEST_VAR" "walletId" "$SELECTOR"
    else
        append_query_param "$DEST_VAR" "walletLabel" "$SELECTOR"
    fi
}

append_wallet_id_json_field() {
    DEST_VAR="$1"
    SELECTOR="$2"
    BODY="${!DEST_VAR}"
    if is_uint "$SELECTOR"; then
        BODY="$BODY\"walletId\": $SELECTOR"
    else
        json_escape_var WALLET_ID_ESC "$SELECTOR"
        BODY="$BODY\"walletId\": \"$WALLET_ID_ESC\""
    fi
    printf -v "$DEST_VAR" '%s' "$BODY"
}

require_decimal() {
    NAME="$1"
    VALUE="$2"
    if ! [[ "$VALUE" =~ ^[0-9]+([.][0-9]+)?$ ]]; then
        echo "Error: $NAME must be a number."
        exit 1
    fi
}

pretty_print_json() {
    if command -v jq >/dev/null 2>&1; then
        jq . 2>/dev/null || cat
    else
        cat
    fi
}

confirm_risky_action() {
    ACTION="$1"
    if [ "$FORCE_RISKY" -eq 1 ]; then
        return 0
    fi

    if [ ! -t 0 ]; then
        echo "Error: $ACTION is a high-risk action. Re-run with --yes to confirm."
        exit 1
    fi

    echo "WARNING: $ACTION can move funds or import sensitive keys."
    echo "Target API host: $BASE_URL"
    printf "Type YES to continue: "
    read -r ANSWER
    if [ "$ANSWER" != "YES" ]; then
        echo "Cancelled."
        exit 1
    fi
}

case "$COMMAND" in
    wallets)
        curl -s -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            "$BASE_URL/api/agent/wallets" | pretty_print_json
        ;;

    wallet)
        SELECTOR="$2"
        CHAIN="$3"
        if [ -z "$SELECTOR" ]; then
            echo "Usage: agentwalletapi.sh wallet <walletId|publicWalletId|walletLabel> [chain]"
            exit 1
        fi
        URL="$BASE_URL/api/agent/wallet"
        append_wallet_selector_query URL "$SELECTOR"
        if [ -n "$CHAIN" ]; then
            append_query_param URL "chain" "$CHAIN"
        fi
        curl -s -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            "$URL" | pretty_print_json
        ;;

    create)
        confirm_risky_action "Wallet creation"
        LABEL="$2"
        NETWORK="${3:-sepolia}"
        PASSPHRASE_ENV_VAR="$4"
        if [ -z "$LABEL" ] || [ -z "$PASSPHRASE_ENV_VAR" ]; then
            echo "Usage: agentwalletapi.sh create <label> [network] <passphraseEnvVar> [--yes]"
            echo "  network options: sepolia | mainnet | solana-devnet | solana-testnet | solana-mainnet"
            echo "  Example:"
            echo "    export WALLET_EXPORT_PASSPHRASE_OPS='your-strong-passphrase'"
            echo "    agentwalletapi.sh create \"Ops Wallet\" sepolia WALLET_EXPORT_PASSPHRASE_OPS --yes"
            exit 1
        fi
        PASSPHRASE_VALUE="${!PASSPHRASE_ENV_VAR}"
        if [ -z "$PASSPHRASE_VALUE" ]; then
            echo "Error: env var $PASSPHRASE_ENV_VAR is not set."
            echo "Store the wallet export passphrase in an env var first, then retry."
            exit 1
        fi
        json_escape_var LABEL_ESC "$LABEL"
        json_escape_var NETWORK_ESC "$NETWORK"
        json_escape_var PASSPHRASE_ESC "$PASSPHRASE_VALUE"
        json_escape_var PASSPHRASE_ENV_ESC "$PASSPHRASE_ENV_VAR"
        BODY="{\"label\":\"$LABEL_ESC\",\"network\":\"$NETWORK_ESC\",\"exportPassphrase\":\"$PASSPHRASE_ESC\",\"exportPassphraseStorageType\":\"env\",\"exportPassphraseStorageRef\":\"$PASSPHRASE_ENV_ESC\",\"confirmExportPassphraseSaved\":true}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/wallets/create" | pretty_print_json
        unset PASSPHRASE_VALUE
        ;;

    import)
        confirm_risky_action "Wallet import"
        if [ "$FORCE_RISKY" -eq 1 ]; then
            echo "Import confirmation accepted via --yes."
        fi
        LABEL="$2"
        NETWORK="$3"
        PRIVATE_KEY="$4"
        if [ -z "$LABEL" ] || [ -z "$NETWORK" ]; then
            echo "Usage: agentwalletapi.sh import <label> <network> [privateKey|-] [--yes]"
            echo "  network options: mainnet | solana-mainnet"
            echo "  pass '-' to read private key from stdin (recommended for automation)"
            exit 1
        fi
        if [ "$PRIVATE_KEY" = "-" ]; then
            if [ -t 0 ]; then
                echo "Error: private key input set to '-' but stdin is empty."
                echo "Example: printf '%s' '<private_key>' | agentwalletapi.sh import <label> <network> - --yes"
                exit 1
            fi
            IFS= read -r PRIVATE_KEY
        elif [ -n "$PRIVATE_KEY" ]; then
            echo "WARNING: passing private key as a CLI argument can leak in shell history/process logs."
            echo "Safer options: omit [privateKey] for hidden prompt, or pass '-' and pipe via stdin."
        fi
        if [ -z "$PRIVATE_KEY" ]; then
            if [ ! -t 0 ]; then
                echo "Error: private key missing. Provide as argument or run interactively to be prompted."
                exit 1
            fi
            printf "Enter private key (input hidden): "
            stty -echo
            read -r PRIVATE_KEY
            stty echo
            echo ""
        fi
        json_escape_var LABEL_ESC "$LABEL"
        json_escape_var NETWORK_ESC "$NETWORK"
        json_escape_var PRIVATE_KEY_ESC "$PRIVATE_KEY"
        BODY="{\"label\":\"$LABEL_ESC\",\"network\":\"$NETWORK_ESC\",\"privateKey\":\"$PRIVATE_KEY_ESC\"}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/wallets/import" | pretty_print_json
        unset PRIVATE_KEY
        unset BODY
        ;;

    transactions)
        WALLET_ID="$2"
        CHAIN="$3"
        if [ -z "$WALLET_ID" ]; then
            echo "Usage: agentwalletapi.sh transactions <walletId|publicWalletId> [chain]"
            exit 1
        fi
        URL="$BASE_URL/api/agent/transactions"
        append_query_param URL "walletId" "$WALLET_ID"
        if [ -n "$CHAIN" ]; then
            append_query_param URL "chain" "$CHAIN"
        fi
        curl -s -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            "$URL" | pretty_print_json
        ;;

    balance)
        WALLET_ID="$2"
        TOKEN_FILTER="$3"
        CHAIN="$4"
        if [ -z "$WALLET_ID" ]; then
            echo "Usage: agentwalletapi.sh balance <walletId|publicWalletId> [token] [chain]"
            exit 1
        fi
        BODY="{"
        append_wallet_id_json_field BODY "$WALLET_ID"
        if [ -n "$TOKEN_FILTER" ]; then
            json_escape_var TOKEN_FILTER_ESC "$TOKEN_FILTER"
            BODY="$BODY, \"token\": \"$TOKEN_FILTER_ESC\""
        fi
        if [ -n "$CHAIN" ]; then
            json_escape_var CHAIN_ESC "$CHAIN"
            BODY="$BODY, \"chain\": \"$CHAIN_ESC\""
        fi
        BODY="$BODY}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/token-balance" | pretty_print_json
        ;;

    transfer)
        confirm_risky_action "Transfer"
        WALLET_ID="$2"
        TO="$3"
        AMOUNT="$4"
        TOKEN="${5:-ETH}"
        CHAIN="$6"
        if [ -z "$WALLET_ID" ] || [ -z "$TO" ] || [ -z "$AMOUNT" ]; then
            echo "Usage: agentwalletapi.sh transfer <walletId|publicWalletId> <to> <amount> [token] [chain]"
            echo "  token defaults to the wallet's native token (ETH/SOL) if not specified"
            exit 1
        fi
        json_escape_var TO_ESC "$TO"
        json_escape_var AMOUNT_ESC "$AMOUNT"
        BODY="{"
        append_wallet_id_json_field BODY "$WALLET_ID"
        BODY="$BODY, \"to\": \"$TO_ESC\", \"amount\": \"$AMOUNT_ESC\""
        if [ "$TOKEN" != "ETH" ]; then
            json_escape_var TOKEN_ESC "$TOKEN"
            BODY="$BODY, \"token\": \"$TOKEN_ESC\""
        fi
        if [ -n "$CHAIN" ]; then
            json_escape_var CHAIN_ESC "$CHAIN"
            BODY="$BODY, \"chain\": \"$CHAIN_ESC\""
        fi
        BODY="$BODY}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/transfer" | pretty_print_json
        ;;

    tokens)
        NETWORK="${2:-mainnet}"
        CHAIN="$3"
        URL="$BASE_URL/api/agent/supported-tokens"
        append_query_param URL "network" "$NETWORK"
        if [ -n "$CHAIN" ]; then
            append_query_param URL "chain" "$CHAIN"
        fi
        curl -s "$URL" | pretty_print_json
        ;;

    quote)
        NETWORK="$2"
        TOKEN_IN="$3"
        TOKEN_OUT="$4"
        AMOUNT_IN="$5"
        CHAIN="$6"
        if [ -z "$NETWORK" ] || [ -z "$TOKEN_IN" ] || [ -z "$TOKEN_OUT" ] || [ -z "$AMOUNT_IN" ]; then
            echo "Usage: agentwalletapi.sh quote <network> <tokenIn> <tokenOut> <amountInBaseUnits> [chain]"
            exit 1
        fi
        json_escape_var TOKEN_IN_ESC "$TOKEN_IN"
        json_escape_var TOKEN_OUT_ESC "$TOKEN_OUT"
        json_escape_var AMOUNT_IN_ESC "$AMOUNT_IN"
        BODY="{\"tokenIn\":\"$TOKEN_IN_ESC\",\"tokenOut\":\"$TOKEN_OUT_ESC\",\"amountIn\":\"$AMOUNT_IN_ESC\""
        if [ -n "$CHAIN" ]; then
            json_escape_var CHAIN_ESC "$CHAIN"
            BODY="$BODY, \"chain\": \"$CHAIN_ESC\""
        fi
        BODY="$BODY}"
        URL="$BASE_URL/api/agent/quote"
        append_query_param URL "network" "$NETWORK"
        curl -s -X POST \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$URL" | pretty_print_json
        ;;

    swap)
        confirm_risky_action "Swap"
        WALLET_ID="$2"
        TOKEN_IN="$3"
        TOKEN_OUT="$4"
        AMOUNT_IN="$5"
        SLIPPAGE="${6:-0.5}"
        CHAIN="$7"
        if [ -z "$WALLET_ID" ] || [ -z "$TOKEN_IN" ] || [ -z "$TOKEN_OUT" ] || [ -z "$AMOUNT_IN" ]; then
            echo "Usage: agentwalletapi.sh swap <walletId|publicWalletId> <tokenIn> <tokenOut> <amountInBaseUnits> [slippage] [chain]"
            exit 1
        fi
        require_decimal "slippage" "$SLIPPAGE"
        json_escape_var TOKEN_IN_ESC "$TOKEN_IN"
        json_escape_var TOKEN_OUT_ESC "$TOKEN_OUT"
        json_escape_var AMOUNT_IN_ESC "$AMOUNT_IN"
        BODY="{"
        append_wallet_id_json_field BODY "$WALLET_ID"
        BODY="$BODY,\"tokenIn\":\"$TOKEN_IN_ESC\",\"tokenOut\":\"$TOKEN_OUT_ESC\",\"amountIn\":\"$AMOUNT_IN_ESC\",\"slippage\":$SLIPPAGE"
        if [ -n "$CHAIN" ]; then
            json_escape_var CHAIN_ESC "$CHAIN"
            BODY="$BODY, \"chain\": \"$CHAIN_ESC\""
        fi
        BODY="$BODY}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/swap" | pretty_print_json
        ;;

    approve)
        confirm_risky_action "Token approval"
        WALLET_ID="$2"
        TOKEN_ADDRESS="$3"
        SPENDER="$4"
        AMOUNT="$5"
        CHAIN="$6"
        if [ -z "$WALLET_ID" ] || [ -z "$TOKEN_ADDRESS" ] || [ -z "$SPENDER" ] || [ -z "$AMOUNT" ]; then
            echo "Usage: agentwalletapi.sh approve <walletId|publicWalletId> <tokenAddress> <spender> <amountBaseUnits> [chain]"
            exit 1
        fi
        json_escape_var TOKEN_ADDRESS_ESC "$TOKEN_ADDRESS"
        json_escape_var SPENDER_ESC "$SPENDER"
        json_escape_var AMOUNT_ESC "$AMOUNT"
        BODY="{"
        append_wallet_id_json_field BODY "$WALLET_ID"
        BODY="$BODY,\"tokenAddress\":\"$TOKEN_ADDRESS_ESC\",\"spender\":\"$SPENDER_ESC\",\"amount\":\"$AMOUNT_ESC\""
        if [ -n "$CHAIN" ]; then
            json_escape_var CHAIN_ESC "$CHAIN"
            BODY="$BODY, \"chain\": \"$CHAIN_ESC\""
        fi
        BODY="$BODY}"
        curl -s -X POST \
            -H "X-Agent-Key: $AGENTWALLETAPI_KEY" \
            -H "Content-Type: application/json" \
            -d "$BODY" \
            "$BASE_URL/api/agent/approve" | pretty_print_json
        ;;

    *)
        echo "OpenclawCash CLI Tool"
        echo ""
        echo "Usage: agentwalletapi.sh <command> [options]"
        echo ""
        echo "Commands:"
        echo "  wallets                                    List all wallets"
        echo "  wallet <walletId|publicWalletId|walletLabel> [chain]  Get one wallet detail with balances"
        echo "  create <label> [network] <passphraseEnvVar> [--yes]  Create wallet (default network: sepolia)"
        echo "  import <label> <network> [privateKey] [--yes]      Import wallet (mainnet|solana-mainnet)"
        echo "  transactions <walletId|publicWalletId> [chain]    List wallet transaction history"
        echo "  balance <walletId|publicWalletId> [token] [chain] Check balances"
        echo "  transfer <walletId|publicWalletId> <to> <amount> [token] [chain] [--yes]  Send native/token transfer"
        echo "  tokens [network] [chain]                           List supported tokens"
        echo "  quote <network> <tokenIn> <tokenOut> <amountInBaseUnits> [chain]  Get swap quote"
        echo "  swap <walletId|publicWalletId> <tokenIn> <tokenOut> <amountInBaseUnits> [slippage] [chain] [--yes]  Execute swap"
        echo "  approve <walletId|publicWalletId> <tokenAddress> <spender> <amountBaseUnits> [chain] [--yes]  Approve allowance"
        echo ""
        echo "Examples:"
        echo "  agentwalletapi.sh wallets"
        echo "  export WALLET_EXPORT_PASSPHRASE_OPS='your-strong-passphrase'"
        echo "  agentwalletapi.sh create 'Ops Wallet' sepolia WALLET_EXPORT_PASSPHRASE_OPS --yes"
        echo "  agentwalletapi.sh import 'Treasury Imported' mainnet --yes"
        echo "  agentwalletapi.sh transactions 2"
        echo "  agentwalletapi.sh balance 2"
        echo "  agentwalletapi.sh transfer 2 0xRecipient 0.01 --yes"
        echo "  agentwalletapi.sh transfer 2 0xRecipient 100 USDC --yes"
        echo "  agentwalletapi.sh tokens mainnet"
        echo "  agentwalletapi.sh quote mainnet WETH USDC 10000000000000000"
        echo "  agentwalletapi.sh swap 2 ETH USDC 10000000000000000 0.5 --yes"
        echo "  agentwalletapi.sh approve 2 0xA0b86991... 0xSpender... 1000000000 --yes"
        ;;
esac
