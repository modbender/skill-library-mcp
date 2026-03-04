#!/usr/bin/env bash
# _common.sh — Shared constants and helpers for DeAI scripts
# All contract addresses are env-overridable.

# Defaults
export DEAI_CHAIN_ID="${DEAI_CHAIN_ID:-8453}"
export DEAI_RPC_URL="${DEAI_RPC_URL:-https://mainnet.base.org}"
export DEAI_INDEXER_URL="${DEAI_INDEXER_URL:-http://localhost:3001}"

# Auth: Foundry encrypted keystore only.
#   DEAI_ACCOUNT        — keystore account name (e.g. "deai-agent")
#   DEAI_PASSWORD_FILE  — optional, for non-interactive use (file should be chmod 0600)
#   Setup: cast wallet import <name> --interactive
export DEAI_ACCOUNT="${DEAI_ACCOUNT:-}"
export DEAI_PASSWORD_FILE="${DEAI_PASSWORD_FILE:-}"

# Core contracts
export DEAI_ASSET_AUCTION_ADDR="${DEAI_ASSET_AUCTION_ADDR:-}"
export DEAI_ESCROW_ADDR="${DEAI_ESCROW_ADDR:-}"
export DEAI_IDENTITY_ADDR="${DEAI_IDENTITY_ADDR:-}"
export DEAI_REPUTATION_ADDR="${DEAI_REPUTATION_ADDR:-}"
export DEAI_ENDORSEMENT_ADDR="${DEAI_ENDORSEMENT_ADDR:-}"

# Registries
export DEAI_ADAPTER_REGISTRY_ADDR="${DEAI_ADAPTER_REGISTRY_ADDR:-}"
export DEAI_PAYMENT_TOKEN_WHITELIST_ADDR="${DEAI_PAYMENT_TOKEN_WHITELIST_ADDR:-}"

# Asset adapters
export DEAI_ERC20_ADAPTER_ADDR="${DEAI_ERC20_ADAPTER_ADDR:-}"
export DEAI_ERC721_ADAPTER_ADDR="${DEAI_ERC721_ADAPTER_ADDR:-}"
export DEAI_ERC1155_ADAPTER_ADDR="${DEAI_ERC1155_ADAPTER_ADDR:-}"
export DEAI_ERC4626_ADAPTER_ADDR="${DEAI_ERC4626_ADAPTER_ADDR:-}"

# Tokens — Base USDC default
export DEAI_USDC_ADDR="${DEAI_USDC_ADDR:-0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913}"

# Short aliases used inside scripts
ASSET_AUCTION_ADDR="$DEAI_ASSET_AUCTION_ADDR"
ESCROW_ADDR="$DEAI_ESCROW_ADDR"
IDENTITY_ADDR="$DEAI_IDENTITY_ADDR"
USDC_ADDR="$DEAI_USDC_ADDR"

# ─── Input Validation ─────────────────────────

# Validate that a value is a non-negative integer (uint256)
assert_uint() {
  local label="$1" val="$2"
  if [[ ! "$val" =~ ^[0-9]+$ ]]; then
    echo "ERROR: $label must be a non-negative integer, got: '$val'" >&2
    exit 1
  fi
}

# Validate that a value is a non-negative decimal number
assert_decimal() {
  local label="$1" val="$2"
  if [[ ! "$val" =~ ^[0-9]+\.?[0-9]*$ ]]; then
    echo "ERROR: $label must be a number, got: '$val'" >&2
    exit 1
  fi
}

# Validate that a value looks like an Ethereum address (0x + 40 hex chars)
assert_address() {
  local label="$1" val="$2"
  if [[ ! "$val" =~ ^0x[0-9a-fA-F]{40}$ ]]; then
    echo "ERROR: $label must be a valid address (0x + 40 hex), got: '$val'" >&2
    exit 1
  fi
}

# ─── Helpers ───────────────────────────────────

# Resolve token symbol → address
resolve_token() {
  local sym="${1,,}"
  case "$sym" in
    usdc) echo "$DEAI_USDC_ADDR" ;;
    *)    echo "$1" ;; # assume raw address
  esac
}

# Resolve asset type → adapter address
resolve_adapter() {
  local atype="${1,,}"
  case "$atype" in
    erc20)   echo "$DEAI_ERC20_ADAPTER_ADDR" ;;
    erc721)  echo "$DEAI_ERC721_ADAPTER_ADDR" ;;
    erc1155) echo "$DEAI_ERC1155_ADAPTER_ADDR" ;;
    erc4626) echo "$DEAI_ERC4626_ADAPTER_ADDR" ;;
    *)       echo "$1" ;; # assume raw address
  esac
}

# Build cast flags as an array (avoids word-splitting injection).
# Populates global CAST_FLAGS array — callers use "${CAST_FLAGS[@]}".
build_cast_flags() {
  CAST_FLAGS=(--rpc-url "$DEAI_RPC_URL" --account "$DEAI_ACCOUNT")
  if [[ -n "${DEAI_PASSWORD_FILE:-}" ]]; then
    if [[ ! -f "$DEAI_PASSWORD_FILE" ]]; then
      echo "ERROR: DEAI_PASSWORD_FILE does not exist: $DEAI_PASSWORD_FILE" >&2
      exit 1
    fi
    CAST_FLAGS+=(--password-file "$DEAI_PASSWORD_FILE")
  fi
}

# Get wallet address from keystore
get_wallet() {
  cast wallet address --account "$DEAI_ACCOUNT" 2>/dev/null || echo ""
}

# Chain name for display
chain_name() {
  case "$DEAI_CHAIN_ID" in
    8453)  echo "Base" ;;
    31337) echo "Localhost" ;;
    *)     echo "Chain $DEAI_CHAIN_ID" ;;
  esac
}

# Explorer URL helpers
explorer_base() {
  case "$DEAI_CHAIN_ID" in
    8453)  echo "https://basescan.org" ;;
    *)     echo "https://basescan.org" ;;
  esac
}

explorer_tx_url() {
  echo "$(explorer_base)/tx/${1:?}"
}

explorer_addr_url() {
  echo "$(explorer_base)/address/${1:?}"
}

# Format wei to human-readable (6 decimals for USDC)
format_amount() {
  local wei="$1"
  local decimals="${2:-6}"
  assert_uint "wei value" "$wei"
  assert_uint "decimals" "$decimals"
  python3 -c "print(f'{int($wei) / 10**$decimals:.{$decimals}f}')" 2>/dev/null || echo "$wei"
}

# Convert human-readable amount to raw token units (e.g. 50 → 50000000 for 6-decimal USDC)
to_wei() {
  local amount="$1"
  local decimals="${2:-6}"
  assert_decimal "amount" "$amount"
  assert_uint "decimals" "$decimals"
  python3 -c "print(int(float($amount) * 10**$decimals))" 2>/dev/null || echo "$amount"
}

# Alias: convert raw units back to human-readable (same as format_amount)
to_token_units() {
  format_amount "$1" "${2:-6}"
}

# Resolve token symbol → decimals
token_decimals() {
  local sym="${1,,}"
  case "$sym" in
    usdc) echo "6" ;;
    *)    echo "6" ;; # default to 6 for stablecoins
  esac
}
