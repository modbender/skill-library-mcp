---
name: rebalance-position
description: Rebalance an out-of-range Uniswap V3/V4 LP position by closing the old position and opening a new one centered on the current price. Handles fee collection, removal, range calculation, and re-entry in a single workflow. Use when a position is out of range and needs adjustment.
model: opus
allowed-tools: [Task(subagent_type:liquidity-manager), mcp__uniswap__get_positions_by_owner, mcp__uniswap__get_position, mcp__uniswap__get_pool_info]
---

# Rebalance Position

## Overview

When a V3/V4 LP position goes out of range, it stops earning fees. This skill handles the full rebalance workflow: collect accumulated fees, close the old position, calculate a new optimal range centered on the current price, and open a new position — all in a single operation.

This is a high-value skill because out-of-range positions are effectively dead capital. The difference between a monitored position that gets rebalanced promptly and an unmonitored one can be 15-30% APY in lost fee revenue.

## When to Use

Activate when the user says:

- "Rebalance my position"
- "My position is out of range"
- "Adjust my LP range"
- "Re-center my liquidity"
- "Position #12345 is out of range, fix it"
- "My ETH/USDC position stopped earning"
- "Move my range to the current price"
- "My LP isn't earning fees anymore"

Also proactively suggest rebalancing when:
- A `track-performance` or `portfolio-report` shows an out-of-range position
- The user asks "why am I not earning fees?"

## Parameters

| Parameter    | Required | Default       | How to Extract                                           |
| ------------ | -------- | ------------- | -------------------------------------------------------- |
| positionId   | No*      | —             | Position ID, or "my ETH/USDC position" (resolved by search) |
| chain        | No       | ethereum      | Chain where the position lives                            |
| newRange     | No       | Auto-optimal  | "narrow" (±5%), "medium" (±15%), "wide" (±50%)           |

*If no position ID: search with `get_positions_by_owner`, filter for out-of-range positions, and confirm with the user.

## Workflow

### Pre-Rebalance Analysis

Before executing anything, gather data and present the situation to the user:

```
Step 1: IDENTIFY THE POSITION
├── If position ID given → fetch via get_position
├── If "my X/Y position" → search via get_positions_by_owner
│   ├── Filter by token pair and out-of-range status
│   ├── If multiple out-of-range → list all, ask which one
│   └── If none out-of-range → "All your positions are in range!"
└── Validate: confirm the position IS actually out of range

Step 2: ANALYZE CURRENT SITUATION
├── Current pool state via get_pool_info
│   ├── Current price
│   ├── Pool TVL, volume, fee APY
│   └── Tick distribution (where is liquidity concentrated?)
├── Position details
│   ├── Current tick range (lower, upper)
│   ├── How far out of range (above or below?)
│   ├── Uncollected fees
│   ├── Current token balances in position
│   └── Time since going out of range (if estimable)
└── Cost-benefit calculation
    ├── Estimated gas cost for full rebalance (remove + add = ~$30-60 on mainnet)
    ├── Estimated daily fee revenue if rebalanced (from pool APY + position size)
    ├── Break-even time: gas_cost / daily_revenue
    └── If break-even > 30 days → WARN that rebalancing may not be worth it
```

### Present the Rebalance Plan

Before executing, show the user exactly what will happen:

```text
Rebalance Plan for Position #12345

  Current Situation:
    Pool:      WETH/USDC 0.05% (V3, Ethereum)
    Status:    OUT OF RANGE ⚠ (price moved above your range)
    Current:   $1,963
    Your range: $1,500 - $1,800 (position is 9% above upper bound)
    
  Uncollected Fees: 0.01 WETH ($19.60) + 15.20 USDC ($15.20)
  Position Value: ~$3,940

  Proposed New Range:
    Strategy: Medium (±15%)
    Lower:    $1,668 (current - 15%)
    Upper:    $2,258 (current + 15%)
    Expected time-in-range: ~80-85%

  Cost:
    Gas (remove + add): ~$35
    Break-even: ~2 days at current fee APY

  Steps:
    1. Collect uncollected fees ($34.80)
    2. Remove all liquidity from position #12345
    3. Add liquidity at new range ($1,668 - $2,258)
    4. New position created with new NFT ID

  Proceed? (yes/no)
```

### Execution (after user confirms)

```
Step 3: DELEGATE TO LIQUIDITY-MANAGER
├── The agent executes atomically:
│   a. Collect fees from old position
│   b. Remove 100% liquidity from old position
│   c. Calculate new tick range based on:
│      - Current pool price
│      - Selected range strategy (narrow/medium/wide)
│      - Pool tick spacing
│   d. Approve tokens for new position (if needed)
│   e. Add liquidity at new range
│   f. Each step validated by safety-guardian
└── Returns: old position closed, fees collected, new position ID, new range, tx hashes

Step 4: PRESENT RESULT
├── Confirmation of old position closure
├── Fees collected (amounts + USD)
├── New position details (ID, range, amounts deposited)
├── Total gas cost for the operation
├── Net cost/benefit of the rebalance
└── Next steps for monitoring
```

