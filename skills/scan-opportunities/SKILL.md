---
name: scan-opportunities
description: Scan for LP opportunities, arbitrage, and high-yield pools across all Uniswap deployments. Use when the user asks about the best opportunities, high-yield pools, or arbitrage.
model: opus
allowed-tools: [Task(subagent_type:opportunity-scanner)]
---

# Scan Opportunities

## Overview

Scans across all Uniswap deployments for LP opportunities, price discrepancies, and high-yield pools. Delegates to the `opportunity-scanner` agent which analyzes pools, compares prices, and evaluates emerging opportunities.

## When to Use

Activate when the user asks:

- "Find best LP opportunities"
- "Any arbitrage opportunities?"
- "Show me high-yield pools"
- "New pools with good volume"
- "Where should I LP?"
- "What are the best opportunities right now?"

## Parameters

| Parameter      | Required | Default    | Description                                        |
| -------------- | -------- | ---------- | -------------------------------------------------- |
| type           | No       | all        | "lp", "arb", "new-pools", or "all"                 |
| chains         | No       | All chains | Specific chains or "all"                            |
| riskTolerance  | No       | moderate   | "conservative", "moderate", "aggressive"            |
| minTvl         | No       | $50,000    | Minimum TVL filter for pool consideration           |

## Workflow

1. **Extract parameters** from the user's request: identify opportunity type, chain filter, risk tolerance, and minimum TVL.

2. **Delegate to opportunity-scanner**: Invoke `Task(subagent_type:opportunity-scanner)` with the parameters. The agent scans LP opportunities (high APY pools), arbitrage opportunities (>0.5% spread after fees), and emerging pools (>100% volume growth in 7d).

3. **Present results**: Format as a ranked list of opportunities with risk ratings.

## Output Format

```text
Opportunities Found: 5

  1. LP: WETH/USDC 0.05% (Ethereum)
     APY: 21.3% | TVL: $332M | Risk: LOW
     Why: Highest volume-to-TVL ratio on mainnet

  2. LP: ARB/WETH 0.30% (Arbitrum)
     APY: 35.2% | TVL: $12M | Risk: MEDIUM
     Why: Growing volume trend (+45% 7d)

  3. New Pool: AGENT/WETH 0.30% (Base)
     APY: 120%* | TVL: $500K | Risk: HIGH
     Why: New pool with strong early volume (*projected, limited data)
```

## Important Notes

- All APY figures are historical estimates, not guaranteed returns.
- High-APY opportunities often carry higher risk (IL, low TVL, new tokens).
- Each opportunity is risk-rated by the agent's internal risk assessment.
- Arbitrage opportunities are ephemeral and may disappear before execution.

## Error Handling

| Error                     | User-Facing Message                              | Suggested Action                  |
| ------------------------- | ------------------------------------------------ | --------------------------------- |
| No opportunities found    | "No opportunities matching your criteria found."  | Adjust risk tolerance or min TVL  |
| Chain unreachable         | "Could not scan [chain]. Data may be incomplete." | Try again or narrow chain scope   |
