#!/usr/bin/env bash
# deai-buy-now.sh — Instant purchase on a Buy It Now auction
# Usage: deai-buy-now.sh <auctionId>
# Calls AssetAuction.buyNow(auctionId) — atomic settlement in one transaction
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

AUCTION_ID="${1:?Usage: deai-buy-now.sh <auctionId>}"

assert_uint "auctionId" "$AUCTION_ID"
build_cast_flags

echo "=== DeAI Buy Now ==="
echo "Auction: #$AUCTION_ID"
echo ""

# Fetch auction details
AUCTION_DATA=$(curl -sf "${DEAI_INDEXER_URL}/api/auctions/${AUCTION_ID}" 2>/dev/null || echo "")
if [[ -n "$AUCTION_DATA" && "$AUCTION_DATA" != "null" ]]; then
  STATUS=$(echo "$AUCTION_DATA" | jq -r '.status // "unknown"')
  PRICE=$(echo "$AUCTION_DATA" | jq -r '.reservePrice // "?"')
  SELLER=$(echo "$AUCTION_DATA" | jq -r '.seller // "?"')
  echo "Status:  $STATUS"
  echo "Price:   $PRICE"
  echo "Seller:  $SELLER"
  echo ""

  if [[ "$STATUS" != "active" && "$STATUS" != "0" ]]; then
    echo "Auction is not active (status: $STATUS). Cannot buy."
    exit 1
  fi
fi

echo "Executing Buy Now..."
TX_HASH=$(cast send "$ASSET_AUCTION_ADDR" \
  "buyNow(uint256)" \
  "$AUCTION_ID" \
  "${CAST_FLAGS[@]}" \
  --json | jq -r '.transactionHash')

echo "TX: $TX_HASH"
echo "Waiting for confirmation..."

RECEIPT=$(cast receipt "$TX_HASH" --rpc-url "$DEAI_RPC_URL" --json)
STATUS=$(echo "$RECEIPT" | jq -r '.status')

if [[ "$STATUS" == "0x1" ]]; then
  echo ""
  echo "Purchase complete! Asset transferred to your wallet."
  echo "Payment sent to seller (minus 1.5% fee)."
  echo "Reputation updated for both parties."
  echo "Explorer: $(explorer_tx_url "$TX_HASH")"
else
  echo "Transaction FAILED."
  echo "Common reasons:"
  echo "  - Not a Buy It Now auction"
  echo "  - Auction not active (already sold or cancelled)"
  echo "  - Not registered as agent"
  echo "  - Insufficient token balance or allowance"
  echo "Explorer: $(explorer_tx_url "$TX_HASH")"
  exit 1
fi
