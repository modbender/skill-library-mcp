#!/usr/bin/env bash
# deai-create-auction.sh — Create a new asset auction
# Usage: deai-create-auction.sh <assetType> <assetAddr> <amountOrTokenId> <paymentToken> <reservePrice> <duration> <type>
#
# Arguments:
#   assetType:    erc20 | erc721 | erc1155 | erc4626 | <adapter address>
#   assetAddr:    Address of the asset contract
#   amountOrTokenId: For ERC-20/ERC-4626: raw amount. For ERC-721: tokenId. For ERC-1155: tokenId,amount
#   paymentToken: usdc | <token address>
#   reservePrice: Minimum price in human-readable units (e.g. 100 = 100 USDC)
#   duration:     Auction duration in seconds (0 for Buy It Now)
#   type:         english | buynow (0 = ENGLISH, 1 = BUY_IT_NOW)
#
# Examples:
#   # English auction: sell 1000 tokens, reserve 500 USDC, 24h
#   deai-create-auction.sh erc20 0xAsset... 1000000000 usdc 500 86400 english
#
#   # Buy It Now: sell NFT #42 for 100 USDC
#   deai-create-auction.sh erc721 0xNFT... 42 usdc 100 0 buynow
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

ASSET_TYPE="${1:?Usage: deai-create-auction.sh <assetType> <assetAddr> <amountOrTokenId> <paymentToken> <reservePrice> <duration> <type>}"
ASSET_ADDR="${2:?Missing assetAddr}"
AMOUNT_OR_ID="${3:?Missing amountOrTokenId}"
PAYMENT_TOKEN="${4:?Missing paymentToken}"
RESERVE_PRICE="${5:?Missing reservePrice}"
DURATION="${6:?Missing duration}"
AUCTION_TYPE="${7:?Missing type (english|buynow)}"

assert_address "assetAddr" "$ASSET_ADDR"
assert_decimal "reservePrice" "$RESERVE_PRICE"
assert_uint "duration" "$DURATION"
build_cast_flags

# Resolve adapter address
ADAPTER_ADDR=$(resolve_adapter "$ASSET_TYPE")
if [[ -z "$ADAPTER_ADDR" ]]; then
  echo "ERROR: Could not resolve adapter for asset type: $ASSET_TYPE"
  exit 1
fi

# Resolve payment token address and convert reserve price to raw units
PAYMENT_ADDR=$(resolve_token "$PAYMENT_TOKEN")
if [[ "${PAYMENT_TOKEN,,}" != "usdc" ]]; then
  assert_address "paymentToken" "$PAYMENT_ADDR"
fi
RESERVE_RAW=$(to_wei "$RESERVE_PRICE" "$(token_decimals "$PAYMENT_TOKEN")")

# Encode asset data based on type (with input validation)
case "${ASSET_TYPE,,}" in
  erc20|erc4626)
    assert_uint "amountOrTokenId" "$AMOUNT_OR_ID"
    ASSET_DATA=$(cast abi-encode "f(uint256)" "$AMOUNT_OR_ID")
    ;;
  erc721)
    assert_uint "tokenId" "$AMOUNT_OR_ID"
    ASSET_DATA=$(cast abi-encode "f(uint256)" "$AMOUNT_OR_ID")
    ;;
  erc1155)
    # Expect format: tokenId,amount
    IFS=',' read -r TOKEN_ID AMOUNT <<< "$AMOUNT_OR_ID"
    assert_uint "tokenId" "$TOKEN_ID"
    assert_uint "amount" "${AMOUNT:?Missing amount in tokenId,amount format}"
    ASSET_DATA=$(cast abi-encode "f(uint256,uint256)" "$TOKEN_ID" "$AMOUNT")
    ;;
  *)
    # Raw adapter address — validate adapter, assume ERC-20 encoding
    assert_address "adapterAddr" "$ASSET_TYPE"
    assert_uint "amountOrTokenId" "$AMOUNT_OR_ID"
    ASSET_DATA=$(cast abi-encode "f(uint256)" "$AMOUNT_OR_ID")
    ;;
esac

# Resolve auction type enum
case "${AUCTION_TYPE,,}" in
  english|0) TYPE_ENUM=0 ;;
  buynow|buy_it_now|1) TYPE_ENUM=1 ;;
  *) echo "ERROR: Invalid auction type: $AUCTION_TYPE (use english or buynow)"; exit 1 ;;
esac

echo "=== DeAI Create Auction ==="
echo "Asset Type:    $ASSET_TYPE"
echo "Adapter:       $ADAPTER_ADDR"
echo "Asset Contract: $ASSET_ADDR"
echo "Asset Data:    $AMOUNT_OR_ID"
echo "Payment Token: $PAYMENT_TOKEN ($PAYMENT_ADDR)"
echo "Reserve Price: $RESERVE_PRICE ($RESERVE_RAW raw)"
echo "Duration:      ${DURATION}s"
echo "Auction Type:  $AUCTION_TYPE ($TYPE_ENUM)"
echo ""

# Remind about asset approval
echo "NOTE: Ensure you have approved the adapter ($ADAPTER_ADDR) to transfer your asset."
echo ""

echo "Creating auction..."
TX_HASH=$(cast send "$ASSET_AUCTION_ADDR" \
  "createAuction(address,address,bytes,address,uint256,uint256,uint8)" \
  "$ADAPTER_ADDR" "$ASSET_ADDR" "$ASSET_DATA" "$PAYMENT_ADDR" "$RESERVE_RAW" "$DURATION" "$TYPE_ENUM" \
  "${CAST_FLAGS[@]}" \
  --json | jq -r '.transactionHash')

echo "TX: $TX_HASH"
echo "Waiting for confirmation..."

RECEIPT=$(cast receipt "$TX_HASH" --rpc-url "$DEAI_RPC_URL" --json)
STATUS=$(echo "$RECEIPT" | jq -r '.status')

if [[ "$STATUS" == "0x1" ]]; then
  # Extract auctionId from AuctionCreated event
  AUCTION_ID=$(echo "$RECEIPT" | jq -r '.logs[0].topics[1]' | cast to-dec 2>/dev/null || echo "unknown")
  echo ""
  echo "Auction created successfully!"
  echo "Auction ID: $AUCTION_ID"
  echo "Explorer: $(explorer_tx_url "$TX_HASH")"
  echo "View: https://deai.au/auctions/$AUCTION_ID"
else
  echo "Transaction FAILED."
  echo "Common reasons:"
  echo "  - Not registered as agent (seller identity required)"
  echo "  - Adapter not whitelisted"
  echo "  - Payment token not whitelisted"
  echo "  - Asset not approved for adapter"
  echo "  - Zero reserve price"
  echo "Explorer: $(explorer_tx_url "$TX_HASH")"
  exit 1
fi
