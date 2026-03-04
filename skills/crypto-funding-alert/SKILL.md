---
name: crypto-funding-alert
description: Real-time crypto funding rate scanner with smart alerts. Finds negative funding rates for profitable long positions. Supports Binance futures. No API key needed for scanning.
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["node"] },
        "tags": ["crypto", "trading", "funding-rate", "binance", "futures", "arbitrage", "defi", "scanner", "alert", "monitoring"],
      },
  }
---

# Crypto Funding Rate Alert

Real-time cryptocurrency funding rate scanner that identifies profitable opportunities with negative funding rates on Binance futures markets.

## Features

- **Smart Scanning**: Monitors 40+ major cryptocurrencies for negative funding rates
- **Risk Management**: Built-in safety filters (volume, leverage limits, stop-loss)
- **Scoring System**: Combines funding rate, price trend, and trading volume
- **Signal Classification**: STRONG / MODERATE / WATCH alerts
- **No API Key Required**: Uses public Binance API endpoints
- **Historical Tracking**: Saves scan results to JSONL for analysis

## How It Works

When funding rates are negative, longs receive payments from shorts. This creates a profitable opportunity to:
1. Open a long position
2. Collect funding fees every 8 hours
3. Benefit from potential price appreciation

The scanner filters opportunities by:
- Minimum absolute funding rate (0.05%)
- Minimum 24h volume ($10M)
- Price trend analysis
- Composite scoring algorithm

## Usage

### Basic Scan

```bash
node scan.js
```

### With Custom Config

```bash
node scan.js --max-leverage 2 --min-volume 20000000 --stop-loss 0.15
```

### Automated Monitoring (Cron)

```bash
# Add to OpenClaw cron - scan every 4 hours
openclaw cron add "0 */4 * * *" "cd ~/.openclaw/workspace/skills/crypto-funding-alert && node scan.js"
```

## Configuration

Edit the `SAFE_CONFIG` object in `scan.js`:

```javascript
const SAFE_CONFIG = {
  maxLeverage: 3,          // Maximum leverage (1-5x recommended)
  maxPositionPct: 0.3,     // Max position size (30% of capital)
  stopLossPct: 0.10,       // Stop-loss percentage (10%)
  minVolume: 10000000,     // Minimum 24h volume ($10M)
  minAbsRate: 0.0005,      // Minimum funding rate (0.05%)
  maxCoins: 5,             // Max simultaneous positions
};
```

## Output Example

```
🔍 Safe Funding Rate Monitor | 2026-02-26T06:21:00.000Z
══════════════════════════════════════════════════════════════════════
Safety: 3x max | 10% stop-loss | $10M min volume
══════════════════════════════════════════════════════════════════════

  Signal   Coin     Rate      24h     Vol($M)  Score  Annual(3x)
  ────────────────────────────────────────────────────────────────
  🟢 STRONG   DOGE     -0.0125%    2.34%    145.2    72.3  41%
  🟡 MODERATE SOL      -0.0089%   -1.12%     89.5    48.7  29%
  ⚪ WATCH    XRP      -0.0056%   -2.45%     67.3    35.2  18%

🏆 推荐操作:
   DOGE: 开多 3x | 止损 10% | 费率 -0.0125% | 年化 41%

══════════════════════════════════════════════════════════════════════
📁 历史记录: data/funding-monitor/scan_history.jsonl
```

## Safety Rules

Based on real trading experience:

- **Max Leverage**: 3x (reduces liquidation risk)
- **Position Sizing**: ≤30% per coin (diversification)
- **Stop Loss**: 10% minimum (capital preservation)
- **Volume Filter**: Only liquid markets ($10M+)
- **Trend Check**: Prefer positive 24h momentum
- **No Panic Trading**: Skip during extreme volatility

## Data Storage

Scan results are saved to:
```
~/.openclaw/workspace/data/funding-monitor/scan_history.jsonl
```

Each line contains:
```json
{
  "timestamp": "2026-02-26T06:21:00.000Z",
  "results": [...],
  "config": {...}
}
```

## Command-Line Options

```bash
node scan.js [options]

Options:
  --max-leverage <n>      Maximum leverage (default: 3)
  --min-volume <n>        Minimum 24h volume in USD (default: 10000000)
  --stop-loss <n>         Stop-loss percentage (default: 0.10)
  --min-rate <n>          Minimum absolute funding rate (default: 0.0005)
  --max-coins <n>         Maximum simultaneous positions (default: 5)
  --coins <list>          Comma-separated coin list (default: built-in list)
  --output <path>         Custom output directory
```

## Integration Examples

### Telegram Alert

```bash
node scan.js | grep "🟢 STRONG" && openclaw message send --target @me --message "Strong funding opportunity detected!"
```

### Discord Webhook

```bash
RESULT=$(node scan.js)
curl -X POST $DISCORD_WEBHOOK -H "Content-Type: application/json" -d "{\"content\":\"$RESULT\"}"
```

### Custom Script

```javascript
const { exec } = require('child_process');

exec('node scan.js', (err, stdout) => {
  const lines = stdout.split('\n');
  const strong = lines.filter(l => l.includes('🟢 STRONG'));
  
  if (strong.length > 0) {
    // Your custom logic here
    console.log('Opportunities found:', strong);
  }
});
```

## Disclaimer

This tool is for informational purposes only. Cryptocurrency trading involves substantial risk of loss. Always:
- Do your own research
- Never invest more than you can afford to lose
- Use proper risk management
- Test strategies with small amounts first
- Understand funding rate mechanics before trading

## Requirements

- Node.js 14+
- Internet connection
- No API keys needed for scanning

## Support

For issues or feature requests, visit the ClawHub repository or contact the skill author.

## License

MIT

## Keywords

crypto, trading, funding-rate, binance, futures, arbitrage, defi, scanner, alert, monitoring, negative-funding, long-position, risk-management, automated-trading, cryptocurrency
