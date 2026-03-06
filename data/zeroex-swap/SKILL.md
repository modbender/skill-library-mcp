---
name: ZeroEx Swap Skill
description: "⚠️ SECURITY WARNING: This skill involves real funds. Review all
  parameters before executing swaps."
---

# ZeroEx Swap Skill

⚠️ **SECURITY WARNING:** This skill involves real funds. Review all parameters before executing swaps.

## Install
```bash
cd skills/zeroex-swap
npm install
```

## Required Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ZEROEX_API_KEY` | Get from https://dashboard.0x.org/ | Yes |
| `PRIVATE_KEY` | Wallet private key (hex, without 0x prefix) | Yes |
| `RPC_URL` | RPC endpoint for chain (optional, defaults provided) | No |

**Declared required env vars:** `ZEROEX_API_KEY`, `PRIVATE_KEY`

```bash
export ZEROEX_API_KEY="your-0x-api-key"
export PRIVATE_KEY="your-private-key-hex"
export RPC_URL="https://mainnet.base.org"  # optional
```

## Usage

### Get Price Quote
```bash
node quote.js --sell USDC --buy WETH --amount 1 --chain base
```

### Execute Swap (sell → buy)
```bash
node swap.js --sell USDC --buy WETH --amount 1 --chain base
```

### Execute Swap (buy example)
```bash
node swap.js --sell WETH --buy USDC --amount 0.01 --chain base
```

## Trade History

### getSwapTrades
```bash
curl -s "https://api.0x.org/trade-analytics/swap?chainId=8453&taker=0xYOUR_WALLET" \
  -H "0x-api-key: $ZEROEX_API_KEY" \
  -H "0x-version: v2"
```

### getGaslessTrades
```bash
curl -s "https://api.0x.org/trade-analytics/gasless?chainId=8453&taker=0xYOUR_WALLET" \
  -H "0x-api-key: $ZEROEX_API_KEY" \
  -H "0x-version: v2"
```

## Gasless Swap (Meta-transaction)

**Flow:**
1. Get gasless quote
2. Sign EIP-712 payload
3. Submit meta-tx

### 1) Get gasless quote
```bash
curl -s "https://api.0x.org/gasless/quote?sellToken=USDC&buyToken=WETH&sellAmount=1000000&chainId=8453&taker=0xYOUR_WALLET" \
  -H "0x-api-key: $ZEROEX_API_KEY" \
  -H "0x-version: v2"
```

### 2) Sign EIP-712 (use viem)
```js
// use viem to sign quote.trade.eip712
await client.signTypedData({
  domain: quote.trade.eip712.domain,
  types: quote.trade.eip712.types,
  message: quote.trade.eip712.message,
  primaryType: quote.trade.eip712.primaryType
});
```

### 3) Submit
```bash
curl -s -X POST "https://api.0x.org/gasless/submit" \
  -H "0x-api-key: $ZEROEX_API_KEY" \
  -H "0x-version: v2" \
  -H "Content-Type: application/json" \
  -d '{"trade": {"type":"settler_metatransaction","eip712": {"domain": {"name": "Settler", "chainId": 8453, "verifyingContract": "0x..."},"types": {...},"message": {...},"primaryType":"..."},"signature": {"v": 27, "r": "0x...", "s": "0x...", "signatureType": 2}}}'
```

## Security Best Practices

- Use a dedicated hot wallet
- Set slippage protection
- Approve exact amounts only
- Use your own RPC via `RPC_URL`

