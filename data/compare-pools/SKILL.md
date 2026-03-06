---
name: compare-pools
description: Compare all Uniswap pools for a token pair across fee tiers and versions. Use when the user asks which pool is best, wants to compare V3 vs V4, or wants to find the optimal fee tier.
model: opus
allowed-tools: [Task(subagent_type:pool-researcher)]
---

# Compare Pools

## Overview

Compares all available Uniswap pools for a token pair across fee tiers (1bp, 5bp, 30bp, 100bp) and protocol versions (V2, V3, V4). Delegates to `pool-researcher` in comparison mode to rank pools by APY, liquidity depth, and utilization.

## When to Use

Activate when the user asks:

- "Compare ETH/USDC pools"
- "Which pool is best for ETH/USDC?"
- "V3 vs V4 for this pair"
- "Best fee tier for WETH/USDC"
- "Which fee tier has the best APY?"
- "Compare liquidity across fee tiers"

## Parameters

| Parameter | Required | Default     | Description                                    |
| --------- | -------- | ----------- | ---------------------------------------------- |
| token0    | Yes      | —           | First token name, symbol, or address           |
| token1    | Yes      | —           | Second token name, symbol, or address          |
| chain     | No       | All chains  | Chain name or "all" for cross-chain comparison |
| compareBy | No       | all         | Focus: "tvl", "volume", "apy", or "all"        |

## Workflow

1. **Extract parameters** from the user's request.

2. **Delegate to pool-researcher**: Invoke `Task(subagent_type:pool-researcher)` asking for a comparison of all pools for the token pair. The agent will discover pools across fee tiers and versions, gather data for each, and rank them.

3. **Present comparison**: Format as a comparison table with a clear recommendation.

## Output Format

```text
Pool Comparison: WETH/USDC (Ethereum)

  | Pool       | Fee    | TVL     | Vol 24h  | APY 7d | Depth 1% | Recommended |
  | ---------- | ------ | ------- | -------- | ------ | -------- | ----------- |
  | V3 0.05%   | 5bp    | $332M   | $610M    | 21.3%  | $5M      | Best APY    |
  | V3 0.30%   | 30bp   | $85M    | $45M     | 8.2%   | $2M      |             |
  | V3 1.00%   | 100bp  | $12M    | $3M      | 4.1%   | $500K    |             |
  | V2 0.30%   | 30bp   | $25M    | $8M      | 3.5%   | $1M      |             |

  Recommendation: V3 0.05% pool — highest APY with deepest liquidity.
```

## Important Notes

- Delegates to `pool-researcher` — no direct MCP tool calls.
- Pools with zero liquidity or no activity are excluded from comparison.
- Ranking considers multiple factors: APY, depth, stability, and utilization.

## Error Handling

| Error              | User-Facing Message                        | Suggested Action                |
| ------------------ | ------------------------------------------ | ------------------------------- |
| No pools found     | "No active pools found for X/Y."           | Check token names or try another chain |
| Single pool only   | "Only one pool exists for X/Y."            | Shows single pool analysis instead     |
