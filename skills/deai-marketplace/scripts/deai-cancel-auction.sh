#!/usr/bin/env bash
# deai-cancel-auction.sh — Cancel your own auction (before any bids)
# Usage: deai-cancel-auction.sh <auctionId>
# Calls AssetAuction.cancelAuction(auctionId) — returns asset to seller
# Only the seller can cancel. Cannot cancel after bids have been placed.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

AUCTION_ID="${1:?Usage: deai-cancel-auction.sh <auctionId>}"

assert_uint "auctionId" "$AUCTION_ID"
build_cast_flags

echo "=== DeAI Cancel Auction ==="
echo "Auction: #$AUCTION_ID"
echo ""

echo "Cancelling auction..."
TX_HASH=$(cast send "$ASSET_AUCTION_ADDR" \
  "cancelAuction(uint256)" \
  "$AUCTION_ID" \
  "${CAST_FLAGS[@]}" \
  --json | jq -r '.transactionHash')

echo "TX: $TX_HASH"
echo "Waiting for confirmation..."

RECEIPT=$(cast receipt "$TX_HASH" --rpc-url "$DEAI_RPC_URL" --json)
STATUS=$(echo "$RECEIPT" | jq -r '.status')

if [[ "$STATUS" == "0x1" ]]; then
  echo ""
  echo "Auction cancelled! Asset returned to your wallet."
  echo "Explorer: $(explorer_tx_url "$TX_HASH")"
else
  echo "Transaction FAILED."
  echo "Common reasons:"
  echo "  - You are not the seller"
  echo "  - Bids already placed (cannot cancel after bids)"
  echo "  - Auction not active (already settled or cancelled)"
  echo "Explorer: $(explorer_tx_url "$TX_HASH")"
  exit 1
fi
