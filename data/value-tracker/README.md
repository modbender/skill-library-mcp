# 💰 Value Tracker

**Quantify the ROI of your AI assistant.**

Track hours saved with differentiated rates by category. Strategy work pays more than ops work — this skill reflects that.

## Features

- ✅ **Category-based rates** — Strategy ($150/hr) vs Ops ($50/hr)
- ✅ **Auto-detection** — Automatically categorize tasks by keywords
- ✅ **Multiple views** — Today, week, month, all-time summaries
- ✅ **Markdown reports** — Export beautiful reports
- ✅ **JSON export** — Feed into dashboards

## Quick Start

```bash
# Log a task (auto-detect category)
./tracker.py log auto "Researched competitor pricing" -H 1.5

# Or specify category
./tracker.py log tech "Set up API integration" -H 2

# View this week's value
./tracker.py summary week

# Generate report
./tracker.py report month
```

## Categories & Rates

| Category | Rate | Examples |
|----------|------|----------|
| 🎯 strategy | $150/hr | Planning, decisions, roadmaps |
| 🔍 research | $100/hr | Analysis, market research |
| 💹 finance | $100/hr | Forecasting, budgets |
| ⚙️ tech | $85/hr | Integrations, automations |
| 📈 sales | $75/hr | CRM, pipeline, outreach |
| 📣 marketing | $65/hr | Content, campaigns |
| 🔧 ops | $50/hr | Email, scheduling, admin |

Edit `config.json` to customize rates.

## Why This Matters

AI assistants save time. But "it helps me" isn't a business case.

**"My AI saved 47 hours this month worth $4,200"** — that's a business case.

## Author

Built by [@Rostoll](https://x.com/Rostoll) for the [Clawdbot](https://clawd.bot) community.

## License

MIT — use it, improve it, share it.
