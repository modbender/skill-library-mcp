---
name: research-token
description: Research a token's Uniswap liquidity, volume profile, pool distribution, and risk factors. Use when the user asks about a token's tradability, liquidity depth, or wants due diligence.
model: opus
allowed-tools: [Task(subagent_type:token-analyst)]
---

# Research Token

## Overview

Performs comprehensive due diligence on a token from a Uniswap protocol perspective. Delegates to the `token-analyst` agent to analyze liquidity across all pools, volume trends, and risk factors.

## When to Use

Activate when the user asks:

- "Research UNI token"
- "Is there enough liquidity for X?"
- "Token analysis for PEPE"
- "Due diligence on this token"
- "What pools trade X?"
- "How liquid is X on Uniswap?"
- "Is X safe to trade?"

## Parameters

| Parameter | Required | Default      | Description                                    |
| --------- | -------- | ------------ | ---------------------------------------------- |
| token     | Yes      | —            | Token name, symbol, or contract address         |
| chain     | No       | All chains   | Specific chain or "all" for cross-chain view   |
| focus     | No       | Full analysis| "liquidity", "volume", or "risk"               |

## Workflow

1. **Extract parameters** from the user's request: identify the token and any chain/focus filters.

2. **Delegate to token-analyst**: Invoke `Task(subagent_type:token-analyst)` with the token identifier. The agent resolves the token, discovers all pools, analyzes liquidity and volume, and produces a risk assessment.

3. **Present results**: Format the token-analyst's report into a user-friendly summary.

## Output Format

```text
Token Research: UNI (Uniswap)

  Address:  0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
  Chains:   Ethereum, Arbitrum, Optimism, Polygon, Base
  Pools:    24 active pools across all chains

  Liquidity:
    Total TVL:   $85M across all pools
    Best pool:   WETH/UNI 0.3% (49.4% of liquidity)
    Depth (1%):  $2.5M trade size
    Fragmentation: Moderate

  Volume:
    24h: $15M | 7d: $95M | 30d: $380M
    Trend: Stable
    Turnover: 0.18x daily

  Risk Factors:
    - Moderate pool concentration (49.4% in one pool) — LOW severity

  Trading: Suitable for trades up to $2.5M with < 1% price impact
```

## Important Notes

- Delegates entirely to `token-analyst` — no direct MCP tool calls.
- The analysis is from a Uniswap protocol perspective only — not a general investment analysis.
- Risk factors are based on observable on-chain metrics, not price predictions.

## Error Handling

| Error                | User-Facing Message                              | Suggested Action              |
| -------------------- | ------------------------------------------------ | ----------------------------- |
| Token not found      | "Could not find token X on Uniswap."             | Provide contract address      |
| No pools             | "No Uniswap pools found for this token."          | Token may not be listed       |
| Insufficient data    | "Limited trading data available for this token."  | Token may be too new          |
