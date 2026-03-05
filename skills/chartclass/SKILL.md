---
metadata:
  name: ChartClass
  description: Technical analysis and chart pattern recognition for equities, options, and crypto markets
  version: 0.0.2
  tags: [finance, trading, technical-analysis, charting, patterns]
  openclaw:
    requires:
      env: [CHARTCLASS_API_KEY]
    primaryEnv: CHARTCLASS_API_KEY
---

# ChartClass

Technical analysis and chart pattern recognition for financial markets.

## What it does

ChartClass provides AI-powered technical analysis capabilities for equities, options, and crypto, including:

- **Pattern recognition** — identify head-and-shoulders, double tops/bottoms, flags, wedges, cups, and other chart formations
- **Indicator analysis** — moving averages, RSI, MACD, Bollinger Bands, volume profile, and custom indicator combinations
- **Support/resistance** — automatically detect key price levels from historical price action
- **Trend analysis** — classify current trend direction, strength, and potential reversal signals
- **Multi-timeframe** — analyze daily, weekly, and intraday charts with timeframe confluence detection

## Usage

Ask your agent to analyze charts and technical setups:

- "Analyze the daily chart for TSLA and identify the current pattern"
- "What are the key support and resistance levels for SPY?"
- "Screen for stocks forming bullish flag patterns above their 200-day MA"
- "Show RSI divergences on the NVDA 4-hour chart"

## Configuration

Set the following environment variables for market data access:

- `CHARTCLASS_API_KEY` — API key for ChartClass. Used to authenticate requests for OHLCV price data, technical indicator values, and pattern scan results.
- `CHARTCLASS_DEFAULT_TIMEFRAME` — (optional) default chart timeframe, one of: `1m`, `5m`, `15m`, `1h`, `4h`, `daily`, `weekly`. Defaults to `daily`.
