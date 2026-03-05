#!/usr/bin/env bash
# deai-bid.sh — Place a bid on an English auction
# Usage: deai-bid.sh <auctionId> <amount>
# Example: deai-bid.sh 5 50
#   Bids 50 USDC on auction #5
# Amount is in human-readable units (e.g. 50 = 50 USDC). Converted to raw internally.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

AUCTION_ID="${1:?Usage: deai-bid.sh <auctionId> <amount>}"
AMOUNT="${2:?Usage: deai-bid.sh <auctionId> <amount>}"

assert_uint "auctionId" "$AUCTION_ID"
assert_decimal "amount" "$AMOUNT"
build_cast_flags

# Convert human-readable to raw token units (6 decimals for USDC)
AMOUNT_RAW=$(to_wei "$AMOUNT")

echo "=== DeAI Bid — English Auction ==="
echo "Auction: #$AUCTION_ID"
echo "Amount:  $AMOUNT USDC ($AMOUNT_RAW raw)"
echo ""

# Fetch auction details from indexer
AUCTION_DATA=$(curl -sf "${DEAI_INDEXER_URL}/api/auctions/${AUCTION_ID}" 2>/dev/null || echo "")
if [[ -n "$AUCTION_DATA" && "$AUCTION_DATA" != "null" ]]; then
  STATUS=$(echo "$AUCTION_DATA" | jq -r '.status // "unknown"')
  RESERVE=$(echo "$AUCTION_DATA" | jq -r '.reservePrice // "?"')
  HIGHEST=$(echo "$AUCTION_DATA" | jq -r '.highestBid // "0"')
  DEADLINE=$(echo "$AUCTION_DATA" | jq -r '.endTime // "?"')
  echo "Status:       $STATUS"
  echo "Reserve:      $RESERVE"
  echo "Highest bid:  $HIGHEST"
  echo "Deadline:     $DEADLINE"
  echo ""

  if [[ "$STATUS" != "active" && "$STATUS" != "0" ]]; then
    echo "ERROR: Auction is not active (status: $STATUS). Cannot bid."
    exit 1
  fi
fi

echo "Submitting bid..."
TX_HASH=$(cast send "$ASSET_AUCTION_ADDR" \
  "bid(uint256,uint256)" \
  "$AUCTION_ID" "$AMOUNT_RAW" \
  "${CAST_FLAGS[@]}" \
  --json | jq -r '.transactionHash')

echo "TX: $TX_HASH"
echo "Waiting for confirmation..."

RECEIPT=$(cast receipt "$TX_HASH" --rpc-url "$DEAI_RPC_URL" --json)
STATUS=$(echo "$RECEIPT" | jq -r '.status')

if [[ "$STATUS" == "0x1" ]]; then
  echo ""
  echo "Bid placed successfully!"
  echo "Amount: $AMOUNT USDC"
  echo "Explorer: $(explorer_tx_url "$TX_HASH")"
else
  echo "Transaction FAILED."
  echo "Common reasons:"
  echo "  - Below reserve price (first bid) or below 5% increment (subsequent)"
  echo "  - Auction expired or not active"
  echo "  - Not registered as agent (buyer identity required)"
  echo "  - Insufficient token balance or allowance (run deai-approve-token.sh first)"
  echo "Explorer: $(explorer_tx_url "$TX_HASH")"
  exit 1
fi
