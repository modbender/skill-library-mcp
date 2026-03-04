---
name: openclaw-cost-tracker
description: "Track OpenClaw token usage and API costs by parsing session JSONL files. Use when user asks about token spend, API costs, model usage breakdown, daily cost trends, or wants to know how much they're spending on Claude/GPT. Shows per-model breakdown, daily spend chart, and grand totals. No API keys needed — reads directly from local session files."
---

# OpenClaw Cost Tracker

Parse OpenClaw session files to compute per-model token usage, costs, and daily spend trends. Works with any OpenClaw installation — no API keys or external services needed.

## Usage

```bash
# All-time cost report
python3 scripts/cost_tracker.py

# Last 7 days
python3 scripts/cost_tracker.py --days 7

# Today only
python3 scripts/cost_tracker.py --days 1

# Since a specific date
python3 scripts/cost_tracker.py --since 2026-02-01

# JSON output for dashboards/integrations
python3 scripts/cost_tracker.py --days 30 --format json

# Custom agents directory
python3 scripts/cost_tracker.py --agents-dir /path/to/agents
```

## What It Reports

**Per-model breakdown:**
- Total cost, tokens, and request count
- Input/output/cache token split
- Visual percentage bar

**Daily spend:** Bar chart of cost per day (text) or structured array (JSON).

**Grand totals:** Combined cost, tokens, and requests across all models.

## How It Works

1. Auto-discovers the OpenClaw agents directory (`~/.openclaw/agents`)
2. Scans all agent session JSONL files (filtered by mtime for speed)
3. Extracts `message.usage` and `message.model` from each entry
4. Aggregates by model and by day
5. Outputs formatted report or JSON

## JSON Output Schema

```json
{
  "models": [
    {
      "model": "claude-opus-4-6",
      "totalTokens": 220800000,
      "inputTokens": 3200,
      "outputTokens": 390800,
      "cacheReadTokens": 149400000,
      "cacheWriteTokens": 1200000,
      "totalCost": 528.55,
      "requestCount": 2088
    }
  ],
  "daily": [
    { "date": "2026-02-20", "cost": 37.14, "byModel": { "opus-4-6": 35.0, "sonnet-4": 2.14 } }
  ],
  "grandTotal": { "totalCost": 580.11, "totalTokens": 269800000, "totalRequests": 3122 },
  "meta": { "agentsDir": "...", "filesScanned": 65, "entriesParsed": 3122, "range": "7d" }
}
```

## Integration

Feed JSON output into dashboards, alerting, or budgeting tools. The `daily` array is ready for charting. Set up a cron to track spend over time:

```bash
# Daily cost snapshot to file
0 0 * * * python3 /path/to/cost_tracker.py --days 1 --format json >> ~/cost-log.jsonl
```

## Requirements

- Python 3.8+
- OpenClaw installed with session data in `~/.openclaw/agents/`
- No external dependencies (stdlib only)
