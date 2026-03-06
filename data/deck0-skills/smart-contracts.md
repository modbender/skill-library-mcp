# Smart Contract Operations

Buying and opening packs in DECK-0 are on-chain operations. This guide covers the complete flow from getting a price quote to minting packs and opening them.

## Overview

| Operation | Function | Gas | Payment |
|-----------|----------|-----|---------|
| Buy packs | `mintPacks()` | Payable | Native token (APE/ETH) |
| Open packs | `openPacks()` | Non-payable | No payment required |

## Supported Networks

| Network | Chain ID | Currency | Display decimals | Block Explorer |
|---------|----------|----------|------------------|----------------|
| Apechain Mainnet | 33139 | APE | 2 | https://apescan.io |
| Base | 8453 | ETH | 4 | https://basescan.org |

Native tokens use 18 decimals on-chain; the table above is for display precision only.

## Buying Packs

### Step 1: Get Signed Price

Call the price endpoint to get a server-signed price quote:

```
GET /api/agents/v1/collections/{address}/price
```

Response:

```json
{
  "success": true,
  "data": {
    "priceInCents": "123",
    "priceInNative": "813008130081300813",
    "expiration": 1706200120,
    "signature": "0xabcd...1234",
    "nonce": "0x1234...abcd",
    "currency": "APE",
    "chainId": 33139,
    "contractAddress": "0x1234...abcd"
  }
}
```

The signed price expires after **2 minutes**. You must complete the transaction before expiration.

### Step 2: Calculate Payment Value

The payment amount in wei is:

```
value = (packPrice * priceInNative * quantity) / 100
```

Where:
- `packPrice` — the album's pack price in USD cents (from collection details, e.g., `1000` = $10.00)
- `priceInNative` — wei per $1 USD scaled by 100 (from price endpoint)
- `quantity` — number of packs to buy
- Division by 100 removes the scaling factor

**Example** (1 APE = $1.23, pack costs $10.00, buying 2 packs):

```
priceInNative = (1e18 * 100) / (1.23 * 100) = 813,008,130,081,300,813
value = (1000 * 813,008,130,081,300,813 * 2) / 100
     = 16,260,162,601,626,016,260
     ≈ 16.26 APE
```

### Step 3: Call mintPacks

```solidity
function mintPacks(
    address to,
    uint256 quantity,
    uint256 nativeUSDPrice,
    uint256 nativeUSDPriceExpiration,
    bytes signature,
    bytes32 nonce
) external payable
```

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `to` | address | Recipient wallet address (can gift to another address) |
| `quantity` | uint256 | Number of packs to mint |
| `nativeUSDPrice` | uint256 | `priceInNative` from the price endpoint |
| `nativeUSDPriceExpiration` | uint256 | `expiration` from the price endpoint |
| `signature` | bytes | `signature` from the price endpoint |
| `nonce` | bytes32 | `nonce` from the price endpoint |

**ABI:**

```json
{
  "inputs": [
    { "internalType": "address", "name": "to", "type": "address" },
    { "internalType": "uint256", "name": "quantity", "type": "uint256" },
    { "internalType": "uint256", "name": "nativeUSDPrice", "type": "uint256" },
    { "internalType": "uint256", "name": "nativeUSDPriceExpiration", "type": "uint256" },
    { "internalType": "bytes", "name": "signature", "type": "bytes" },
    { "internalType": "bytes32", "name": "nonce", "type": "bytes32" }
  ],
  "name": "mintPacks",
  "outputs": [],
  "stateMutability": "payable",
  "type": "function"
}
```

**Events emitted:**

- `PackMinted(address indexed to, uint256 packId)` — one per pack minted

### Step 4: Extract Pack IDs

Parse the transaction receipt for `PackMinted` events to get the minted pack token IDs. You'll need these IDs to open the packs.

## Opening Packs

### Call openPacks

```solidity
function openPacks(uint256[] calldata packIds) external
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `packIds` | uint256[] | Array of pack token IDs to open |

The caller must own all specified pack IDs. Each pack contains 5 cards.

**ABI:**

```json
{
  "inputs": [
    { "internalType": "uint256[]", "name": "packIds", "type": "uint256[]" }
  ],
  "name": "openPacks",
  "outputs": [],
  "stateMutability": "nonpayable",
  "type": "function"
}
```

**Events emitted:**

- `PackOpened(uint256 packId, uint256[] cardIds)` — one per pack opened, includes the revealed card IDs
- `Transfer` events for burning packs and minting cards

## Complete Code Example (Shell with Foundry cast)

```bash
#!/usr/bin/env bash
set -euo pipefail

