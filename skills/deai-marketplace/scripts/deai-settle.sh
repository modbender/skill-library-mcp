#!/usr/bin/env bash
# deai-settle.sh — Settle an expired English auction
# Usage: deai-settle.sh <auctionId>
# Calls AssetAuction.settle(auctionId) — transfers asset to winner, payment to seller
# Can be called by anyone after the auction deadline passes.
# If no bids: returns asset to seller, status → EXPIRED
# If bids exist: asset → winner, payment → seller (minus 1.5% fee), reputation updated
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

AUCTION_ID="${1:?Usage: deai-settle.sh <auctionId>}"

assert_uint "auctionId" "$AUCTION_ID"
build_cast_flags

echo "=== DeAI Settle Auction ==="
echo "Auction: #$AUCTION_ID"
echo ""

# Fetch auction details
AUCTION_DATA=$(curl -sf "${DEAI_INDEXER_URL}/api/auctions/${AUCTION_ID}" 2>/dev/null || echo "")
if [[ -n "$AUCTION_DATA" && "$AUCTION_DATA" != "null" ]]; then
  STATUS=$(echo "$AUCTION_DATA" | jq -r '.status // "unknown"')
  HIGHEST_BID=$(echo "$AUCTION_DATA" | jq -r '.highestBid // "0"')
  HIGHEST_BIDDER=$(echo "$AUCTION_DATA" | jq -r '.highestBidder // "none"')
  END_TIME=$(echo "$AUCTION_DATA" | jq -r '.endTime // "?"')
  echo "Status:         $STATUS"
  echo "Highest Bid:    $HIGHEST_BID"
  echo "Highest Bidder: $HIGHEST_BIDDER"
  echo "End Time:       $END_TIME"
  echo ""
fi

echo "Settling auction..."
TX_HASH=$(cast send "$ASSET_AUCTION_ADDR" \
  "settle(uint256)" \
  "$AUCTION_ID" \
  "${CAST_FLAGS[@]}" \
  --json | jq -r '.transactionHash')

echo "TX: $TX_HASH"
echo "Waiting for confirmation..."

RECEIPT=$(cast receipt "$TX_HASH" --rpc-url "$DEAI_RPC_URL" --json)
STATUS=$(echo "$RECEIPT" | jq -r '.status')

if [[ "$STATUS" == "0x1" ]]; then
  echo ""
  echo "Auction settled!"
  echo "Explorer: $(explorer_tx_url "$TX_HASH")"
else
  echo "Transaction FAILED."
  echo "Common reasons:"
  echo "  - Auction not yet expired (deadline not passed)"
  echo "  - Not an English auction (use buyNow for Buy It Now)"
  echo "  - Auction not active (already settled or cancelled)"
  echo "Explorer: $(explorer_tx_url "$TX_HASH")"
  exit 1
fi
