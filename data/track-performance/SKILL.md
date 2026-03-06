---
name: track-performance
description: Track the performance of Uniswap LP positions over time — check which positions need attention, are out of range, or have uncollected fees. Use when the user asks how their positions are doing.
model: opus
allowed-tools: [Task(subagent_type:portfolio-analyst)]
---

# Track Performance

## Overview

Tracks the performance of Uniswap LP positions with a focus on changes and alerts since the last review. Delegates to the `portfolio-analyst` agent to check position status, fee accumulation, and identify positions needing attention.

## When to Use

Activate when the user asks:

- "How are my positions doing?"
- "Check my LP performance"
- "Any positions need attention?"
- "Which positions are out of range?"
- "How much have I earned today?"
- "Position status update"

## Parameters

| Parameter | Required | Default                 | Description                              |
| --------- | -------- | ----------------------- | ---------------------------------------- |
| wallet    | No       | Configured agent wallet | Wallet address to track                  |
| chains    | No       | All chains              | Specific chains or "all"                  |
| since     | No       | Last check              | Time period: "24h", "7d", "30d"           |

## Workflow

1. **Extract parameters** from the user's request: identify wallet, chain filter, and time period.

2. **Delegate to portfolio-analyst**: Invoke `Task(subagent_type:portfolio-analyst)` with a focus on performance tracking and alerts. The agent checks all positions, identifies status changes, and flags positions needing attention.

3. **Present results**: Format as a performance summary with actionable alerts.

## Output Format

```text
Performance Update (last 24h)

  Overall: +$320 (+0.26%)

  Positions:
    USDC/WETH 0.05% (Ethereum) — IN RANGE ✓
      Fees earned (24h): $180
      Value change:      +$120
      Status: Healthy

    UNI/WETH 0.30% (Ethereum) — OUT OF RANGE ⚠
      Fees earned (24h): $0 (not earning — out of range)
      Value change:      -$50
      Status: Needs rebalance

  Action Items:
    1. Rebalance UNI/WETH position (out of range since 6h ago)
    2. Consider collecting $1,200 in accumulated fees from UNI/WETH
```

## Important Notes

- Delegates entirely to `portfolio-analyst` — no direct MCP tool calls.
- "Out of range" positions are not earning fees and may need rebalancing.
- Action items are suggestions, not automatic actions.
- Performance data may be slightly delayed due to RPC/subgraph sync.

## Error Handling

| Error                | User-Facing Message                              | Suggested Action              |
| -------------------- | ------------------------------------------------ | ----------------------------- |
| Wallet not configured | "No wallet configured."                          | Set WALLET_TYPE + PRIVATE_KEY |
| No positions found   | "No Uniswap positions found."                    | Wallet may not have LP'd      |
| Data stale           | "Position data may be delayed."                  | Try again in a few minutes    |
