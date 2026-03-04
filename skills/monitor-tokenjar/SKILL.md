---
name: monitor-tokenjar
description: >-
  Monitor the Uniswap TokenJar with a real-time dashboard showing balances,
  accumulation rates, burn economics, and projected time to next profitable burn.
  Supports one-shot snapshot and streaming modes. Use when user asks "Watch the
  TokenJar", "Track fee accumulation", or "When is the next profitable burn?"
model: opus
allowed-tools:
  - Task(subagent_type:protocol-fee-seeker)
  - mcp__uniswap__get_tokenjar_balances
  - mcp__uniswap__get_firepit_state
  - mcp__uniswap__get_fee_accumulation_rate
  - mcp__uniswap__subscribe_tokenjar
  - mcp__uniswap__get_burn_history
  - mcp__uniswap__get_token_price
---

# Monitor TokenJar

## Overview

A monitoring dashboard for Uniswap's protocol fee system. The TokenJar accumulates fees from all Uniswap sources (V2, V3, V4, UniswapX, Unichain native fees). This skill provides a comprehensive view of what's in the jar, how fast it's growing, and when the next burn will be profitable -- the single most actionable question for protocol fee seekers.

Two modes: **one-shot** (instant snapshot with analytics) and **streaming** (real-time deposit tracking with live updates).

**Why this is 10x better than calling tools individually:**

1. **Actionable projection**: The key output is "estimated time to next profitable burn" -- a compound calculation that requires TokenJar balances, UNI price, gas estimates, and accumulation rates. No single tool provides this. Manually computing it requires calling 4-5 tools and doing the math yourself.
2. **Compound dashboard**: Instead of raw JSON from separate tools, you get a single formatted view combining balances, rates, burn economics, and history. The agent cross-references all data sources to produce insights none of them provide alone.
3. **Streaming mode with context**: Raw `subscribe_tokenjar` returns deposit events without context. This skill enriches each deposit with a running total, updated profitability estimate, and alert when the threshold is crossed -- turning raw events into actionable intelligence.
4. **Historical context**: The dashboard includes recent burn history and competitive intelligence, so you understand not just the current state but the dynamics of the system.

## When to Use

Activate when the user says anything like:

- "Watch the TokenJar"
- "Monitor protocol fees"
- "Track fee accumulation"
- "When is the next profitable burn?"
- "Show me TokenJar analytics"
- "How fast are fees accumulating?"
- "Alert me when a burn is profitable"
- "TokenJar dashboard"
- "What's the accumulation rate?"

**Do NOT use** when the user wants to execute a burn (use `seek-protocol-fees` instead) or wants deep historical analysis of burn economics (use `analyze-burn-economics` instead).

## Parameters

| Parameter           | Required | Default  | How to Extract                                                      |
| ------------------- | -------- | -------- | ------------------------------------------------------------------- |
| chain               | No       | ethereum | Always Ethereum mainnet for TokenJar                                |
| streaming           | No       | false    | "watch", "stream", "live", "real-time" implies true                 |
| duration            | No       | 60       | Streaming duration in seconds (1-300). "Watch for 5 minutes" = 300  |
| alert-threshold-usd | No       | --       | "Alert me when jar hits $50K" extracts 50000                        |
| include-history     | No       | true     | "Skip history" or "just current state" implies false                |

## Workflow

### One-Shot Mode (default)

1. **Parallel data collection**: Make all MCP calls simultaneously for speed:
   - `mcp__uniswap__get_tokenjar_balances` -- current jar contents
   - `mcp__uniswap__get_firepit_state` -- threshold, nonce, readiness
   - `mcp__uniswap__get_fee_accumulation_rate` -- daily/weekly/monthly rates
   - `mcp__uniswap__get_burn_history` (if `include-history: true`) -- recent burns

2. **Compound analysis**: Delegate to `Task(subagent_type:protocol-fee-seeker)` in monitoring mode:

   ```
   Produce a TokenJar monitoring dashboard.

   Current data:
   - TokenJar balances: {from parallel calls}
   - Firepit state: threshold={threshold}, nonce={nonce}
   - Accumulation rates: {from parallel calls}
   - Recent burn history: {from parallel calls}

   Tasks:
   1. Price all TokenJar assets in USD using get_token_price.
   2. Calculate total jar value.
   3. Calculate current burn cost (threshold UNI * UNI price + gas estimate).
   4. Determine current profitability: jar value vs. burn cost.
   5. Using accumulation rates, project when the next burn will be profitable
      (if not already) or when ROI will exceed 10% (if already profitable).
   6. Summarize recent burn history: last burn date, frequency, average profit.
   7. Identify the top fee-generating tokens and any notable trends.

   Return a structured dashboard report.
   ```

3. **Format and present**: Display the dashboard with all sections.

### Streaming Mode

1. **Initial snapshot**: Run the same one-shot workflow above to establish a baseline.

2. **Start streaming**: Call `mcp__uniswap__subscribe_tokenjar` with the user's duration:
   - If `alert-threshold-usd` is set, include `minDepositUsd` filter.
   - Default duration: 60 seconds.

