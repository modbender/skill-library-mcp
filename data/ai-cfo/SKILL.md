---
name: AI CFO
description: "Full AI Chief Financial Officer — connects Mercury Banking + Stripe into real-time business intelligence. Daily cash position, automated P&L, revenue tracking, expense categorization, cash flow forecasting, burn rate alerts, and weekly financial reports."
homepage: https://github.com/aiwithabidi/ai-cfo-skill
license: MIT
compatibility: ">=0.9.0"
metadata: {"emoji":"📊","requires":["MERCURY_API_TOKEN","STRIPE_API_KEY","OPENROUTER_API_KEY"],"primaryEnv":"MERCURY_API_TOKEN","homepage":"https://agxntsix.ai"}
---

# 📊 AI CFO

**Full AI Chief Financial Officer for Agent6ix LLC**

Connects Mercury Banking + Stripe into real-time business intelligence. Daily cash position, automated P&L, revenue tracking, expense categorization, cash flow forecasting, burn rate alerts, and weekly financial reports.

## Commands

| Command | Description |
|---------|-------------|
| `dashboard` | Full financial dashboard — balances, MRR, burn rate, runway |
| `transactions` | Recent transactions with AI categorization |
| `pnl` | P&L statement for any date range |
| `cashflow` | Cash flow analysis with 30/60/90 day forecast |
| `revenue` | Stripe revenue breakdown — MRR, new vs recurring, churn |
| `expenses` | Categorized expenses with trends and anomaly detection |
| `report` | Weekly/monthly executive financial report |
| `budget` | Set and track budgets by category |
| `runway` | Burn rate and runway calculation |
| `invoice` | Outstanding Stripe invoices and aging |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `MERCURY_API_TOKEN` | Yes | Mercury Banking API token (read-only) |
| `STRIPE_API_KEY` | Yes | Stripe secret key (restricted, read-only) |
| `OPENROUTER_API_KEY` | Yes | For AI transaction categorization |

## Usage

```bash
python3 scripts/ai_cfo.py dashboard
python3 scripts/ai_cfo.py transactions --days 30
python3 scripts/ai_cfo.py pnl --start 2026-01-01 --end 2026-01-31
python3 scripts/ai_cfo.py cashflow
python3 scripts/ai_cfo.py revenue
python3 scripts/ai_cfo.py expenses --days 30
python3 scripts/ai_cfo.py report --period weekly
python3 scripts/ai_cfo.py budget --set Marketing 5000
python3 scripts/ai_cfo.py runway
python3 scripts/ai_cfo.py invoice
```

## Daily Automation

```bash
# Add to cron for daily 8 AM brief
python3 scripts/cfo_cron.py
```

## Data Storage

All data stored in `.data/sqlite/cfo.db`:
- Categorized transactions
- Budget allocations
- Daily snapshots
- Monthly P&L snapshots

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need an AI CFO for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
