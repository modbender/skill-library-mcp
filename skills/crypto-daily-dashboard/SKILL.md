---
name: crypto-daily-dashboard
description: All-in-one crypto dashboard showing Binance portfolio, BTC/ETH/SOL prices, Fear & Greed index, top funding rates, and economic tracking. Beautiful terminal UI. Configurable via environment variables.
metadata:
  {
    "openclaw": {
      "requires": { "bins": ["node"] }
    }
  }
---

# Crypto Daily Dashboard

A comprehensive cryptocurrency financial dashboard that displays:

- 📊 Binance account balances (spot, futures, total, unrealized PnL)
- 📈 Major crypto prices (BTC, ETH, SOL) with 24h change
- 🎭 Fear & Greed Index (market sentiment)
- 💸 Top funding rates (negative rates = earn by going long)
- 🏦 Economic tracking (balance, runway, income/expenses)

## Features

- **Beautiful terminal UI** with box-drawing characters and emojis
- **Zero dependencies** - uses only Node.js built-ins
- **Graceful fallbacks** - works even without API keys (shows prices & sentiment)
- **Multi-source data** - CoinGecko → Binance fallback for reliability
- **Configurable** - all sensitive data via environment variables

## Installation

No installation needed - just configure and run!

## Configuration

### Required (for Binance balance)

```bash
export BINANCE_API_KEY="your_api_key"
export BINANCE_API_SECRET="your_api_secret"
```

### Optional

The dashboard works without API keys - it will show crypto prices and market sentiment using public APIs.

## Usage

### Basic

```bash
node dashboard.js
```

### From OpenClaw

```bash
exec node ~/.openclaw/workspace/skills/crypto-daily-dashboard/dashboard.js
```

### As a cron job

Add to your OpenClaw cron:

```bash
openclaw cron add "0 9 * * *" "node ~/.openclaw/workspace/skills/crypto-daily-dashboard/dashboard.js" --label "daily-crypto-dashboard"
```

## Output Example

```
╔══════════════════════════════════════════════╗
║       💰 每日财务仪表盘 | 2026-02-26 09:00   ║
╚══════════════════════════════════════════════╝

📊 Binance 账户
────────────────────────────────────────
  现货: $1,234.56
  合约: $5,678.90
  总计: $6,913.46 USDT
  未实现盈亏: $123.45

📈 主要加密货币
────────────────────────────────────────
  bitcoin     $   65432.10  +2.3%
  ethereum    $    3456.78  -1.2%
  solana      $     123.45  +5.6%

🎭 市场情绪
────────────────────────────────────────
  😊 Greed: 67/100

💸 Funding Rate (负费率=做多赚钱)
────────────────────────────────────────
  BTC      -0.0123%  年化(3x): 13%
  ETH      -0.0089%  年化(3x): 9%

🏦 经济状态
────────────────────────────────────────
  🟢 状态: THRIVING
  💰 余额: $10,000.00
  📈 总收入: $15,000.00
  📉 总支出: $5,000.00
  ⏳ 跑道: 365 天

══════════════════════════════════════════════
💡 记住：不赚钱拔网线 | 安全第一 | 复利增长
══════════════════════════════════════════════
```

## Data Sources

- **Binance API** - account balances and funding rates
- **CoinGecko API** - crypto prices (free tier, no key needed)
- **Binance Public API** - fallback for prices
- **Alternative.me API** - Fear & Greed Index (free, no key needed)

## Security

- No hardcoded credentials
- API keys via environment variables only
- Read-only API permissions recommended
- No data sent to third parties

## Troubleshooting

### "无法获取" (Cannot fetch)

- Check your internet connection
- Verify Binance API keys are set correctly
- Ensure API keys have read permissions

### Rate limiting

The script uses multiple data sources with fallbacks. If one source is rate-limited, it automatically tries alternatives.

## License

MIT

## Author

Created for OpenClaw agent ecosystem
