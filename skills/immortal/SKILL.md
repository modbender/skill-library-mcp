---
name: Named Immortal
description: >
  Empowers AI agents with crypto resource vitality assessment. Calls the
  Majestify API (crypto-health-hub) to compute Sharpe, Sortino, VaR, CVaR,
  drawdown, and other risk metrics, then classifies assets as IMMORTAL,
  MORTAL, or CRITICAL. Zero local dependencies — works anywhere with
  internet access.
license: MIT
compatibility:
  os: [windows, macos, linux]
  python: ">=3.10"
metadata:
  openclaw:
    emoji: 🛡️
    version: 1.0.0
    tags:
      - crypto-risk
      - resource-management
      - vitality-assessment
      - agent-intelligence
      - majestify
    requires:
      bins: []
      packages: []          # httpx is optional; falls back to stdlib
---

# Named Immortal: Agent Resource Intelligence

> *"To survive the infinite game, one must understand not just price, but Vitality — the mathematical probability of survival."*

## What This Skill Does

This skill gives agents the ability to **assess the financial health of crypto assets** by calling the live [Majestify](https://majestify.io) API. It calculates institutional-grade risk metrics and classifies each asset into one of three vitality tiers:

| Tier | Criteria | Agent Recommendation |
|:---|:---|:---|
| 🛡️ **IMMORTAL** | Sharpe > 1.2, Drawdown < 60% | Treasury / Long-term hold |
| ⚠️ **MORTAL** | Moderate risk profile | Active management / Growth |
| ☠️ **CRITICAL** | Drawdown > 80% or Sharpe < -1.0 | Avoid / Hedge |

## Metrics Computed

All metrics are powered by the Crypto Health Hub backend (`services.py`):

- **Sharpe Ratio** — Risk-adjusted return vs. risk-free rate
- **Sortino Ratio** — Downside-only risk adjustment
- **VaR / CVaR (95%)** — Worst-case loss scenarios
- **Cornish-Fisher VaR** — Skewness/kurtosis-adjusted VaR
- **Max Drawdown** — Largest peak-to-trough decline
- **Annualized Return** — CAGR over the window
- **Skewness / Kurtosis** — Distribution shape

## Usage

### Basic (default: BTC + ETH, 365-day window)
```bash
python .agent/skills/immortal/scripts/assess_vitality.py
```

### Custom assets
```bash
python .agent/skills/immortal/scripts/assess_vitality.py --coins bitcoin ethereum solana
```

### Custom API endpoint
```bash
python .agent/skills/immortal/scripts/assess_vitality.py --api https://crypto-health-hub.onrender.com
```

### Custom time window
```bash
python .agent/skills/immortal/scripts/assess_vitality.py --coins bitcoin --days 90
```

## Output

**Human-readable** output goes to `stdout`. **Machine-readable JSON** is emitted to `stderr` for agent piping:

```bash
# Agent can capture JSON like this:
python assess_vitality.py --coins bitcoin 2>results.json
```

## Dependencies

- **Python 3.10+** (uses `match`-free syntax, compatible with 3.10)
- **httpx** (optional) — if installed, used for async HTTP. Falls back to `urllib` from stdlib.
- **Internet access** to the Majestify API (`crypto-health-hub.onrender.com`)

## Related Skills

- [immortal-api](file:///.agent/skills/immortal-api/SKILL.md) — Full compute-budget survival API with ledger, optimizer, policy engine, and circuit breakers.
- [financial_analysis](file:///.agent/skills/financial_analysis/SKILL.md) — Coding standards and metric comparison guidelines.
