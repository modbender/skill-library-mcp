---
name: crypto-market-analyzer
description: Cryptocurrency market analysis for Bitcoin and Ethereum. Fetches 4h (24h) and 1d (30-day) data from Binance API, calculates technical indicators (RSI, SMAs, support/resistance), and provides bullish/bearish sentiment analysis with reasoning. Use when user asks for crypto market reports, BTC/ETH analysis, or daily market summaries.
---

# Crypto Market Analyzer

This skill provides automated cryptocurrency market analysis for Bitcoin (BTC) and Ethereum (ETH).

## What It Does

- Fetches market data from Binance public API (no authentication required)
- Analyzes 4-hour timeframe (last 24 hours)
- Analyzes daily timeframe (last 30 days)
- Calculates technical indicators:
  - RSI (Relative Strength Index, 14-period)
  - Simple Moving Averages (20-day and 50-day)
  - Support and resistance levels
  - Price change (24h and 7d)
- Provides sentiment analysis (Bullish/Bearish/Neutral) with confidence level
- Generates structured reports with reasoning

## Usage

### Generate Market Report

Run the analysis script:

```bash
python3 scripts/fetch_crypto_data.py
```

Output format (JSON):

```json
{
  "BTCUSDT": {
    "indicators": {
      "current_price": 43250.50,
      "sma_20": 42800.00,
      "sma_50": 41500.00,
      "rsi": 58.3,
      "support": 42000.00,
      "resistance": 44000.00,
      "price_change_24h": 2.5,
      "price_change_7d": 5.8
    },
    "sentiment": {
      "sentiment": "Bullish (看涨)",
      "confidence": 0.75,
      "reasons": [
        "RSI (58.3) shows bullish momentum",
        "Price above both SMAs (20d and 50d) - bullish trend",
        "Strong 24h gain (2.50%) - bullish"
      ]
    },
    "timestamp": "2026-02-11T14:38:00"
  },
  "ETHUSDT": { ... }
}
```

### Generate Human-Readable Report

To create a user-friendly report, use the JSON output and format it:

```
📊 加密货币市场分析报告
生成时间: 2026-02-11 14:38

## 比特币 (BTC)

💰 当前价格: $43,250.50
📈 24h涨跌: +2.5%
📊 7日涨跌: +5.8%

### 技术指标
- RSI (14): 58.3
- SMA 20: $42,800
- SMA 50: $41,500
- 支撑位: $42,000
- 阻力位: $44,000

### 市场判断
🎯 趋势: 看涨 (Bullish)
📊 置信度: 75%

📝 分析理由:
- RSI (58.3) 显示多头动能
- 价格位于20日和50日均线上方 - 上升趋势
- 24小时涨幅强劲 (2.50%) - 多头信号

## 以太坊 (ETH)
...
```

## Scheduled Execution

This skill is designed for daily automated execution at 10:00 AM (UTC+8).

To schedule via OpenClaw cron:

```bash
# Create a cron job to run daily at 10:00 AM UTC+8
# This corresponds to 02:00 UTC
```

The cron job should:
1. Execute the analysis script
2. Parse the JSON output
3. Format a human-readable report
4. Send the report to the user via messaging channel

## Technical Details

### Data Source

- **API**: Binance Public API
- **Endpoint**: `/api/v3/klines`
- **Rate Limits**: 1200 request weight per minute (well within limits)
- **No Authentication Required**: Public market data

### Timeframes

- **4h**: 6 candles (24 hours of data)
- **1d**: 30 candles (30 days of data)

### Indicators Explained

- **RSI**: Momentum oscillator (0-100). <30 = oversold, >70 = overbought
- **SMA 20/50**: Trend indicators. Price > both SMAs = bullish
- **Support/Resistance**: Recent low/high averages
- **Price Change**: Percentage change over specified period

### Sentiment Logic

Sentiment is determined by combining multiple signals:

1. RSI position (oversold/overbought/momentum)
2. Price vs moving averages (trend direction)
3. Recent price changes (momentum strength)

Each signal contributes to a bullish/bearish score, which determines:
- Overall sentiment (Bullish/Bearish/Neutral)
- Confidence level (0.3 to 0.9)
- Detailed reasoning

## Extending the Skill

To add more cryptocurrencies:

Edit `scripts/fetch_crypto_data.py` and modify the `symbols` list:

```python
symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "ADAUSDT"]
```

To add more indicators:

Extend the `calculate_technical_indicators()` function with additional calculations (MACD, Bollinger Bands, etc.).

To customize sentiment logic:

Modify the `analyze_sentiment()` function to adjust weighting and thresholds.
