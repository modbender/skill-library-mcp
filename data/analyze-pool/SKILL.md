---
name: analyze-pool
description: Analyze a specific Uniswap pool's performance, liquidity depth, fee APY, and risk factors. Use when the user asks about pool metrics, TVL, volume, or whether a pool is good for LPing.
model: opus
allowed-tools: [Task(subagent_type:pool-researcher)]
---

# Analyze Pool

## Overview

Provides a detailed analysis of a specific Uniswap pool by delegating to the `pool-researcher` agent. Returns TVL, volume, fee APY, liquidity depth, concentration metrics, and risk factors.

## When to Use

Activate when the user asks:

- "Analyze the ETH/USDC pool"
- "What's the TVL of X/Y pool?"
- "How much volume does the WETH/USDC pool do?"
- "What's the fee APY for ETH/USDC?"
- "Is this pool good for LPing?"
- "Pool info for ETH/USDC on Base"
- "How deep is the liquidity in this pool?"

## Parameters

| Parameter | Required | Default     | Description                                   |
| --------- | -------- | ----------- | --------------------------------------------- |
| token0    | Yes      | —           | First token name, symbol, or address          |
| token1    | Yes      | —           | Second token name, symbol, or address         |
| chain     | No       | ethereum    | Chain name (ethereum, base, arbitrum, etc.)    |
| feeTier   | No       | Auto-detect | Fee tier (e.g., "0.05%", "30bp", "3000")      |
| version   | No       | Auto-detect | Protocol version: "v2", "v3", or "v4"         |

## Workflow

1. **Extract parameters** from the user's request: identify token0, token1, chain, fee tier, and version.

2. **Delegate to pool-researcher**: Invoke `Task(subagent_type:pool-researcher)` with the extracted parameters. The pool-researcher will gather on-chain data, calculate metrics, and produce a structured report.

3. **Present results**: Format the pool-researcher's report into a user-friendly summary covering:
   - Pool identification (address, version, fee tier)
   - Current state (price, TVL, liquidity)
   - Performance (fee APY 7d/30d, volume 24h/7d, utilization)
   - Liquidity depth (trade size at < 1% impact)
   - Risk factors (if any)

## Output Format

Present a clean summary:

```text
Pool Analysis: WETH/USDC 0.05% (V3, Ethereum)

  Address: 0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640
  TVL:     $332M
  Price:   $1,963.52

  Performance:
    Fee APY (7d):  21.3%
    Fee APY (30d): 6.65%
    Volume (24h):  $610M
    Utilization:   1.84x

  Liquidity Depth:
    1% impact: $5M trade size
    5% impact: $25M trade size
    Concentration: 78.5% within ±2% of price

  Risk Factors: None identified
```

## Important Notes

- This skill delegates entirely to the `pool-researcher` agent — it does not call MCP tools directly.
- If the pool doesn't exist, the agent will report this clearly.
- Fee APY is historical (not guaranteed). The output distinguishes realized vs projected APY.

## Error Handling

| Error                    | User-Facing Message                          | Suggested Action                |
| ------------------------ | -------------------------------------------- | ------------------------------- |
| Pool not found           | "No pool found for X/Y on this chain."       | Try different fee tier or chain |
| Token not recognized     | "Could not resolve token X."                 | Provide contract address        |
| Insufficient data        | "Limited data available for this pool."       | Pool may be too new             |
