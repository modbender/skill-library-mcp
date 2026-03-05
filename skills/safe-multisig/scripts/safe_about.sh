#!/usr/bin/env bash
set -euo pipefail

TX_SERVICE_URL=""
CHAIN=""

# Chain slug → Safe Transaction Service gateway slug
# Must match TX_SERVICE_SLUGS in safe_lib.mjs
declare -A CHAIN_SLUGS=(
  [mainnet]=eth [ethereum]=eth
  [optimism]=oeth [op-mainnet]=oeth
  [bsc]=bnb [gnosis]=gno
  [polygon]=pol [base]=base
  [arbitrum]=arb1 [arbitrum-one]=arb1
  [avalanche]=avax [sepolia]=sep
  [base-sepolia]=basesep
)

while [[ $# -gt 0 ]]; do
  case "$1" in
    --tx-service-url)
      TX_SERVICE_URL="$2"; shift 2 ;;
    --chain)
      CHAIN="$2"; shift 2 ;;
    -h|--help)
      echo "Usage: $0 (--chain <slug> | --tx-service-url <url>)" >&2
      exit 0
      ;;
    *)
      echo "Unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -z "$TX_SERVICE_URL" ]]; then
  if [[ -z "$CHAIN" ]]; then
    echo "Missing --chain or --tx-service-url" >&2
    exit 2
  fi
  SLUG="${CHAIN_SLUGS[$CHAIN]:-}"
  if [[ -z "$SLUG" ]]; then
    echo "Unknown chain slug: $CHAIN. Known: ${!CHAIN_SLUGS[*]}" >&2
    exit 2
  fi
  # Gateway URL includes /api — consistent with safe_lib.mjs resolveTxServiceUrl
  TX_SERVICE_URL="https://api.safe.global/tx-service/${SLUG}/api"
fi

curl -sSf --connect-timeout 10 --max-time 30 "${TX_SERVICE_URL}/v1/about/"
