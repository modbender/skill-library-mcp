# YieldAgent Superskills

*Modular add-on: advanced capabilities that emerge when YieldAgent combines with agent memory and scheduling.*

> Not investment advice. Superskills are tools for monitoring and managing yield positions. The agent reports data and builds transactions. You make decisions.

---

## Quick Reference

| Category | Superskills |
|----------|-------------|
| **Monitoring** | Rate alerts, trend detection, position health, morning briefing |
| **Discovery** | Cross-chain comparison, new yield alerts, similar yield finder, target rate hunting |
| **Portfolio** | Protocol diversification, network diversification, stable/volatile split, yield type breakdown |
| **Management** | Rotation, exit simulation, rebalance to target, dust cleanup, multi-wallet overview |
| **Rewards** | Harvest timing, batch claiming, accumulation tracking, gas-efficient batching |
| **Scheduling** | Daily check, weekly review, maturity tracking, scheduled entry |
| **Staking** | Validator tracking, performance monitoring, commission alerts |

---

## All 40 Superskills

**Monitoring & Alerts**

1. **Rate Monitoring** — Alert when yield drops below threshold
2. **Rate Trend Detection** — Track direction over multiple checks, spot declining yields early
3. **Position Health Check** — Review all positions with current rates, pending rewards, and exit options
4. **Morning Briefing** — Summary of what moved overnight
5. **Opportunity Cost Alert** — What you're leaving on the table vs best available
6. **New Yield Alerts** — Notified when new opportunities match criteria
7. **Target Rate Hunting** — Watch for yields hitting desired level
8. **Entry Rate Comparison** — Track current rate vs when you entered

**Discovery & Research**

9. **Cross-Chain Comparison** — Same asset, different rates across chains
10. **Similar Yield Finder** — Find alternatives to positions you like
11. **TVL-Based Filtering** — Filter by TVL and liquidity thresholds
12. **APR vs APY Normalization** — Compare rates on equal terms
13. **Yield Type Exploration** — Compare lending vs staking vs vaults vs LPs
14. **Provider Deep Dive** — Research specific protocols across all their yields

**Portfolio Analysis**

15. **Protocol Diversification** — Check concentration by provider
16. **Network Diversification** — Check concentration by chain
17. **Stable vs Volatile Split** — Understand risk allocation
18. **Yield Type Breakdown** — Allocation across lending, staking, vaults, LPs
19. **Concentration Warning** — Flag when one position is too large
20. **Multi-Wallet Overview** — Aggregate positions across all addresses
21. **Position Age Tracking** — How long you've been in each position
22. **Total Earnings Summary** — Lifetime rewards across all positions

**Position Management**

23. **Rotation Workflow** — Exit underperformer, enter better option in one flow
24. **Exit Simulation** — Preview what exiting looks like before committing
25. **Rebalance to Target** — Adjust positions to match target allocation
26. **Dust Cleanup** — Exit tiny positions not worth the gas
27. **Idle Funds Detection** — Find wallet tokens not earning yield (requires wallet skill)
28. **Partial Exit** — Reduce position size without full withdrawal
29. **Position Scaling** — Increase an existing position
30. **Emergency Exit** — Quick withdrawal workflow

**Rewards & Claiming**

31. **Reward Harvesting** — Identify and claim all pending rewards
32. **Harvest Timing** — Wait for lower gas before claiming
33. **Gas-Efficient Batching** — Queue transactions for batch signing (wallet dependent)
34. **Reward Accumulation** — Track historical earnings over time (requires agent memory)
35. **Auto-Compound Check** — Decide whether to restake or withdraw rewards
36. **Claim Threshold** — Only claim when rewards exceed minimum

**Scheduling & Automation**

37. **Scheduled Portfolio Check** — Daily or weekly automated reviews
38. **Maturity Tracking** — Alerts before fixed-term positions expire
39. **Scheduled Entry** — Queue deposits for low-gas periods
40. **Validator Performance** — Monitor staking validator commission and APY changes

---

## How Superskills Work

Superskills combine three capabilities:

```
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  Yield.xyz API  │ + │  Agent State    │ + │   Scheduling    │
│                 │   │                 │   │                 │
│ • Real-time     │   │ • Positions     │   │ • Heartbeats    │
│   yield data    │   │ • Rate history  │   │ • Cron jobs     │
│ • Balances      │   │ • Preferences   │   │ • Periodic      │
│ • Transaction   │   │ • Alerts        │   │   checks        │
│   construction  │   │ • Wallets       │   │ • Timed alerts  │
└─────────────────┘   └─────────────────┘   └─────────────────┘
```

**State File:** `~/.openclaw/skills/yield-agent/state/yield-cache.json`

Single JSON file. Positions keyed by yieldId for O(1) lookup. Rate history capped at 30 days to prevent bloat. Preferences are global defaults with per-position overrides.

