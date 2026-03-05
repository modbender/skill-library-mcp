---
name: portfolio-report
description: Generate a comprehensive portfolio report for a wallet's Uniswap positions across all chains — covering total value, PnL, fee earnings, impermanent loss, and composition. Use when the user asks about their positions, earnings, or portfolio overview.
model: opus
allowed-tools: [Task(subagent_type:portfolio-analyst)]
---

# Portfolio Report

## Overview

Generates a comprehensive portfolio report for a wallet's Uniswap positions across all supported chains. Delegates to the `portfolio-analyst` agent to discover positions, calculate PnL, track fee earnings, and analyze composition.

## When to Use

Activate when the user asks:

- "Show me my positions"
- "Portfolio report"
- "What's my Uniswap PnL?"
- "How much have I earned in fees?"
- "Which positions are out of range?"
- "What's my portfolio worth?"
- "Summarize my LP positions"

## Parameters

| Parameter | Required | Default              | Description                                |
| --------- | -------- | -------------------- | ------------------------------------------ |
| wallet    | No       | Configured agent wallet | Wallet address to analyze               |
| chains    | No       | All chains           | Specific chains or "all"                   |
| focus     | No       | full                 | "positions", "pnl", "fees", or "full"      |

## Workflow

1. **Extract parameters** from the user's request: identify wallet address, chain filter, and focus area.

2. **Delegate to portfolio-analyst**: Invoke `Task(subagent_type:portfolio-analyst)` with the parameters. The agent discovers all positions across chains, values them, calculates PnL, and analyzes composition.

3. **Present results**: Format the portfolio report as a user-friendly summary.

## Output Format

```text
Portfolio Report: 0xf39F...2266

  Total Value: $125,000
    LP Positions: $95,000
    Idle Tokens:  $28,000
    Uncollected:  $2,000

  PnL Summary:
    Realized:    +$5,200
    Unrealized:  +$3,800
    Gas Costs:   -$450
    Net PnL:     +$8,550 (+7.3%)

  Positions (2):
    1. USDC/WETH 0.05% (V3, Ethereum) — IN RANGE
       Value: $50,000 | PnL: +$2,000 | Fees: $800 uncollected
    2. UNI/WETH 0.30% (V3, Ethereum) — OUT OF RANGE
       Value: $45,000 | PnL: +$2,000 | Fees: $1,200 uncollected

  Recommendations:
    - Collect $1,200 in fees from UNI/WETH position
    - Rebalance UNI/WETH position (currently out of range)
```

## Important Notes

- Delegates entirely to `portfolio-analyst` — no direct MCP tool calls.
- PnL includes gas costs. A position may be profitable before gas but unprofitable after.
- IL is reported as both absolute dollar value and percentage.
- Data may be slightly delayed due to RPC/subgraph sync.

## Error Handling

| Error                | User-Facing Message                              | Suggested Action              |
| -------------------- | ------------------------------------------------ | ----------------------------- |
| Wallet not configured | "No wallet configured."                          | Set WALLET_TYPE + PRIVATE_KEY |
| No positions found   | "No Uniswap positions found for this wallet."    | Wallet may not have LP'd      |
| Chain unreachable    | "Could not connect to X chain."                  | Try again later               |
