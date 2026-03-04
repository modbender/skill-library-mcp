# Token Budget Monitor

Track and control token consumption across OpenClaw cron jobs, fallback chains, and sessions.

## Features

- **Per-job tracking** — log tokens per cron job execution
- **Budget limits** — set max tokens per job/day
- **Auto-fallback** — switch to cheaper models when over budget  
- **Alerts** — warn before hitting limits
- **Model recommendations** — suggest free alternatives

## Usage

```bash
# Check current usage
node track-usage.js status

# Check budget for a specific job
node track-usage.js check daily-tweet

# Alert if over budget
node track-usage.js alert

# Get model recommendations
node track-usage.js recommend
```

## Configuration

Create `config.json` in skill directory:

```json
{
  "dailyLimit": 100000,
  "jobLimits": {
    "daily-tweet": 5000,
    "rss-brief": 10000,
    "daily-openclaw-search": 15000
  },
  "alertThreshold": 0.8,
  "freeModels": [
    "nvidia/moonshotai/kimi-k2.5",
    "google/gemini-2.0-flash-exp"
  ]
}
```

## Output

Logs written to `~/.openclaw/workspace/outputs/token-usage.json`:

```json
{
  "date": "2026-02-22",
  "totalTokens": 45000,
  "jobs": {
    "daily-tweet": { "input": 1000, "output": 500 },
    "rss-brief": { "input": 8000, "output": 2000 }
  }
}
```