```json
{
  "meta": {
    "schemaVersion": 1,
    "lastHeartbeat": "2026-02-10T08:00:00Z",
    "lastFullScan": "2026-02-09T12:00:00Z"
  },

  "wallets": {
    "0x0bbe5ebc254b60a373a4a578ea3a64d2a1e35e3a": {
      "label": "main",
      "type": "crossmint"
    }
  },

  "positions": {
    "base-usdc-aave-v3-lending": {
      "wallet": "0x0bbe5ebc254b60a373a4a578ea3a64d2a1e35e3a",
      "status": "active",
      "enteredAt": "2026-02-01T10:00:00Z",
      "entryRate": 0.042,
      "entryAmount": "1000",
      "lastRate": 0.040,
      "lastChecked": "2026-02-10T08:00:00Z",
      "alertThreshold": 0.03,
      "maturityDate": null,
      "exitAvailableAt": null
    }
  },

  "rateHistory": {
    "base-usdc-aave-v3-lending": [
      { "rate": 0.040, "ts": "2026-02-10" },
      { "rate": 0.041, "ts": "2026-02-09" },
      { "rate": 0.042, "ts": "2026-02-08" }
    ]
  },

  "rewards": {
    "base-usdc-aave-v3-lending": [
      { "amount": "50.00", "ts": "2026-02-01", "txHash": "0x..." }
    ]
  },

  "preferences": {
    "defaults": {
      "minTvl": 50000000,
      "maxConcentration": 0.5,
      "alertOnDropPercent": 0.01,
      "claimThresholdUsd": 10,
      "rateHistoryDays": 30
    }
  },

  "alerts": {
    "rateAlerts": [
      {
        "yieldId": "base-usdc-aave-v3-lending",
        "condition": "below",
        "threshold": 0.03,
        "active": true
      }
    ],
    "targetAlerts": [
      {
        "network": "base",
        "token": "USDC",
        "condition": "above",
        "threshold": 0.08,
        "active": true
      }
    ]
  }
}
```

**Schema notes:**
- `positions[].status`: `active`, `pending_exit`, `deprecated`, `paused`
- `positions[].exitAvailableAt`: set when unstaking cooldown applies
- `positions[].alertThreshold`: per-position override of `preferences.defaults.alertOnDropPercent`
- `rateHistory`: capped at `preferences.defaults.rateHistoryDays` entries per position
- `wallets`: tracks addresses for multi-wallet superskills
- `meta.lastHeartbeat`: used by scheduling superskills to know when checks last ran
```

---

## Trigger Phrases

| User Says | Superskill |
|---------|------------|
| "Alert me if yield drops below 3%" | Rate Monitoring |
| "Where's USDC paying more?" | Cross-Chain Comparison |
| "Check my positions" | Position Health Check |
| "Morning briefing" | Morning Briefing |
| "Claim all my rewards" | Reward Harvesting |
| "Move me out of anything under 4%" | Rotation Workflow |
| "Am I too concentrated?" | Protocol Diversification |
| "Find yields like this one" | Similar Yield Finder |
| "What am I leaving on the table?" | Opportunity Cost Alert |
| "Show dust positions" | Dust Cleanup |
| "Track my yields daily" | Scheduled Portfolio Check |
| "When does my position mature?" | Maturity Tracking |
| "Is my rate trending down?" | Rate Trend Detection |
| "Show my protocol breakdown" | Protocol Diversification |
| "What's my total earned?" | Total Earnings Summary |
| "Simulate exiting Aave" | Exit Simulation |
| "Rebalance to 60/40" | Rebalance to Target |
| "Tell me when USDC hits 6%" | Target Rate Hunting |
| "Is my validator still good?" | Validator Performance |
| "What's not earning yield?" | Idle Funds Detection |
| "How long have I been in Aave?" | Position Age Tracking |
| "Compare my rate to when I entered" | Entry Rate Comparison |

---

## Examples

### Rate Monitoring

User: "Alert me if my Aave yield drops below 3%"

```bash
# 1. Add alert to state file (~/.openclaw/skills/yield-agent/state/yield-cache.json)
#    alerts.rateAlerts += { yieldId, condition: "below", threshold: 0.03, active: true }

# 2. On each heartbeat check:
YIELD=$(./scripts/get-yield-info.sh base-usdc-aave-v3-lending)
CURRENT_RATE=$(echo "$YIELD" | jq '.rewardRate.total')

# 3. Compare against stored threshold, alert if breached
# 4. Update positions[].lastRate and positions[].lastChecked
```

Agent: "Watching base-usdc-aave-v3-lending. Currently at 4.1%. I'll ping you if it drops below 3%."

### Morning Briefing

Agent (8:02 AM):

```
Morning. Here's your yield summary:

Positions:
  Aave Base USDC — 4.1% (stable)
  Morpho Flagship — 5.7% (+0.3% from yesterday)
  Compound — 3.1% (was 3.8%, dropped 3 days in a row)

Alerts:
• Compound is below your 3.5% threshold
• $89 in rewards ready to claim across 3 positions

Recommendations:
• Compound is underperforming — want alternatives?
```

### Rotation Workflow

User: "Move me out of anything under 3.5%"

Agent:

```
Scanning 4 positions...

Found 1 below threshold:
• Compound ETH — 3.1% (threshold: 3.5%)

Best replacement for ETH:
• Lido — 4.8%

Rotation plan:
1. Exit Compound (withdraw 2.5 ETH)
2. Enter Lido (stake 2.5 ETH)

2 transactions. Want to proceed?
```

---

## What Superskills Are NOT

- Not investment advice — agent reports numbers, you decide
- Not automated trading — every transaction needs your approval
- Not predictions — no forecasting, no "this will go up"
- Not risk ratings — TVL and audit status are facts, not recommendations
- Not guaranteed — rates change, protocols have risks
