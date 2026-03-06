---
name: token-budget-monitor
version: "1.0.0"
description: Track and control token consumption across OpenClaw cron jobs
author: aviclaw
tags:
  - token
  - budget
  - monitor
  - openclaw
---

# token-budget-monitor

Track and control token consumption across OpenClaw cron jobs, fallback chains, and sessions.

## Installation

```bash
openclaw skills install aviclaw/token-budget-monitor
```

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

## Integration

Add to cron jobs to track usage:

```javascript
// After LLM call completes
const usage = result.usage;
exec('node /path/to/track-usage.js track <job-name> ' + 
  usage.input_tokens + ' ' + usage.output_tokens + ' ' + model);
```

## Configuration

Edit `config.json`:

```json
{
  "dailyLimit": 100000,
  "jobLimits": {
    "daily-tweet": 5000,
    "rss-brief": 15000
  },
  "alertThreshold": 0.8,
  "freeModels": [
    "nvidia/moonshotai/kimi-k2.5",
    "google/gemini-2.0-flash-exp"
  ]
}
```

## Features

- Per-job token tracking
- Daily budget limits
- Per-job custom limits
- Alert when threshold exceeded
- Recommend free model alternatives

## Author

- GitHub: @aviclaw

## License

MIT
