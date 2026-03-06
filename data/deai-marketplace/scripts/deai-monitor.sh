#!/usr/bin/env bash
# deai-monitor.sh — Browse asset auctions from the indexer
# Usage: deai-monitor.sh [--status active|settled|cancelled|expired] [--type english|buynow] [--limit N]
# Defaults: --status active --limit 20
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

STATUS_FILTER="active"
TYPE_FILTER="all"
LIMIT="20"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --status) STATUS_FILTER="$2"; shift 2 ;;
    --type) TYPE_FILTER="$2"; shift 2 ;;
    --limit) LIMIT="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

# Validate filter inputs (prevent query string injection)
if [[ ! "$STATUS_FILTER" =~ ^[a-zA-Z_]+$ ]]; then
  echo "ERROR: --status must be alphabetic, got: '$STATUS_FILTER'" >&2; exit 1
fi
if [[ ! "$TYPE_FILTER" =~ ^[a-zA-Z_]+$ ]]; then
  echo "ERROR: --type must be alphabetic, got: '$TYPE_FILTER'" >&2; exit 1
fi
assert_uint "limit" "$LIMIT"

URL="${DEAI_INDEXER_URL}/api/auctions?status=${STATUS_FILTER}&limit=${LIMIT}"

echo "=== DeAI Auction Monitor ($(chain_name)) ==="
echo "Filter: status=$STATUS_FILTER, type=$TYPE_FILTER, limit=$LIMIT"
echo "Browse: https://deai.au/auctions"
echo ""

RESPONSE=$(curl -sf "$URL" 2>/dev/null)
if [[ -z "$RESPONSE" ]]; then
  echo "ERROR: Could not reach indexer at $DEAI_INDEXER_URL"
  echo "Make sure the indexer is running or set DEAI_INDEXER_URL."
  exit 1
fi

# Parse auctions — handle both array and {auctions:[]} formats
if echo "$RESPONSE" | jq -e '.auctions' &>/dev/null; then
  AUCTIONS=$(echo "$RESPONSE" | jq '.auctions')
else
  AUCTIONS="$RESPONSE"
fi

# Client-side type filter (indexer may not support type query param)
if [[ "$TYPE_FILTER" == "english" ]]; then
  AUCTIONS=$(echo "$AUCTIONS" | jq '[.[] | select(.auctionType == 0 or .auctionType == "english" or .auctionType == "ENGLISH")]')
elif [[ "$TYPE_FILTER" == "buynow" ]]; then
  AUCTIONS=$(echo "$AUCTIONS" | jq '[.[] | select(.auctionType == 1 or .auctionType == "buy_it_now" or .auctionType == "BUY_IT_NOW")]')
fi

TOTAL=$(echo "$AUCTIONS" | jq 'length')

echo "Found $TOTAL auction(s)"
echo ""

if [[ "$TOTAL" == "0" ]]; then
  echo "No auctions found matching filters."
  exit 0
fi

# Display each auction
echo "$AUCTIONS" | jq -r '.[] | [
  "Auction #\(.id // .auctionId // "?")",
  "  Seller:       \(.seller // "?")",
  "  Asset:        \(.assetContract // "?") (\(.adapter // "?"))",
  "  Reserve:      \(.reservePrice // "?")",
  "  Highest Bid:  \(.highestBid // "0")",
  "  Bidder:       \(.highestBidder // "none")",
  "  Type:         \(if .auctionType == 0 or .auctionType == "english" or .auctionType == "ENGLISH" then "English" elif .auctionType == 1 or .auctionType == "buy_it_now" or .auctionType == "BUY_IT_NOW" then "Buy It Now" else .auctionType // "?" end)",
  "  End Time:     \(.endTime // "no deadline")",
  "  Status:       \(.status // "?")",
  ""
] | join("\n")'
