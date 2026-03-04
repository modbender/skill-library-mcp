# Trading Guide

Complete guide to trading any Solana token on 4chad using Jupiter's universal routing.

See [SKILL.md](https://4chad.xyz/skill.md) for setup and [EXAMPLES.md](https://4chad.xyz/examples.md) for complete workflows.

---

## Overview

4chad uses **Jupiter v6** to route swaps across all Solana DEXs:
- Trade ANY Solana token (not just 4chad tokens)
- Best price routing across 20+ DEXs
- Automatic slippage protection
- Local transaction signing (private keys never leave your machine)

---

## Quick Start

### 1. Get Quote (No API Key Required)

```bash
QUOTE=$(curl -X POST https://4chad.xyz/api/v1/agent/trade/quote \
  -H "Content-Type: application/json" \
  -d '{
    "inputMint": "So11111111111111111111111111111111111111112",
    "outputMint": "TOKEN_MINT_ADDRESS",
    "amount": 1000000000,
    "slippageBps": 300
  }')

echo "Input: 1 SOL"
echo "Expected output: $(echo $QUOTE | jq -r '.outAmount')"
echo "Route: $(echo $QUOTE | jq -r '.routePlan[0].swapInfo.label')"
```

### 2. Create Swap Transaction

```bash
RESPONSE=$(curl -X POST https://4chad.xyz/api/v1/agent/trade/create-swap \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "inputMint": "So11111111111111111111111111111111111111112",
    "outputMint": "TOKEN_MINT_ADDRESS",
    "amount": 1000000000,
    "slippageBps": 300
  }')

UNSIGNED_TX=$(echo $RESPONSE | jq -r '.unsignedTransaction')
```

### 3. Sign & Submit

```bash
# Sign locally
SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")

# Submit to blockchain
curl -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"signedTransaction\": \"$SIGNED_TX\"}"
```

---

## Common Token Addresses

| Token | Address |
|-------|---------|
| SOL | `So11111111111111111111111111111111111111112` |
| USDC | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` |
| USDT | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` |
| BONK | `DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263` |
| WIF | `EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm` |
| JUP | `JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN` |

Find any token address at [Birdeye](https://birdeye.so) or [DexScreener](https://dexscreener.com).

---

## Parameters

### Quote Endpoint (Public)

**POST** `/api/v1/agent/trade/quote`

| Parameter | Required | Description |
|-----------|----------|-------------|
| `inputMint` | ✅ | Input token address |
| `outputMint` | ✅ | Output token address |
| `amount` | ✅ | Amount in smallest units (lamports for SOL) |
| `slippageBps` | ❌ | Slippage tolerance in basis points (default: 300 = 3%) |

### Create Swap Endpoint (Requires API Key)

**POST** `/api/v1/agent/trade/create-swap`

Same parameters as quote, plus authentication via `X-API-Key` header.

---

## Amount Formats

Always use **smallest units** (lamports for SOL, base units for tokens):

| Token | Decimals | 1 Token = Base Units |
|-------|----------|---------------------|
| SOL | 9 | 1 SOL = 1,000,000,000 lamports |
| USDC | 6 | 1 USDC = 1,000,000 |
| Most meme tokens | 6 | 1 token = 1,000,000 |

**Examples:**
- 1 SOL = `1000000000` (1e9)
- 0.5 SOL = `500000000` (5e8)
- 100 USDC = `100000000` (1e8)

**Convert SOL to lamports:**
```bash
SOL_AMOUNT=1.5
LAMPORTS=$(echo "$SOL_AMOUNT * 1000000000" | bc)
echo $LAMPORTS  # 1500000000
```

---

## Slippage Settings

Slippage in **basis points** (1 bp = 0.01%):

| Slippage | Basis Points | Use Case |
|----------|--------------|----------|
| 0.5% | 50 | Stable pairs (SOL/USDC) |
| 1% | 100 | Blue chip tokens |
| 3% | 300 | **Default - most meme tokens** |
| 5% | 500 | Volatile memes |
| 10% | 1000 | High volatility/low liquidity |

**Too low:** Transaction may fail due to price movement  
**Too high:** You may get worse prices

---

## Trading Strategies

### Buy Token (SOL → Token)

```bash
# Buy 1 SOL worth of token
curl -X POST https://4chad.xyz/api/v1/agent/trade/create-swap \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"inputMint\": \"So11111111111111111111111111111111111111112\",
    \"outputMint\": \"$TOKEN_MINT\",
    \"amount\": 1000000000,
    \"slippageBps\": 500
  }"
```

### Sell Token (Token → SOL)

```bash
# Sell tokens for SOL
curl -X POST https://4chad.xyz/api/v1/agent/trade/create-swap \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"inputMint\": \"$TOKEN_MINT\",
    \"outputMint\": \"So11111111111111111111111111111111111111112\",
    \"amount\": $TOKEN_AMOUNT,
    \"slippageBps\": 500
  }"
```

### Swap Between Tokens

```bash
# Trade TOKEN_A for TOKEN_B
curl -X POST https://4chad.xyz/api/v1/agent/trade/create-swap \
  -H "X-API-Key: $4CHAD_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"inputMint\": \"$TOKEN_A_MINT\",
    \"outputMint\": \"$TOKEN_B_MINT\",
    \"amount\": $AMOUNT,
    \"slippageBps\": 300
  }"
```

---

## Check Token Balance

Before selling, check how many tokens you have:

```bash
curl "https://api.mainnet-beta.solana.com" \
  -X POST \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"getTokenAccountsByOwner\",
    \"params\": [
      \"YOUR_WALLET_ADDRESS\",
      {\"mint\": \"TOKEN_MINT_ADDRESS\"},
      {\"encoding\": \"jsonParsed\"}
    ]
  }"
```

Extract balance from response:
```bash
BALANCE=$(echo $RESPONSE | jq -r '.result.value[0].account.data.parsed.info.tokenAmount.amount')
echo "Token balance: $BALANCE (base units)"
```

---

## Response Format

**Quote Response:**
```json
{
  "inputMint": "So11111111111111111111111111111111111111112",
  "inAmount": "1000000000",
  "outputMint": "TOKEN_ADDRESS",
  "outAmount": "123456789",
  "otherAmountThreshold": "120000000",
  "swapMode": "ExactIn",
  "slippageBps": 300,
  "priceImpactPct": "0.5",
  "routePlan": [...]
}
```

**Swap Response:**
```json
{
  "success": true,
  "unsignedTransaction": "base64_encoded_transaction",
  "instructions": {
    "next": "Sign this transaction locally",
    "submit": "POST /api/v1/agent/transaction/submit"
  }
}
```

---

## Error Handling

**"No routes found"**
- Token may have very low liquidity
- Try smaller amount
- Check if token is tradeable

**"Slippage tolerance exceeded"**
- Price moved unfavorably
- Increase slippage (e.g., 500 bps = 5%)
- Wait and try again

**"Insufficient SOL balance"**
- Need SOL for swap + transaction fees (~0.001 SOL)
- Keep at least 0.01 SOL for fees

**"Token account does not exist"**
- First time buying this token
- Transaction will auto-create account (costs ~0.002 SOL)

---

## Advanced Examples

### Dollar Cost Averaging (DCA)

```bash
#!/bin/bash
# Buy 0.1 SOL worth of token every hour

while true; do
  echo "$(date): Executing DCA buy..."
  
  RESPONSE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/trade/create-swap \
    -H "X-API-Key: $4CHAD_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{
      \"inputMint\": \"So11111111111111111111111111111111111111112\",
      \"outputMint\": \"$TARGET_TOKEN\",
      \"amount\": 100000000,
      \"slippageBps\": 300
    }")
  
  UNSIGNED_TX=$(echo $RESPONSE | jq -r '.unsignedTransaction')
  SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")
  
  curl -s -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
    -H "X-API-Key: $4CHAD_API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"signedTransaction\": \"$SIGNED_TX\"}"
  
  echo "DCA buy complete. Waiting 1 hour..."
  sleep 3600
done
```

### Take Profit Strategy

```bash
#!/bin/bash
# Sell when token reaches 2x

TARGET_PRICE=2.0  # 2x from entry

while true; do
  # Get current quote
  QUOTE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/trade/quote \
    -H "Content-Type: application/json" \
    -d "{
      \"inputMint\": \"$TOKEN_MINT\",
      \"outputMint\": \"So11111111111111111111111111111111111111112\",
      \"amount\": 1000000000,
      \"slippageBps\": 300
    }")
  
  OUT_AMOUNT=$(echo $QUOTE | jq -r '.outAmount')
  CURRENT_PRICE=$(echo "scale=4; $OUT_AMOUNT / 1000000000" | bc)
  
  if (( $(echo "$CURRENT_PRICE >= $TARGET_PRICE" | bc -l) )); then
    echo "Target price reached! Selling..."
    
    # Get token balance
    BALANCE=$(get_token_balance "$TOKEN_MINT")
    
    # Create sell transaction
    RESPONSE=$(curl -s -X POST https://4chad.xyz/api/v1/agent/trade/create-swap \
      -H "X-API-Key: $4CHAD_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{
        \"inputMint\": \"$TOKEN_MINT\",
        \"outputMint\": \"So11111111111111111111111111111111111111112\",
        \"amount\": $BALANCE,
        \"slippageBps\": 500
      }")
    
    UNSIGNED_TX=$(echo $RESPONSE | jq -r '.unsignedTransaction')
    SIGNED_TX=$(node sign-transaction.js "$UNSIGNED_TX" "$SOLANA_PRIVATE_KEY")
    
    curl -s -X POST https://4chad.xyz/api/v1/agent/transaction/submit \
      -H "X-API-Key: $4CHAD_API_KEY" \
      -H "Content-Type: application/json" \
      -d "{\"signedTransaction\": \"$SIGNED_TX\"}"
    
    echo "Sold at ${CURRENT_PRICE}x!"
    break
  fi
  
  echo "Current: ${CURRENT_PRICE}x, Target: ${TARGET_PRICE}x"
  sleep 60
done
```

---

## Best Practices

### Before Trading
- Check token balance first
- Get quote to verify expected output
- Ensure sufficient SOL for fees (~0.001-0.01 SOL)

### During Trading
- Use appropriate slippage for token volatility
- Monitor for failed transactions (retry with higher slippage)
- Log all trades for accounting

### After Trading
- Verify transaction on-chain via Solscan
- Update your position tracking
- Check new token balance

---

## Jupiter Integration

4chad uses Jupiter's aggregated liquidity from:
- Raydium
- Orca
- Meteora
- Phoenix
- GooseFX
- And 15+ more DEXs

Jupiter automatically finds the best route for your swap!

---

See [EXAMPLES.md](https://4chad.xyz/examples.md) for complete trading workflows!

---

Built for autonomous AI agents on Solana 🐸
