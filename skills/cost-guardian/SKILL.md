---
name: cost-guardian — AI & Infrastructure Cost Tracker
description: Track, analyze, and optimize the total cost of running your AI
  agent and infrastructure. Budget alerts, spend forecasts, and concrete
  optimization recommendations.
---

# cost-guardian — AI & Infrastructure Cost Tracker

Track, analyze, and optimize the total cost of running your AI agent and infrastructure. Budget alerts, spend forecasts, and concrete optimization recommendations.

## Commands

### Initialize
```bash
python scripts/cost-guardian.py init
```
Creates config and database in `~/.openclaw/workspace/costs/`.

### Track a Cost Entry
```bash
# Track API spend
python scripts/cost-guardian.py track --provider openai --amount 12.50 --currency USD --period monthly --category api

# Track infrastructure cost
python scripts/cost-guardian.py track --provider hetzner --amount 5.00 --currency EUR --period monthly --category hosting

# Track one-time cost
python scripts/cost-guardian.py track --provider cloudflare --amount 10.00 --currency USD --period once --category domain

# Track electricity
python scripts/cost-guardian.py track --provider electricity --amount 15.00 --currency EUR --period monthly --category power
```

### Scan Token Usage from Gateway Logs
```bash
# Scan recent gateway logs for token consumption per model
python scripts/cost-guardian.py scan-tokens

# Scan specific days
python scripts/cost-guardian.py scan-tokens --days 7
```

### Set Budget
```bash
# Monthly budget
python scripts/cost-guardian.py budget --monthly 50.00 --currency EUR

# Budget with alert threshold (alert at 80%)
python scripts/cost-guardian.py budget --monthly 50.00 --alert-pct 80
```

### Cost Report
```bash
# Current month report
python scripts/cost-guardian.py report

# Weekly report
python scripts/cost-guardian.py report --period week

# JSON output
python scripts/cost-guardian.py report --json

# Specific month
python scripts/cost-guardian.py report --month 2026-02
```

### Optimization Recommendations
```bash
# Get optimization suggestions
python scripts/cost-guardian.py optimize

# JSON output
python scripts/cost-guardian.py optimize --json
```

### Forecast Spend
```bash
# Forecast next 3 months
python scripts/cost-guardian.py forecast

# Forecast next N months
python scripts/cost-guardian.py forecast --months 6

# JSON output
python scripts/cost-guardian.py forecast --json
```

### Manage Subscriptions
```bash
# Add a subscription
python scripts/cost-guardian.py sub add --name "OpenRouter" --amount 20.00 --currency USD --cycle monthly --renews 2026-03-15 --category api

# List subscriptions
python scripts/cost-guardian.py sub list

# Remove a subscription
python scripts/cost-guardian.py sub remove --name "OpenRouter"

# Check upcoming renewals
python scripts/cost-guardian.py sub upcoming --days 14
```

### Status Dashboard
```bash
# Quick status overview
python scripts/cost-guardian.py status

# JSON output  
python scripts/cost-guardian.py status --json
```

## Categories

- `api` — AI model API costs (OpenAI, Anthropic, OpenRouter, etc.)
- `hosting` — VPS, cloud, domain, DNS
- `power` — Electricity for homelab
- `subscription` — SaaS subscriptions
- `hardware` — One-time hardware purchases
- `other` — Everything else

## Output Modes

All commands support:
- **Human-readable** (default) — colored terminal output
- **JSON** (`--json`) — structured data for programmatic use

## Cron Integration

Add to OpenClaw cron for automated cost tracking:
- Daily: `scan-tokens` to track API usage
- Weekly: `report --period week` for digest
- Monthly: `report` + `forecast` for full analysis
- On-demand: `optimize` when looking to cut costs

## Data Storage

All data stored in `~/.openclaw/workspace/costs/`:
- `config.json` — budget settings, preferences
- `costs.db` — SQLite database (entries, subscriptions, token scans)

## Zero Dependencies

Pure Python 3 stdlib — no pip install needed. Uses sqlite3, json, datetime, pathlib.
