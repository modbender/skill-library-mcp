#!/usr/bin/env bash
set -euo pipefail

API_BASE_DEFAULT="https://x402pulse.xyz"
API_BASE="${API_BASE:-$API_BASE_DEFAULT}"

REGISTRY_DEFAULT="0xe61C615743A02983A46aFF66Db035297e8a43846"
TOKEN_DEFAULT="0x21111B39A502335aC7e45c4574Dd083A69258b07"

REGISTRY_ADDRESS="${PULSE_REGISTRY_ADDRESS:-$REGISTRY_DEFAULT}"
PULSE_TOKEN_ADDRESS="${PULSE_TOKEN_ADDRESS:-$TOKEN_DEFAULT}"

usage() {
  cat >&2 <<EOF
Usage:
  Direct on-chain (cast):
    $0 --direct <amountWei>

Env:
  BASE_RPC_URL              RPC URL (default: https://mainnet.base.org)
  PRIVATE_KEY               Private key (required for --direct)
  PULSE_REGISTRY_ADDRESS    Override registry (default: $REGISTRY_DEFAULT)
  PULSE_TOKEN_ADDRESS       Override token (default: $TOKEN_DEFAULT)
EOF
}

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "$1" == "--direct" ]]; then
  if [[ $# -ne 2 ]]; then
    usage
    exit 2
  fi

  AMOUNT="$2"
  if [[ ! "$AMOUNT" =~ ^[0-9]+$ ]] || [[ "$AMOUNT" == "0" ]]; then
    echo "Error: Amount must be a positive integer (wei units)." >&2
    exit 1
  fi

  BASE_RPC_URL="${BASE_RPC_URL:-https://mainnet.base.org}"
  if [[ -z "${PRIVATE_KEY:-}" ]]; then
    echo "Error: PRIVATE_KEY is required for --direct mode." >&2
    exit 1
  fi

  echo "[agent-pulse] Direct mode: approving registry then pulsing on Base mainnet..." >&2

  # Approve registry to transfer PULSE.
  cast send --rpc-url "$BASE_RPC_URL" --private-key "$PRIVATE_KEY" \
    "$PULSE_TOKEN_ADDRESS" \
    "approve(address,uint256)(bool)" \
    "$REGISTRY_ADDRESS" "$AMOUNT" >&2

  # Call pulse(amount) on registry.
  cast send --rpc-url "$BASE_RPC_URL" --private-key "$PRIVATE_KEY" \
    "$REGISTRY_ADDRESS" \
    "pulse(uint256)" "$AMOUNT"

  exit 0
fi

echo "Error: Only --direct mode is supported on Base mainnet." >&2
usage
exit 2
