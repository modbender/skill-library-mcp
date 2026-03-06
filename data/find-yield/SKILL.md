---
name: find-yield
description: Find the highest-yield LP pools on Uniswap filtered by risk tolerance and minimum TVL. Use when the user asks about the best yields, highest APY pools, or where to earn fees.
model: opus
allowed-tools: [Task(subagent_type:opportunity-scanner)]
---

# Find Yield

## Overview

Finds the highest-yield LP opportunities on Uniswap, filtered by risk tolerance, minimum TVL, and optionally capital amount. This is a focused version of `scan-opportunities` that only returns LP yield opportunities (no arbitrage or new-pool scanning).

Delegates to the `opportunity-scanner` agent with an LP-only filter.

## When to Use

Activate when the user asks:

- "Best yield on Uniswap"
- "Highest APY pools"
- "Where to earn fees"
- "Best LP returns"
- "Top yielding pools"
- "Where can I earn the most?"

## Parameters

| Parameter      | Required | Default    | Description                                     |
| -------------- | -------- | ---------- | ----------------------------------------------- |
| chains         | No       | All chains | Specific chains or "all"                         |
| riskTolerance  | No       | moderate   | "conservative", "moderate", "aggressive"         |
| capital        | No       | —          | Available capital (helps rank appropriately)     |
| minTvl         | No       | $100,000   | Minimum TVL for pool consideration               |

## Workflow

1. **Extract parameters** from the user's request.

2. **Delegate to opportunity-scanner**: Invoke `Task(subagent_type:opportunity-scanner)` with `type: "lp"` and the user's filters. The agent scans pools, ranks by fee APY adjusted for risk, and returns the top opportunities.

3. **Present results**: Format as a ranked yield table.

## Output Format

```text
Top LP Yields (moderate risk, min $100K TVL):

  | Rank | Pool                | Chain    | APY 7d | TVL    | Risk   |
  | ---- | ------------------- | -------- | ------ | ------ | ------ |
  | 1    | WETH/USDC 0.05%     | Ethereum | 21.3%  | $332M  | LOW    |
  | 2    | ARB/WETH 0.30%      | Arbitrum | 18.5%  | $15M   | MEDIUM |
  | 3    | WETH/USDC 0.05%     | Base     | 15.2%  | $45M   | LOW    |
  | 4    | WBTC/WETH 0.30%     | Ethereum | 12.1%  | $120M  | LOW    |
  | 5    | OP/WETH 0.30%       | Optimism | 11.8%  | $8M    | MEDIUM |

  Note: APY is based on 7-day historical fee revenue. Past performance
  does not guarantee future returns. IL risk not included in APY figures.
```

## Important Notes

- APY figures are historical, not guaranteed. Always consider IL risk.
- Higher APY often correlates with higher risk.
- Conservative risk tolerance filters out pools with < $1M TVL and volatile pairs.
- Risk-adjusted yield accounts for estimated impermanent loss.

## Error Handling

| Error                     | User-Facing Message                              | Suggested Action                        |
| ------------------------- | ------------------------------------------------ | --------------------------------------- |
| No yields found           | "No pools match your risk/TVL criteria."          | Lower minTvl or increase risk tolerance |
| Chain unreachable         | "Could not scan [chain]. Data may be incomplete." | Try again or narrow chain scope         |
