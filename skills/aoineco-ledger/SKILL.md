# Aoineco Ledger — AI Agent Financial Tracking Engine

<!-- 🌌 Aoineco-Verified | S-DNA: AOI-2026-0213-SDNA-AL01 -->

**Version:** 1.0.0  
**Author:** Aoineco & Co.  
**License:** MIT  
**Tags:** finance, expense-tracking, budget, roi, bootstrap, multi-agent, accounting

## Description

Financial tracking engine built for AI agents operating on extreme budgets. Tracks every API call, gas fee, and revenue stream with per-agent cost attribution. Native support for the $7 Bootstrap Protocol.

Rebuilt from `agentledger` (Node.js) into Python with major enhancements for multi-agent squads and micro-budget operations.

**Core metric:** *Intelligence per Dollar (IPD) — how many operations you get per cent spent.*

## Problem

AI agents spend money (API calls, gas fees, subscriptions) but rarely track it. When you're running a 9-agent squad on a $7 seed budget, every fraction of a cent matters. You need:
- Real-time visibility into burn rate and runway
- Per-agent cost attribution (who's spending what?)
- Budget alerts BEFORE you overspend
- Revenue tracking to measure actual ROI

## Features

| Feature | Description |
|---------|-------------|
| **Transaction Logging** | Log expenses, revenue, API costs, gas fees with one-liner methods |
| **$7 Bootstrap Metrics** | Seed tracking, ROI%, runway days, daily burn rate, IPD |
| **Per-Agent Cost Attribution** | Track spending by squad member (oracle, blue-sound, etc.) |
| **Budget Alerts** | Set limits per category/period — warns at 80%, blocks at 100% |
| **Category System** | Pre-configured for AI ops: API/LLM, Gas/Blockchain, Revenue/Gig, etc. |
| **CSV/JSON Export** | Full transaction export for tax, audit, or analysis |
| **JSONL Storage** | Append-only transaction log — fast, corruption-resistant |
| **Period Filtering** | Query by today, this-week, this-month, this-year, or all |

## Quick Start

```python
from ledger_engine import AoinecoLedger

ledger = AoinecoLedger()

# Log API cost
ledger.log_api_cost(0.0042, "Google", "gemini-3-flash", tokens_used=150000, agent="oracle")

# Log gas fee
ledger.log_gas(0.0003, chain="base", tx_hash="0xabc123", agent="blue-sound")

# Log revenue
ledger.log_revenue(0.01, "MoltLaunch", "Tier-1 Intel Report", category="Revenue/Gig")

# Set budget
ledger.set_budget("API/LLM", limit=3.00, period="daily")

# Check $7 Bootstrap metrics
metrics = ledger.get_bootstrap_metrics()
# → Seed: $7.00, Burn: $0.02/day, Runway: 300 days, IPD: 257.5 ops/$
```

## Bootstrap Metrics Output

```
💰 Seed Amount: $7.00
📈 Total Revenue: $0.0150
📉 Total Expenses: $0.0233
🤖 API/LLM Cost: $0.0230
💵 Net Profit: $-0.0083
📊 ROI: -0.1%
💎 Remaining Balance: $6.9917
🔥 Daily Burn Rate: $0.0233/day
⏱️ Runway: 300 days
🧠 IPD: 257.5 ops/$
```

## Pre-Configured Categories

- `API/LLM` — OpenAI, Anthropic, Google API costs
- `Gas/Blockchain` — On-chain transaction fees
- `Revenue/Gig` — MoltLaunch gig income
- `Revenue/DeFi` — Meteora, LP yields
- `Revenue/Music` — claw.fm royalties
- `Infrastructure`, `Marketing`, `Tools`, `Subscriptions`, `Other`

## File Structure

```
aoineco-ledger/
├── SKILL.md              # This file
└── scripts/
    └── ledger_engine.py  # Main engine (zero external dependencies)
```

## Zero Dependencies

Pure Python 3.10+. No pip install needed.
Designed for the $7 Bootstrap Protocol — every byte counts.
