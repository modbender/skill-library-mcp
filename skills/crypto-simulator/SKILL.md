---
name: crypto-simulator
description: Backtest crypto trading strategies (RSI, DCA, MACD, Grid, etc.)
  against real CoinGecko data.
---


# Crypto Simulator

Backtest and simulate cryptocurrency trading strategies using real market data.

## Quick Start

```bash
cd {skill_dir}
npm install && npm run build

# Backtest a strategy
node dist/cli.js backtest --coin bitcoin --strategy rsi_swing --days 90

# Compare all strategies
node dist/cli.js compare --coin ethereum --days 180

# Optimize parameters
node dist/cli.js optimize --coin bitcoin --strategy rsi_swing

# Start REST API
node dist/cli.js serve --port 3002
```

## Strategies

| Strategy | Best For | Logic |
|----------|----------|-------|
| RSI Swing | Volatile markets | Buy RSI < 30, sell RSI > 70 |
| DCA | Long-term | Fixed-interval buys |
| MA Cross | Trending | Buy/sell on MA crossovers |
| Grid | Ranging | Orders at price grid levels |
| HODL | Bull markets | Buy-and-hold baseline |
| Bollinger Bands | Mean reversion | Trade on band breakouts |
| MACD | Momentum | Signal line crossovers |
| Mean Reversion | Ranging | Buy below mean, sell above |

**Supported coins**: BTC, ETH, SOL, DOGE, ADA, DOT, AVAX, LINK, MATIC, XRP

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/prices/:coinId` | Current & historical prices |
| `POST` | `/api/backtest` | Run backtest |
| `GET` | `/api/compare/:coinId` | Compare all strategies |
| `POST` | `/api/optimize` | Find optimal parameters |

## Edge Cases

- **CoinGecko rate limits**: Free tier = ~10-30 req/min. SQLite cache avoids redundant calls
- **Insufficient data**: Short timeframes may lack enough data for indicators (e.g., 50-day MA needs 50+ days)
- **Slippage**: Backtests assume perfect execution — real results will differ

## ⚠️ Disclaimer

**For educational/informational purposes only.** Not financial advice. Past performance ≠ future results.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 3002 | API server port |
| `CACHE_DIR` | `./data` | SQLite cache directory |

## Requirements

- Node.js 18+
- Internet connection (CoinGecko API)
- No API keys needed (free tier)
