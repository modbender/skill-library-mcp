---
name: cost-tracker
description: AI spending monitor — track costs across OpenRouter models with daily, weekly, and monthly reports. Budget limits with alerts, per-model analysis, savings recommendations, and historical tracking via SQLite. Use for controlling AI costs and optimizing model selection.
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+, OpenRouter API key
metadata: {"openclaw": {"emoji": "\ud83d\udcb0", "requires": {"env": ["OPENROUTER_API_KEY"]}, "primaryEnv": "OPENROUTER_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# 💰 Cost Tracker

AI spending monitor for OpenRouter. Track per-model costs, get daily/weekly/monthly reports, set budget alerts, and get savings recommendations.

## Usage

```bash
# Fetch and store current usage from OpenRouter
python3 {baseDir}/scripts/cost_tracker.py fetch

# Show spending reports
python3 {baseDir}/scripts/cost_tracker.py report --period daily
python3 {baseDir}/scripts/cost_tracker.py report --period weekly
python3 {baseDir}/scripts/cost_tracker.py report --period monthly

# Per-model breakdown
python3 {baseDir}/scripts/cost_tracker.py models

# Set monthly budget + check status
python3 {baseDir}/scripts/cost_tracker.py budget --set 25.00
python3 {baseDir}/scripts/cost_tracker.py budget --check

# Savings recommendations
python3 {baseDir}/scripts/cost_tracker.py savings

# Export data as JSON
python3 {baseDir}/scripts/cost_tracker.py export --format json
python3 {baseDir}/scripts/cost_tracker.py export --format csv
```

## Features

- **Live Usage Fetch** — Pulls real spending data from OpenRouter's `/api/v1/auth/key` endpoint
- **Per-Model Tracking** — See which models cost you the most
- **Period Reports** — Daily, weekly, monthly summaries with trends
- **Budget Alerts** — Set limits and get warned at 80% threshold
- **Savings Tips** — Identifies cheaper models that could handle the same workload
- **Historical Data** — SQLite storage for long-term trend analysis
- **Export** — JSON or CSV export for spreadsheets

## Data Storage

All data stored in `{baseDir}/data/cost_tracker.db` (SQLite).

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
