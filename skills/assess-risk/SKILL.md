---
name: assess-risk
description: Get an independent risk assessment for any proposed Uniswap operation — swap, LP position, bridge, or token interaction. Evaluates slippage, impermanent loss, liquidity, smart contract, and bridge risks with a clear APPROVE or VETO decision. Use when the user asks if something is safe or wants a risk evaluation.
model: opus
allowed-tools: [Task(subagent_type:risk-assessor)]
---

# Assess Risk

## Overview

Provides an independent, multi-dimensional risk assessment for any proposed Uniswap operation. Delegates to the `risk-assessor` agent, which evaluates risk across 5+ dimensions and produces a composite score with a clear APPROVE, CONDITIONAL_APPROVE, VETO, or HARD_VETO decision.

The risk-assessor is a **terminal node** — it cannot be influenced by other agents. Its assessment is independent and objective, based solely on on-chain data.

## When to Use

Activate when the user asks:

- "Is this trade safe?"
- "Risk assessment for swapping 100 ETH for USDC"
- "Should I LP in this pool?"
- "Evaluate the risk of swapping X for Y"
- "How risky is this pool?"
- "Is it safe to bridge tokens to Base?"
- "What's the risk of LPing with this token?"
- "Check if this token is safe to trade"
- "Risk check before I swap"

## Parameters

| Parameter      | Required | Default    | How to Extract                                              |
| -------------- | -------- | ---------- | ----------------------------------------------------------- |
| operation      | Yes      | —          | Natural language description of what the user wants to do   |
| riskTolerance  | No       | moderate   | "conservative", "moderate", "aggressive"                    |

The `operation` parameter is flexible — it can be:
- A swap: "swap 100 ETH for USDC on Ethereum"
- An LP action: "add $50K liquidity to WETH/USDC V3 0.05%"
- A bridge: "bridge 10 ETH from Ethereum to Base"
- A token check: "is PEPE safe to trade?"
- A pool check: "is the UNI/WETH pool risky?"

## Workflow

1. **Parse the operation** from the user's request. Identify:
   - Operation type: swap, add liquidity, remove liquidity, bridge, or token check
   - Tokens involved
   - Amounts
   - Chain(s)
   - Pool (if applicable)

2. **Delegate to risk-assessor**: Invoke `Task(subagent_type:risk-assessor)` with the parsed operation details and risk tolerance. The agent evaluates:

   | Dimension        | What It Checks                                              |
   | ---------------- | ----------------------------------------------------------- |
   | Slippage         | Price impact for the trade size vs pool liquidity            |
   | Impermanent Loss | Expected IL based on pair volatility (LP operations only)   |
   | Liquidity        | Can the position be exited? TVL vs position size ratio      |
   | Smart Contract   | Pool age, Uniswap version, hook audit status (V4)           |
   | Bridge           | Bridge mechanism reliability, liquidity (cross-chain only)  |

3. **Present the assessment** clearly with per-dimension scores and a final decision.

## Output Format

```text
Risk Assessment

  Operation: Swap 100 ETH for USDC on Ethereum
  Risk Tolerance: Moderate
  Decision: APPROVE

  Risk Dimensions:
    Slippage:        LOW  (0.3% price impact — sufficient liquidity)
    Liquidity:       LOW  (TVL 250x trade size — deep pool)
    Smart Contract:  LOW  (V3 pool, 18 months old, battle-tested)
    Bridge:          N/A  (not a cross-chain operation)

  Composite Risk: LOW
  
  Conditions: None — safe to proceed

  HARD VETO Checks:
    ✓ Verified tokens
    ✓ Pool TVL > $1,000
    ✓ Price impact < 10%
```

### For a VETO:

```text
Risk Assessment

  Operation: LP $50K into NEWTOKEN/WETH 0.3% V4 (Ethereum)
  Risk Tolerance: Conservative
  Decision: VETO

  Risk Dimensions:
    Slippage:        MEDIUM  (1.2% entry impact due to low liquidity)
    Impermanent Loss: HIGH   (>25% annual estimate — extremely volatile pair)
    Liquidity:       HIGH    (TVL only 8x position size — exit risk)
    Smart Contract:  HIGH    (V4 pool with unaudited hook contract)
    Bridge:          N/A

  Composite Risk: HIGH (exceeds conservative tolerance)

  Why VETO:
    - Impermanent loss estimate exceeds 20% annually
    - V4 hook contract is unaudited — elevated smart contract risk
    - Position would represent 12% of pool TVL — concentration risk

  Mitigations (if you still want to proceed):
    - Reduce position size to < 1% of pool TVL ($4,200)
    - Use a wider range to reduce IL exposure
    - Wait for hook contract audit
    - Switch to risk tolerance "aggressive" (not recommended)
```

### For a HARD VETO:

```text
Risk Assessment

  Operation: Swap 1000 ETH for SCAMTOKEN
  Decision: HARD VETO (non-overridable)

  HARD VETO Trigger: Unverified token contract
  
  SCAMTOKEN (0x1234...5678) failed verification:
    - Not on any verified token list
    - Contract deployed < 24 hours ago
    - No trading history

  This operation CANNOT proceed regardless of risk tolerance.
  Hard vetoes protect against potential rug pulls and scam tokens.

  Suggestion: Use "research-token SCAMTOKEN" to investigate further.
```

## Important Notes

- The risk-assessor is a **terminal, independent node**. Its assessment cannot be overridden by other agents.
- **HARD VETO** decisions are non-negotiable — they trigger for: unverified tokens, pool TVL < $1K, price impact > 10%, bridge amount exceeding bridge liquidity.
- This skill assesses risk but does **not execute** any operations. It's a "should I?" check before acting.
- For LP operations, IL risk is always evaluated alongside the other dimensions.
- When data is insufficient, the risk-assessor defaults to HIGH risk for the affected dimension rather than guessing.

## Error Handling

| Error                | User-Facing Message                                       | Suggested Action                     |
| -------------------- | --------------------------------------------------------- | ------------------------------------ |
| Cannot parse operation | "I need more details. What exactly are you planning?"   | Ask user to describe the operation   |
| Token not found      | "Could not find token X."                                 | Provide contract address             |
| Pool data unavailable| "Cannot access pool data for risk analysis."              | Try again later                      |
| Agent unavailable    | "Risk assessor is not available."                         | Check agent configuration            |
