---
name: vibetrading-global-signals
description: Query AI-generated trading signals from vibetrading-datahub. Signals are produced by autonomous agents analyzing whale activity, news, funding rates, and technical indicators.
metadata:
  {
    "openclaw":
      {
        "emoji": "📡",
        "requires": { "bins": ["curl", "jq"] }
      }
  }
---

# VibeTrading Global Signals

Query AI-generated trading signals from vibetrading-datahub. Signals are produced by autonomous agents analyzing whale activity, news, funding rates, and technical indicators.

## Setup

No authentication required! The API is now open and accessible without any API token.

Simply run the scripts directly:

## API Endpoints

### 1. Get Latest Signals (Multi-Symbol)
Fetch latest signals for multiple symbols, grouped by symbol.

**Example Usage**:
```bash
# Get latest signals for BTC and ETH, all types
curl 'https://vibetrading.dev/api/v1/signals/latest?symbols=BTC,ETH'

# Get only whale and news signals from last 24h
curl 'https://vibetrading.dev/api/v1/signals/latest?symbols=BTC,ETH,SOL&signal_types=WHALE_ACTIVITY,NEWS_ANALYSIS&hours=24'
```

### 2. Get Signals by Symbol
Fetch signals for a single symbol.

**Example Usage**:
```bash
curl 'https://vibetrading.dev/api/v1/signals/BTC?signal_types=TECHNICAL_INDICATOR&limit=5&hours=48'
```

### 3. Get Signals by Symbol and Type
Fetch signals for a specific symbol and signal type combination.

**Example Usage**:
```bash
curl 'https://vibetrading.dev/api/v1/signals/ETH/FUNDING_RATE?limit=3'
```

## Signal Types

| signal_type | Description |
|-------------|-------------|
| `WHALE_ACTIVITY` | Whale wallet movement analysis |
| `NEWS_ANALYSIS` | Crypto news sentiment |
| `FUNDING_RATE` | Perpetual funding rate signals |
| `TECHNICAL_INDICATOR` | Multi-timeframe technical analysis |

## Workflow

### 1. Query Signals
Use the provided scripts to query signals:
- `scripts/get_latest_signals.js` - Get latest signals for multiple symbols
- `scripts/get_signals_by_symbol.js` - Get signals for a specific symbol
- `scripts/get_signals_by_type.js` - Get signals by symbol and type

### 3. Analyze Results
Review the signal payloads for:
- **Sentiment**: BULLISH, BEARISH, or NEUTRAL
- **Analysis**: Detailed markdown analysis
- **Timestamp**: When the analysis was performed

### 4. Schedule Monitoring
Set up cron jobs for regular signal monitoring:
```bash
# Example: Check BTC/ETH signals every hour
0 * * * * /path/to/scripts/get_latest_signals.js BTC,ETH
```

## Scripts
- `scripts/get_latest_signals.js` - Query latest signals for multiple symbols
- `scripts/get_signals_by_symbol.js` - Query signals for a single symbol
- `scripts/get_signals_by_type.js` - Query signals by symbol and type

## Examples

### Quick Signal Check
```bash
# Check BTC signals
node scripts/get_signals_by_symbol.js BTC

# Check latest BTC and ETH signals
node scripts/get_latest_signals.js BTC,ETH

# Check ETH funding rate signals
node scripts/get_signals_by_type.js ETH FUNDING_RATE
```

### Advanced Filtering
```bash
# Get whale activity signals from last 48 hours
node scripts/get_latest_signals.js BTC,ETH,SOL WHALE_ACTIVITY 48

# Get multiple signal types
node scripts/get_latest_signals.js BTC "WHALE_ACTIVITY,NEWS_ANALYSIS" 24
```

## Response Format

All API responses include:
- `symbols`: Array of symbols queried
- `signals`: Object with signals grouped by symbol
- `metadata`: Query metadata (time window, signal types, etc.)

Each signal contains:
- `id`: Unique signal ID
- `symbol`: Trading symbol
- `signal_type`: Type of signal
- `author`: Agent that generated the signal
- `signal_payload`: Detailed analysis with sentiment and markdown
- `created_at`: Timestamp

## Integration with Trading Strategies

Use these signals to:
1. **Confirm trade ideas** with AI-generated analysis
2. **Monitor market sentiment** across multiple dimensions
3. **Set alerts** for specific signal types
4. **Combine with other data** for comprehensive analysis

## Troubleshooting

**Common Issues**:
1. **404 Not Found**: No signals available for the query parameters
2. **Rate limiting**: API may have rate limits, adjust query frequency
3. **Network issues**: Check your internet connection

**Debug Commands**:
```bash
# Test API connectivity
curl 'https://vibetrading.dev/api/v1/signals/latest?symbols=BTC' -v

# Simple ping test
curl -I 'https://vibetrading.dev/api/v1/signals/latest?symbols=BTC'
```

## Notes
- API responses are cached for performance
- Signal timestamps are in UTC
- Always verify signals with other data sources
- Use appropriate risk management with any trading decisions