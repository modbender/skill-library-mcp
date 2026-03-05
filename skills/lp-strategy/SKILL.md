---
name: lp-strategy
description: Comprehensive LP strategy comparison for a token pair — evaluates all versions, fee tiers, range widths, and rebalance approaches side-by-side with APY, IL, gas costs, and risk ratings. Use when the user wants to compare LP options or see a detailed analysis of all strategies.
model: opus
allowed-tools: [Task(subagent_type:lp-strategist), Task(subagent_type:pool-researcher)]
---

# LP Strategy Comparison

## Overview

Produces a comprehensive, multi-strategy comparison for LP positions on a token pair. Unlike `optimize-lp` which gives a single recommendation, this skill presents **all viable strategies side-by-side** with detailed pros/cons, enabling the user to make an informed decision.

This is the "deep dive" version — use when the user wants to understand all their options, not just the top pick.

## When to Use

Activate when the user asks:

- "Compare LP strategies for ETH/USDC"
- "What are my options for LPing into X/Y?"
- "Detailed LP analysis for WETH/USDC"
- "Show me all fee tiers for this pair"
- "V2 vs V3 vs V4 comparison for X/Y"
- "Give me a full breakdown of LP options"
- "I want to understand the tradeoffs before LPing"

## Parameters

| Parameter  | Required | Default    | How to Extract                                    |
| ---------- | -------- | ---------- | ------------------------------------------------- |
| token0     | Yes      | —          | First token                                       |
| token1     | Yes      | —          | Second token                                      |
| capital    | No       | —          | Amount available for LP                           |
| chain      | No       | All chains | Specific chain or "all" for cross-chain comparison|
| strategies | No       | All        | Specific strategies to compare (usually "all")    |

## Workflow

1. **Extract parameters** from the user's request.

2. **Delegate to pool-researcher**: First, get a full pool comparison across all fee tiers and versions via `Task(subagent_type:pool-researcher)`. This provides the data foundation (TVL, volume, APY per pool).

3. **Delegate to lp-strategist**: Invoke `Task(subagent_type:lp-strategist)` in comprehensive comparison mode. The agent evaluates every viable combination:
   - V2 full-range (passive)
   - V3 narrow range per fee tier
   - V3 medium range per fee tier
   - V3 wide range per fee tier
   - V4 options (if available)
   - Cross-chain opportunities (if chain="all")

4. **Present comparison table** with all strategies ranked and annotated with pros/cons.

## Output Format

```text
LP Strategy Comparison: WETH/USDC

  Pair Type: Stable-Volatile (moderate volatility)
  Best Overall: V3 0.05%, Medium Range (see row 2 below)

  ┌────┬──────────────────┬────────┬──────────┬───────┬──────────┬──────────┬────────┐
  │ #  │ Strategy         │ Chain  │ Fee APY  │ IL    │ Net APY  │ Rebal.   │ Risk   │
  ├────┼──────────────────┼────────┼──────────┼───────┼──────────┼──────────┼────────┤
  │ 1  │ V3 0.05% Narrow  │ ETH    │ 35%      │ -12%  │ 23%      │ Weekly   │ HIGH   │
  │ 2  │ V3 0.05% Medium  │ ETH    │ 21%      │ -6%   │ 15%      │ Bi-weekly│ MEDIUM │
  │ 3  │ V3 0.05% Wide    │ ETH    │ 12%      │ -2%   │ 10%      │ Monthly  │ LOW    │
  │ 4  │ V3 0.30% Medium  │ ETH    │ 8%       │ -6%   │ 2%       │ Bi-weekly│ MEDIUM │
  │ 5  │ V3 0.05% Medium  │ Base   │ 18%      │ -5%   │ 13%      │ Bi-weekly│ MEDIUM │
  │ 6  │ V2 0.30% Full    │ ETH    │ 4%       │ -1%   │ 3%       │ Never    │ LOW    │
  └────┴──────────────────┴────────┴──────────┴───────┴──────────┴──────────┴────────┘

  Strategy Details:

  #1 V3 0.05% Narrow (±5%) — HIGH RISK, HIGH REWARD
    Pros: Highest fee capture, maximum capital efficiency
    Cons: Frequent rebalancing ($15/rebalance on mainnet), high IL risk
    Best for: Active managers with >$10K positions
    Gas warning: Break-even ~3 days per rebalance

  #2 V3 0.05% Medium (±15%) — RECOMMENDED
    Pros: Strong APY with manageable rebalancing, 80%+ time-in-range
    Cons: Moderate IL during large moves
    Best for: Most LPs with $1K+ positions
    Gas warning: Break-even ~1 day per rebalance

  #3 V3 0.05% Wide (±50%) — LOW MAINTENANCE
    Pros: Rarely needs rebalancing, low IL, almost passive
    Cons: Lower capital efficiency, lower APY
    Best for: Passive LPs, small positions where gas matters

  #6 V2 0.30% Full Range — SET AND FORGET
    Pros: Zero maintenance, no range management, battle-tested
    Cons: Lowest returns, less capital efficient
    Best for: First-time LPs, long-term holders who don't want to manage

  Ready to proceed? Choose a strategy and say "Add liquidity with strategy #2"
```

## Important Notes

- This skill produces **analysis, not execution**. To act on a strategy, use `manage-liquidity`.
- Net APY = Fee APY - Expected IL. Always show both components.
- Gas costs for rebalancing are factored into the comparison for each chain.
- Cross-chain comparison (when chain="all") highlights L2 gas advantages.
- The lp-strategist internally uses `pool-researcher` for data and `risk-assessor` for risk evaluation.

## Error Handling

| Error                | User-Facing Message                                       | Suggested Action                    |
| -------------------- | --------------------------------------------------------- | ----------------------------------- |
| Token not found      | "Could not find token X."                                 | Provide contract address            |
| No pools exist       | "No pools found for X/Y."                                 | Try different tokens or chain       |
| Insufficient data    | "Not enough data for a reliable comparison."              | Pool may be too new                 |
| Agent unavailable    | "LP strategist is not available."                         | Check agent configuration           |
