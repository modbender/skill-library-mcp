#!/usr/bin/env bash
# deai-config.sh — Validate environment variables and dependencies
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

echo "=== DeAI Configuration Check ==="
echo ""

ERRORS=0

# Check cast is installed
if command -v cast &>/dev/null; then
  echo "[OK] cast: $(cast --version 2>/dev/null | head -1)"
else
  echo "[FAIL] cast not found — install Foundry: https://getfoundry.sh"
  ERRORS=$((ERRORS + 1))
fi

# Check jq is installed
if command -v jq &>/dev/null; then
  echo "[OK] jq: $(jq --version 2>/dev/null)"
else
  echo "[FAIL] jq not found — install: apt install jq / brew install jq"
  ERRORS=$((ERRORS + 1))
fi

# Check curl is installed
if command -v curl &>/dev/null; then
  echo "[OK] curl: $(curl --version 2>/dev/null | head -1)"
else
  echo "[FAIL] curl not found — install: apt install curl / brew install curl"
  ERRORS=$((ERRORS + 1))
fi

# Check python3 is installed (used for decimal math in amount conversion)
if command -v python3 &>/dev/null; then
  echo "[OK] python3: $(python3 --version 2>/dev/null)"
else
  echo "[FAIL] python3 not found — install: apt install python3 / brew install python3"
  ERRORS=$((ERRORS + 1))
fi

# Check keystore account
if [[ -n "$DEAI_ACCOUNT" ]]; then
  WALLET=$(get_wallet)
  if [[ -n "$WALLET" ]]; then
    echo "[OK] Wallet: $WALLET (account: $DEAI_ACCOUNT)"
  else
    echo "[FAIL] DEAI_ACCOUNT=$DEAI_ACCOUNT but cannot derive wallet address"
    ERRORS=$((ERRORS + 1))
  fi
else
  echo "[FAIL] DEAI_ACCOUNT not set"
  ERRORS=$((ERRORS + 1))
fi

# Check password file (optional but recommended for autonomous agents)
if [[ -n "${DEAI_PASSWORD_FILE:-}" ]]; then
  if [[ -f "$DEAI_PASSWORD_FILE" ]]; then
    echo "[OK] Password file: $DEAI_PASSWORD_FILE"
  else
    echo "[WARN] DEAI_PASSWORD_FILE set but file not found: $DEAI_PASSWORD_FILE"
  fi
else
  echo "[INFO] DEAI_PASSWORD_FILE not set — will require interactive password entry"
fi

echo ""
echo "--- Chain ---"
echo "Chain:    $(chain_name) ($DEAI_CHAIN_ID)"
echo "RPC:      $DEAI_RPC_URL"
echo "Indexer:  $DEAI_INDEXER_URL"

# Check RPC connectivity
BLOCK=$(cast block-number --rpc-url "$DEAI_RPC_URL" 2>/dev/null || echo "FAIL")
if [[ "$BLOCK" != "FAIL" ]]; then
  echo "[OK] RPC reachable (block: $BLOCK)"
else
  echo "[FAIL] Cannot reach RPC at $DEAI_RPC_URL"
  ERRORS=$((ERRORS + 1))
fi

# Check indexer connectivity
INDEXER_STATUS=$(curl -sf "${DEAI_INDEXER_URL}/api/stats" 2>/dev/null || echo "FAIL")
if [[ "$INDEXER_STATUS" != "FAIL" ]]; then
  echo "[OK] Indexer reachable"
else
  echo "[WARN] Indexer not reachable at $DEAI_INDEXER_URL (non-critical)"
fi

echo ""
echo "--- Contracts ---"

check_addr() {
  local name="$1" addr="$2"
  if [[ -n "$addr" && "$addr" != "0x" ]]; then
    echo "[OK] $name: $addr"
  else
    echo "[FAIL] $name: not set"
    ERRORS=$((ERRORS + 1))
  fi
}

check_addr "AssetAuction" "$DEAI_ASSET_AUCTION_ADDR"
check_addr "Escrow" "$DEAI_ESCROW_ADDR"
check_addr "Identity" "$DEAI_IDENTITY_ADDR"
check_addr "USDC" "$DEAI_USDC_ADDR"

echo ""
echo "--- Adapters (optional) ---"
[[ -n "$DEAI_ERC20_ADAPTER_ADDR" ]] && echo "[OK] ERC20Adapter: $DEAI_ERC20_ADAPTER_ADDR" || echo "[INFO] ERC20Adapter: not set"
[[ -n "$DEAI_ERC721_ADAPTER_ADDR" ]] && echo "[OK] ERC721Adapter: $DEAI_ERC721_ADAPTER_ADDR" || echo "[INFO] ERC721Adapter: not set"
[[ -n "$DEAI_ERC1155_ADAPTER_ADDR" ]] && echo "[OK] ERC1155Adapter: $DEAI_ERC1155_ADAPTER_ADDR" || echo "[INFO] ERC1155Adapter: not set"
[[ -n "$DEAI_ERC4626_ADAPTER_ADDR" ]] && echo "[OK] ERC4626Adapter: $DEAI_ERC4626_ADAPTER_ADDR" || echo "[INFO] ERC4626Adapter: not set"

echo ""
if [[ "$ERRORS" -gt 0 ]]; then
  echo "RESULT: $ERRORS error(s) found. Fix before proceeding."
  exit 1
else
  echo "RESULT: All checks passed. Ready to trade."
fi
