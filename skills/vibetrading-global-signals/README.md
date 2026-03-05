# VibeTrading Global Signals Skill

This OpenClaw skill allows you to query AI-generated trading signals from VibeTrading DataHub.

## Features

- 📡 Query latest signals for multiple symbols
- 🎯 Get signals by specific symbol
- 🔍 Filter by signal type (WHALE_ACTIVITY, NEWS_ANALYSIS, etc.)
- ⏰ Time-based filtering
- 📊 Beautiful console output with sentiment analysis

## Installation

1. Clone or copy this skill to your OpenClaw workspace:
   ```
   ~/.openclaw/workspace/skills/vibetrading-global-signals/
   ```

2. Install dependencies:
   ```bash
   cd ~/.openclaw/workspace/skills/vibetrading-global-signals
   npm install
   ```

**No API token required!** The API is now open and accessible without authentication.

## Usage Examples

### 1. Get Latest Signals
```bash
# Get latest signals for BTC and ETH
node scripts/get_latest_signals.js BTC,ETH

# Get whale and news signals from last 24h
node scripts/get_latest_signals.js BTC,ETH,SOL WHALE_ACTIVITY,NEWS_ANALYSIS 24

# Get multiple signals per type
node scripts/get_latest_signals.js BTC "WHALE_ACTIVITY,NEWS_ANALYSIS" 48 2
```

### 2. Get Signals by Symbol
```bash
# Get all signals for BTC
node scripts/get_signals_by_symbol.js BTC

# Get technical indicators for ETH
node scripts/get_signals_by_symbol.js ETH "TECHNICAL_INDICATOR" 5

# Get signals from last 48 hours
node scripts/get_signals_by_symbol.js SOL "" 10 48
```

### 3. Get Signals by Type
```bash
# Get whale activity signals for BTC
node scripts/get_signals_by_type.js BTC WHALE_ACTIVITY

# Get funding rate signals for ETH
node scripts/get_signals_by_type.js ETH FUNDING_RATE 3

# Get technical indicators from last 72 hours
node scripts/get_signals_by_type.js SOL TECHNICAL_INDICATOR 5 72
```

## Signal Types

| Type | Description |
|------|-------------|
| `WHALE_ACTIVITY` | Whale wallet movement analysis |
| `NEWS_ANALYSIS` | Crypto news sentiment analysis |
| `FUNDING_RATE` | Perpetual funding rate signals |
| `TECHNICAL_INDICATOR` | Multi-timeframe technical analysis |

## Integration with OpenClaw

This skill is designed to work seamlessly with OpenClaw:

1. **No Configuration Needed**: No API token required, works out of the box
2. **Skill Metadata**: Includes proper metadata for OpenClaw's skill system
3. **Tool Integration**: Can be called from OpenClaw tools and cron jobs

## Example OpenClaw Usage

```javascript
// In an OpenClaw session
const { exec } = require('openclaw/tools');

// Check BTC signals
const result = await exec('node scripts/get_latest_signals.js BTC');

// Schedule regular checks
await cron.add({
  schedule: { kind: 'every', everyMs: 3600000 }, // Every hour
  payload: {
    kind: 'agentTurn',
    message: 'Check BTC and ETH signals'
  }
});
```

## Troubleshooting

### Common Issues

1. **404 Not Found**: No signals available for the query
2. **Network Errors**: Check your internet connection
3. **Rate limiting**: API may have rate limits, adjust query frequency

### Debug Mode

```bash
# Test API connectivity
curl 'https://vibetrading.dev/api/v1/signals/latest?symbols=BTC' -v

# Simple ping test
curl -I 'https://vibetrading.dev/api/v1/signals/latest?symbols=BTC'
```

## License

ISC