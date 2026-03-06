---
name: api-cost-tracker
description: "Track AI API costs across OpenAI, Anthropic, Google AI with budget alerts, analytics, and optimization tips"
metadata:
  clawdbot:
    emoji: 💰
    requires:
      env:
        - OPENAI_API_KEY (optional)
        - ANTHROPIC_API_KEY (optional)
        - GOOGLE_AI_KEY (optional)
---

# API Cost Tracker 💰

Comprehensive AI API cost tracking across multiple providers. Monitor spending, set budgets, get alerts, and optimize your AI costs.

## Features

- ✅ **Multi-Provider Support** - OpenAI, Anthropic, Google AI
- ✅ **Real-Time Tracking** - Monitor costs as they happen
- ✅ **Budget Alerts** - Get notified when approaching limits
- ✅ **Usage Analytics** - Detailed insights into API usage
- ✅ **Cost Optimization** - Tips to reduce spending
- ✅ **Export Reports** - JSON, CSV, Markdown formats
- ✅ **Historical Data** - Track costs over time
- ✅ **Model Comparison** - Compare costs across models

## Installation

```bash
cd api-cost-tracker
npm install
```

## Quick Start

```bash
# Track all providers
node scripts/main.mjs track

# Track specific provider
node scripts/main.mjs track --provider openai

# View analytics
node scripts/main.mjs analytics

# Set budget
node scripts/main.mjs budget set 100 --monthly

# Export report
node scripts/main.mjs export --format markdown --output report.md
```

## Configuration

Edit `config.json`:

```json
{
  "providers": {
    "openai": {
      "enabled": true,
      "apiKey": "${OPENAI_API_KEY}"
    },
    "anthropic": {
      "enabled": true,
      "apiKey": "${ANTHROPIC_API_KEY}"
    },
    "google": {
      "enabled": true,
      "apiKey": "${GOOGLE_AI_KEY}"
    }
  },
  "budgets": {
    "daily": 10,
    "weekly": 50,
    "monthly": 200
  },
  "alerts": {
    "enabled": true,
    "thresholds": [50, 75, 90, 100],
    "webhook": "https://your-webhook.com/alert"
  },
  "tracking": {
    "autoTrack": true,
    "interval": 300000
  }
}
```

## API Reference

### `track(options)`
Track API usage and costs.

**Options:**
- `provider` (string): Specific provider or 'all'
- `period` (string): 'today', 'week', 'month', 'all'

**Returns:**
```json
{
  "total": 45.67,
  "providers": {
    "openai": 32.10,
    "anthropic": 10.50,
    "google": 3.07
  },
  "models": {
    "gpt-4": 28.50,
    "claude-3": 10.50
  }
}
```

### `analytics(period)`
Get detailed analytics.

**Period:** 'day', 'week', 'month', 'year'

**Returns:**
- Cost trends
- Usage patterns
- Model efficiency
- Optimization suggestions

### `budget.set(amount, period)`
Set budget limit.

### `budget.check()`
Check current budget status.

### `export(format, options)`
Export cost report.

**Formats:** 'json', 'csv', 'markdown'

## Usage Examples

### Track Daily Costs
```bash
node scripts/main.mjs track --period today
```

Output:
```
💰 API Costs - Today
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
OpenAI
  GPT-4: $12.50 (125K tokens)
  GPT-3.5: $2.30 (230K tokens)
  Subtotal: $14.80

Anthropic
  Claude-3: $8.20 (82K tokens)
  Subtotal: $8.20

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total: $23.00
Budget: $200/month (11.5% used)
```

### Set Budget Alert
```bash
node scripts/main.mjs budget set 100 --monthly
node scripts/main.mjs alerts enable
```

### Export Monthly Report
```bash
node scripts/main.mjs export --format markdown --period month --output monthly-report.md
```

### Compare Models
```bash
node scripts/main.mjs compare --models gpt-4,claude-3,gemini-pro
```

## Pricing Reference

### OpenAI (per 1K tokens)
- GPT-4: $0.03 (input) / $0.06 (output)
- GPT-4 Turbo: $0.01 / $0.03
- GPT-3.5 Turbo: $0.0005 / $0.0015

### Anthropic (per 1K tokens)
- Claude-3 Opus: $0.015 / $0.075
- Claude-3 Sonnet: $0.003 / $0.015
- Claude-3 Haiku: $0.00025 / $0.00125

### Google AI (per 1K tokens)
- Gemini Pro: $0.00025 / $0.0005
- Gemini Ultra: $0.0025 / $0.0075

## Integration with OpenClaw

Add to your HEARTBEAT.md for automated tracking:

```markdown
Every 6 hours:
- Run: node /path/to/api-cost-tracker/scripts/main.mjs track
- Alert if budget > 75%
```

### Automated Budget Monitoring

```bash
# Add to crontab
0 */6 * * * cd /path/to/api-cost-tracker && node scripts/main.mjs check-budget
```

## Advanced Features

### Cost Optimization Tips

Run optimization analysis:
```bash
node scripts/main.mjs optimize
```

Get suggestions like:
- Switch to GPT-3.5 for simple tasks
- Use Claude-3 Haiku for fast responses
- Batch requests to reduce API calls
- Cache common responses

### Webhook Integration

Configure alerts to send to webhooks:

```json
{
  "webhooks": [
    {
      "url": "https://your-slack-webhook.com",
      "events": ["budget_exceeded", "high_usage"]
    }
  ]
}
```

### Historical Analysis

```bash
# View last 30 days
node scripts/main.mjs history --days 30

# Compare months
node scripts/main.mjs compare --period month --previous
```

## Data Storage

Cost data is stored locally:
```
data/
├── costs/
│   ├── 2026-03-01.json
│   ├── 2026-03-02.json
│   └── ...
├── budgets.json
└── alerts.log
```

## Troubleshooting

### API Key Issues
```bash
# Test API keys
node scripts/main.mjs test-keys
```

### Missing Data
```bash
# Rebuild database
node scripts/main.mjs rebuild
```

## Testing

```bash
npm test
```

## License

MIT - Free for personal and commercial use.

## Support

- GitHub Issues: [your-repo]
- OpenClaw Discord: https://discord.gg/clawd

## Roadmap

- [ ] More providers (Cohere, AI21, etc.)
- [ ] Real-time dashboard
- [ ] Team cost sharing
- [ ] Custom pricing rules
- [ ] Predictive analytics
