---
name: kyberswap-arbitrage
description: "Execute triangular arbitrage on Base network via KyberSwap. Use
  for: (1) Finding arbitrage opportunities between token pairs, (2) Calculating
  optimal swap paths, (3) Executing multi-hop trades, (4) Managing gas and
  slippage."
---


# KyberSwap Arbitrage

## Overview

Triangular arbitrage: profit from price differences between 3 tokens (e.g., USDC → ETH → USDT → USDC)

## Key Contracts (Base Mainnet)

- **Router**: `0x6131B5fae19EA4f9D964eAc0408E4408b2a37dD8`
- **Factory**: `0x5F1dddbf348aC2BEbe18559BF0eDE9D3fE6ce35f`

## Core Logic

### 1. Get Quotes
```typescript
const router = new ethers.Contract(routerAddr, routerABI, provider);

// Get amounts out for exact input
const [amountOut] = await router.getAmountsOut(
  amountIn,      // Wei amount
  [tokenA, tokenB, tokenC] // Path
);
```

### 2. Calculate Profit
```
profit = finalAmount - initialAmount - gasCosts
```

### 3. Execute Swap
```typescript
const tx = await router.swapExactTokensForTokens(
  amountIn,
  amountOutMin,
  path,
  recipient,
  deadline
);
```

## Token Addresses (Base)

- **USDC**: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- **USDT**: `0xfde4C96c85940E8F44A6D8d5e4fD4f4C4f9D8E8`
- **ETH**: `0x4200000000000000000000000000000000000006`
- **WETH**: `0x4200000000000000000000000000000000000006`

## Arbitrage Pairs (Base)

Common triangular paths:
- USDC → ETH → USDC
- USDC → WETH → USDT → USDC
- USDT → ETH → USDC → USDT

## Safety Checks

1. **Slippage**: Set `amountOutMin` = output * (1 - slippage%)
2. **Gas**: Estimate gas, ensure profit > gas
3. **Max Price Impact**: Check pool reserves before large trades
4. **Renounced Contracts**: Only trade tokens with renounced ownership

## Risk Profile

- **Aggressive** but audit-first
- Skip all non-renounced contracts
- Check for honeypot tokens