# Fallback signing: require DECK0_PRIVATE_KEY so unset env fails fast
: "${DECK0_PRIVATE_KEY:?DECK0_PRIVATE_KEY must be set for fallback signing}"

# Requires: auth helpers from auth.md (sign_request, make_authenticated_request, etc.)

WALLET=$(cast wallet address --private-key "$DECK0_PRIVATE_KEY" | tr '[:upper:]' '[:lower:]')
BASE_URL="https://app.deck-0.com"

# --- Buy Packs ---
# Usage: buy_packs CONTRACT_ADDRESS PACK_PRICE QUANTITY RPC_URL
buy_packs() {
  local contract="$1"
  local pack_price="$2"   # in cents, e.g. 1000 = $10.00
  local quantity="$3"
  local rpc_url="$4"

  # 1. Get signed price from API
  local price_json
  price_json="$(make_authenticated_request "/api/agents/v1/collections/${contract}/price")"

  local price_in_native expiration sig nonce
  price_in_native="$(echo "$price_json" | jq -r '.data.priceInNative')"
  expiration="$(echo "$price_json" | jq -r '.data.expiration')"
  sig="$(echo "$price_json" | jq -r '.data.signature')"
  nonce="$(echo "$price_json" | jq -r '.data.nonce')"

  # 2. Calculate payment value: (packPrice * priceInNative * quantity) / 100
  local value
  value="$(echo "$pack_price * $price_in_native * $quantity / 100" | bc)"

  # 3. Call mintPacks on-chain
  local tx_hash
  tx_hash="$(cast send "$contract" \
    "mintPacks(address,uint256,uint256,uint256,bytes,bytes32)" \
    "$WALLET" "$quantity" "$price_in_native" "$expiration" "$sig" "$nonce" \
    --value "$value" \
    --private-key "$DECK0_PRIVATE_KEY" \
    --rpc-url "$rpc_url" \
    --json | jq -r '.transactionHash')"

  echo "Mint transaction: $tx_hash"

  # 4. Extract pack IDs from PackMinted events
  local pack_ids
  pack_ids="$(cast receipt "$tx_hash" --rpc-url "$rpc_url" --json \
    | jq -r '.logs[] | select(.topics[0] == "0x'$(cast keccak "PackMinted(address,uint256)" | cut -c3-)'") | .data' \
    | while read -r data; do cast --to-dec "$data"; done)"

  echo "Pack IDs: $pack_ids"
}

# --- Open Packs ---
# Usage: open_packs CONTRACT_ADDRESS RPC_URL PACK_ID1 [PACK_ID2 ...]
open_packs() {
  local contract="$1"
  local rpc_url="$2"
  shift 2
  local pack_ids="[$( IFS=,; echo "$*" )]"

  local tx_hash
  tx_hash="$(cast send "$contract" \
    "openPacks(uint256[])" \
    "$pack_ids" \
    --private-key "$DECK0_PRIVATE_KEY" \
    --rpc-url "$rpc_url" \
    --json | jq -r '.transactionHash')"

  echo "Open transaction: $tx_hash"
}

# --- Usage ---
# Buy 2 packs from an Apechain Mainnet collection (pack price $10.00 = 1000 cents)
# buy_packs "0x1a2b3c..." 1000 2 "https://rpc.apechain.com"

# Open packs (pass pack IDs from the mint receipt)
# open_packs "0x1a2b3c..." "https://rpc.apechain.com" 42 43
```

## Price Calculation Details

The price endpoint uses the following formula internally:

1. **Fetch token price** from CoinMarketCap (e.g., 1 APE = $1.23)
2. **Convert to cents** and ceil: `usdPerTokenInCents = Math.ceil(1.23 * 100) = 123`
3. **Calculate wei-per-USD (scaled by 100)**:
   ```
   priceInNative = (1e18 * 100) / usdPerTokenInCents
                 = 1e20 / 123
                 = 813,008,130,081,300,813
   ```
4. **Sign the price** with server's ECDSA key, including:
   - `priceInNative`, `expiration` (now + 2 min), `buyer` address, `contractAddress`, `chainId`, `nonce`

The on-chain contract verifies the server's signature before accepting payment.

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| Transaction reverted: expired | Signed price older than 2 minutes | Fetch a new price and retry |
| Transaction reverted: insufficient value | Payment too low | Recalculate using fresh price data |
| Transaction reverted: invalid signature | Signature doesn't match server signer | Ensure you're passing the exact values from the price API |
| Transaction reverted: not owner | Caller doesn't own the pack IDs | Verify pack ownership before calling openPacks |
| Insufficient funds | Wallet balance too low | Top up wallet with APE or ETH |