3. **Enrich deposits**: For each deposit event received:
   - Price the deposited token in USD.
   - Update the running jar total.
   - Recalculate profitability with the new total.
   - If the jar value crosses the burn cost threshold, alert: "Burn is now profitable!"

4. **Final summary**: After streaming ends, present an updated dashboard with:
   - Deposits observed during the session.
   - Updated jar total.
   - Updated profitability estimate.

## Output Format

### One-Shot Dashboard

```text
TokenJar Dashboard (Ethereum)

  ══════════════════════════════════════
  CURRENT BALANCES
  ══════════════════════════════════════
  Token     Balance       USD Value    Share
  WETH      7.20          $18,000      34.6%
  USDC      15,000        $15,000      28.8%
  USDT      8,500         $8,500       16.3%
  WBTC      0.08          $6,400       12.3%
  DAI       4,100         $4,100       7.9%
  ──────────────────────────────────────
  Total                   $52,000      100%

  ══════════════════════════════════════
  ACCUMULATION RATES
  ══════════════════════════════════════
  Daily:    ~$7,400/day
  Weekly:   ~$51,800/week
  Monthly:  ~$222,000/month

  Top Contributors:
    WETH     ~$2,800/day  (37.8%)
    USDC     ~$2,100/day  (28.4%)
    USDT     ~$1,200/day  (16.2%)

  ══════════════════════════════════════
  BURN ECONOMICS
  ══════════════════════════════════════
  Burn Threshold:  4,000 UNI ($28,000)
  Gas Estimate:    ~$45
  Total Burn Cost: $28,045

  Current Jar:     $52,000
  Net Profit:      $23,955
  ROI:             85.4%
  Status:          PROFITABLE

  ══════════════════════════════════════
  RECENT HISTORY
  ══════════════════════════════════════
  Last Burn:       2026-02-03 (7 days ago)
  Burn Frequency:  ~every 5.2 days (avg last 10 burns)
  Avg Profit:      $18,400 per burn
  Nonce:           42

  ══════════════════════════════════════
  PROJECTION
  ══════════════════════════════════════
  Next 10% ROI:    Already exceeded (current: 85.4%)
  Next 100% ROI:   ~0.5 days at current rate
  Competitor Risk:  HIGH — avg burn interval is 5.2 days, currently at 7 days
```

### Streaming Output

```text
TokenJar Live Feed (streaming for 60s)

  Baseline: $52,000 across 5 assets

  [14:00:12] Deposit: 0.15 WETH ($375)  | Running Total: $52,375
  [14:00:28] Deposit: 500 USDC ($500)    | Running Total: $52,875
  [14:00:45] Deposit: 200 USDT ($200)    | Running Total: $53,075

  ──────────────────────────────────────
  Session Summary (60s)
  ──────────────────────────────────────
  Deposits:     3 events, $1,075 total
  Rate:         ~$64,500/hour (this session)
  Updated Total: $53,075
  Profitability: $25,030 net profit (89.3% ROI)
  Status:        PROFITABLE — ready to burn
```

### Alert Output (when threshold crossed)

```text
  ALERT: TokenJar value ($50,125) has crossed your alert threshold ($50,000).
  Current profitability: $22,080 net profit (78.7% ROI).
  Consider running: seek-protocol-fees
```

## Important Notes

- **Read-only skill.** This skill never executes transactions. It only reads data and produces analysis. To execute a burn, use `seek-protocol-fees`.
- **Ethereum mainnet only.** The TokenJar and Firepit are mainnet contracts.
- **Accumulation rates are estimates.** They are based on historical Transfer events over a lookback window (default ~7 days). Actual rates vary with protocol volume and fee settings.
- **Streaming duration is capped at 300 seconds** (5 minutes) by the MCP tool. For longer monitoring, re-run the skill periodically.
- **Competitor intelligence is approximate.** Burn frequency is derived from on-chain history, not mempool monitoring. Another searcher could burn at any time.
- **UNI price volatility affects projections.** The "time to profitable burn" projection assumes stable UNI price. A UNI price spike could make a currently-profitable burn unprofitable.

## Error Handling

| Error                        | User-Facing Message                                                    | Suggested Action                          |
| ---------------------------- | ---------------------------------------------------------------------- | ----------------------------------------- |
| TokenJar empty               | "TokenJar is empty. No fees have accumulated yet."                     | Wait for protocol activity                |
| No accumulation data         | "Insufficient data to calculate accumulation rates."                   | Try a larger lookback window              |
| No burn history              | "No burn history found. This may be a new deployment."                 | Set include-history: false                |
| Streaming timeout            | "Streaming session ended after {duration}s."                           | Re-run for another session                |
| No deposits during stream    | "No deposits observed during the {duration}s streaming window."        | Try a longer duration or check later      |
| Token price unavailable      | "Could not price {token}. Dashboard values may be incomplete."         | Token may be exotic or illiquid           |
| RPC connection failed        | "Cannot connect to Ethereum RPC. Dashboard unavailable."               | Check RPC configuration                   |
