---
name: optimize-lp
description: Get the optimal LP strategy for a token pair — recommends version (V2/V3/V4), fee tier, range width, and rebalance approach based on pair characteristics, historical data, and risk tolerance. Use when the user asks how to LP, what range to use, or which version/fee tier is best.
model: opus
allowed-tools: [Task(subagent_type:lp-strategist)]
---

# Optimize LP

## Overview

Provides a focused, actionable LP strategy recommendation for a specific token pair. Delegates to the `lp-strategist` agent, which analyzes pair volatility, evaluates version options, selects the optimal fee tier, calculates the best range width, and designs a rebalance strategy — all backed by on-chain data and risk analysis.

This skill answers the question: **"How should I LP into X/Y?"** with a concrete, implementable answer.

## When to Use

Activate when the user asks:

- "Best LP strategy for ETH/USDC"
- "How should I LP $10K into ETH/USDC?"
- "Tight or wide range for WETH/USDC?"
- "V2 or V3 for this pair?"
- "What fee tier should I use for UNI/WETH?"
- "Optimize my LP approach for X/Y"
- "What range should I set for my ETH/USDC position?"
- "Should I use concentrated liquidity for this pair?"

## Parameters

| Parameter      | Required | Default    | How to Extract                                          |
| -------------- | -------- | ---------- | ------------------------------------------------------- |
| token0         | Yes      | —          | First token: "ETH", "WETH", "USDC", or 0x address      |
| token1         | Yes      | —          | Second token                                            |
| capital        | No       | —          | Amount to LP: "$10K", "5 ETH", "$50,000"                |
| chain          | No       | ethereum   | "ethereum", "base", "arbitrum", etc.                    |
| riskTolerance  | No       | moderate   | "conservative", "moderate", "aggressive"                |

## Workflow

1. **Extract parameters** from the user's request. Identify the token pair, capital amount (if mentioned), chain, and risk tolerance.

2. **Delegate to lp-strategist**: Invoke `Task(subagent_type:lp-strategist)` with the parameters. The agent performs a 7-step analysis:
   - Classifies the pair (stable-stable, stable-volatile, volatile-volatile)
   - Evaluates V2 vs V3 vs V4 tradeoffs
   - Selects optimal fee tier with data backing
   - Calculates range width targeting >80% time-in-range
   - Designs rebalance strategy with gas cost analysis
   - Gets independent risk assessment from risk-assessor
   - Produces a recommendation with conservative/moderate/optimistic estimates

3. **Present the strategy** as a clear, actionable recommendation with specific numbers.

## Output Format

```text
LP Strategy for WETH/USDC

  Recommendation: V3, 0.05% fee tier
  Pool: 0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640 (Ethereum)

  Range: $1,668 - $2,258 (±15%, medium strategy)
  Expected time-in-range: ~82%

  Expected Returns (annualized):
    Conservative: 8.5% APY (after IL)
    Moderate:     15.2% APY (after IL)
    Optimistic:   24.1% APY (after IL)

  Expected IL:
    Conservative: 2.1%
    Moderate:     5.8%
    Worst case:   12.3%

  Rebalance Strategy:
    Trigger: Price within 10% of range boundary
    Frequency: Every 2-3 weeks (estimated)
    Gas cost: ~$15 per rebalance

  Risk Assessment: MEDIUM (approved by risk-assessor)

  Alternatives Considered:
    V3 0.3%: Lower APY (8%) but less competition
    V2: No range management, ~4% APY — good for passive
    Narrow range (±5%): Higher APY but needs weekly rebalancing

  Ready to add liquidity? Say "Add liquidity to WETH/USDC"
```

## Important Notes

- This skill provides a **strategy recommendation**, not execution. To act on it, use the `manage-liquidity` skill.
- All APY estimates are based on historical data. Past performance does not guarantee future returns.
- IL estimates are always shown alongside fee APY — never fee APY alone.
- For small positions (<$1K), the recommendation accounts for gas costs eating into returns.
- The lp-strategist internally delegates to `pool-researcher` for data and `risk-assessor` for risk evaluation.

## Error Handling

| Error                | User-Facing Message                                      | Suggested Action                     |
| -------------------- | -------------------------------------------------------- | ------------------------------------ |
| Token not found      | "Could not find token X on Uniswap."                    | Provide contract address             |
| No pools exist       | "No pools found for X/Y on this chain."                  | Try different chain or check tokens  |
| Insufficient data    | "Not enough historical data to produce a reliable strategy." | Pool may be too new              |
| Agent unavailable    | "LP strategist is not available."                        | Check agent configuration            |
