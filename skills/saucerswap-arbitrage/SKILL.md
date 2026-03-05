---
name: saucerswap-arbitrage
description: Execute triangular arbitrage on Hedera via SaucerSwap. Use for: (1) Finding arbitrage opportunities on HBAR DEX, (2) Multi-hop token swaps, (3) Calculating profit across pools, (4) Executing atomic swaps.
---

# SaucerSwap Arbitrage

## Overview

SaucerSwap is the main DEX on Hedera. Triangular arbitrage: profit from price differences between 3 tokens.

## Key Contracts (Mainnet)

- **SaucerSwap V1**: `0xcaec9706a4622D356d2D3aEd8f8D40c51f0C0dF`
- **SaucerSwap V2**: `0xA6F4E11E5D8A3F62A7D4E3E6B1E7F3C9E8F2A1B4`

## Get Quotes (V1)

```typescript
const axios = require('axios');

async function getQuote(amountIn, path) {
  const [tokenA, tokenB, tokenC] = path;
  const url = `https://mainnet-api.saucerswap.fi/route?from=${tokenA}&to=${tokenB}&amount=${amountIn}`;
  const response = await axios.get(url);
  return response.data;
}
```

## Token Addresses (Hedera)

- **HBAR**: `0.0.1000` (wrapped: `0x...` in EVM format)
- **USDC**: `0.0.456719`
- **USDT**: `0.0.456720`
- **ETH**: `0.0.456721`
- **WBTC**: `0.0.456722`
- **SAUCE**: `0.0.456723`

## Arbitrage Logic

### 1. Check Prices
```typescript
// Get prices for potential paths
const paths = [
  ['USDC', 'HBAR', 'USDC'],
  ['USDC', 'SAUCE', 'USDC'],
  ['HBAR', 'USDC', 'HBAR']
];

for (const path of paths) {
  const out = await getQuote(1000, path);
  const profit = out - 1000;
  console.log(`${path.join(' → ')}: ${profit}`);
}
```

### 2. Execute Swap
```typescript
// Via HashPack or direct contract call
const tx = new ContractExecuteTransaction()
  .setContractId(poolAddress)
  .setFunction("swap")
  .setParameters([...]);
```

## Safety Checks

1. **Slippage**: Set min output = expected * 0.97
2. **Gas**: Estimate network fees (tinybars)
3. **Pool Depth**: Check liquidity before large trades
4. **Hedera Gossip**: Account for network latency

## Key Differences from EVM

- **No EOA signatures**: Must use Hedera native signing
- **Network fees**: Paid in tinybars (not gas)
- **Transaction types**: Use HAPI, not EVM
- **Token format**: Use `0.0.xxxxx` not `0x...`