## Range Strategy Guide

When the user doesn't specify a range, use this decision framework:

| Pair Type             | Recommended Range | Width  | Rationale                                           |
| --------------------- | ----------------- | ------ | --------------------------------------------------- |
| Stable-stable         | Narrow            | ±0.5%  | Price barely moves; maximize capital efficiency     |
| Stable-volatile       | Medium            | ±15%   | Balance between earning and avoiding rebalance      |
| Volatile-volatile     | Wide              | ±30%   | Reduce rebalance frequency; accept lower APY        |
| User says "aggressive"| Narrow            | ±5%    | Higher fees but frequent rebalancing needed         |
| User says "passive"   | Wide              | ±50%   | Low maintenance, lower returns                      |
| Small position (<$1K) | Wide              | ±50%   | Gas costs make frequent rebalancing uneconomical    |

## When NOT to Rebalance

Proactively advise against rebalancing in these situations:

| Situation                                 | Advice                                                       |
| ----------------------------------------- | ------------------------------------------------------------ |
| Position size < 10x gas cost              | "Gas would cost ${gas} but your position is only ${value}."  |
| Price is near range boundary (within 2%)  | "Price is close to your range — wait to see if it re-enters."|
| Position went out of range < 1 hour ago   | "Give it time — price may return to your range."             |
| User has no strong view on direction      | "Consider a wider range to reduce future rebalances."        |
| Break-even time > 14 days                 | "At current fee rates, rebalancing won't pay for itself for {days} days." |

## Output Format

### Successful Rebalance

```text
Position Rebalanced Successfully

  Old Position: #12345 (CLOSED)
    Received: 0.52 WETH + 950 USDC ($1,970)
    Fees collected: 0.01 WETH + 15.20 USDC ($34.80)

  New Position: #67890
    Pool: WETH/USDC 0.05% (V3, Ethereum)
    Deposited: 0.51 WETH + 965 USDC ($1,960)
    Range: $1,668 - $2,258 (medium, ±15%)
    Current: $1,963 — IN RANGE ✓
    
  Cost:
    Gas: $32.50 (2 transactions)
    
  Net: Position rebalanced with $2.30 lost to gas
       Now earning ~15-21% APY in fees

  Txs:
    Remove: https://etherscan.io/tx/0x...
    Add:    https://etherscan.io/tx/0x...

  Monitor: "How are my positions doing?" or "Track position #67890"
```

### Position Already In Range

```text
Position #12345 is IN RANGE ✓

  Pool:    WETH/USDC 0.05% (V3, Ethereum)
  Current: $1,963
  Range:   $1,700 - $2,300
  Status:  Actively earning fees

  No rebalance needed. Your position is healthy.
  
  Uncollected fees: $34.80
  Want to collect them? (This doesn't affect your position.)
```

## Important Notes

- **Always confirm before executing.** Rebalancing involves closing and reopening a position — it's irreversible.
- **Gas matters.** On Ethereum mainnet, a full rebalance costs $30-60 in gas. On L2s (Base, Arbitrum), it's < $1. Factor this into recommendations.
- **IL is locked in.** When you close a position, any impermanent loss becomes realized. Mention this if the position has significant IL.
- **New NFT ID.** The rebalanced position gets a new NFT token ID. The old one is burned. Make sure the user understands this.
- **V2 positions cannot be rebalanced** — they have full range. If a user asks to rebalance a V2 position, explain that V2 positions cover the entire price range and don't go "out of range."
- **Slippage on exit.** For large positions relative to pool TVL, exiting may cause slippage. Warn if position is > 5% of pool TVL.

## Error Handling

| Error                          | User-Facing Message                                        | Suggested Action                        |
| ------------------------------ | ---------------------------------------------------------- | --------------------------------------- |
| Position not found             | "Position #{id} not found."                                | Check ID and chain                      |
| Position already in range      | "Position is already in range — no rebalance needed."      | Show position status instead            |
| V2 position                    | "V2 positions cover the full price range and can't go out of range." | Explain V2 vs V3 differences  |
| Wallet not configured          | "No wallet configured for transactions."                   | Set WALLET_TYPE + PRIVATE_KEY           |
| Insufficient gas               | "Not enough ETH for gas."                                  | Fund wallet with ETH                    |
| Safety check failed            | "Safety blocked the rebalance: {reason}"                   | Review safety configuration             |
| Remove tx failed               | "Failed to remove liquidity: {reason}"                     | Check position status and try again     |
| Add tx failed                  | "Removed old position but failed to add new one."          | Tokens are in wallet; retry add manually|
| liquidity-manager unavailable  | "Liquidity agent is not available."                        | Check agent configuration               |
