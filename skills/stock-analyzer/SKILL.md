---
name: stock-analyzer
description: Analyze Japanese and US stocks, track portfolios, and summarize financial news using Yahoo Finance data. Use when: (1) Fetching stock prices and indicators, (2) Analyzing portfolio performance, (3) Summarizing quarterly earnings reports, (4) Calculating technical analysis indicators.
---

# Stock Analyzer

## Overview

Comprehensive stock analysis and portfolio tracking tool for Japanese and US markets. Integrates with Yahoo Finance for real-time data collection, technical indicator calculation, and news summarization.

## Quick Start

```bash
# Fetch stock data (Japan)
python3 scripts/fetch_yahoo.py --symbol 7203.T --market japan

# Fetch stock data (US)
python3 scripts/fetch_yahoo.py --symbol AAPL --market us

# Analyze portfolio
python3 scripts/analyze.py --portfolio data/portfolio.json

# Calculate technical indicators
python3 scripts/analyze.py --symbol 7203.T --indicators macd,rsi,bollinger
```

## Core Capabilities

### 1. Data Collection

**Japanese Stocks (Yahoo! Finance Japan)**
- Fetch real-time prices for TOPIX listed stocks (symbol format: XXXX.T)
- Retrieve historical data (daily/weekly/monthly)
- Get company fundamentals and financial statements

**US Stocks (Yahoo Finance)**
- Fetch NYSE/NASDAQ listed stocks
- Retrieve pre-market and after-hours data
- Get SEC filings and analyst ratings

**Usage:**
```bash
# Real-time price
python3 scripts/fetch_yahoo.py --symbol 7203.T --realtime

# Historical data
python3 scripts/fetch_yahoo.py --symbol AAPL --period 1y --interval 1d

# Company fundamentals
python3 scripts/fetch_yahoo.py --symbol MSFT --fundamentals
```

### 2. Portfolio Tracking

Track investment portfolio performance across multiple holdings.

**Features:**
- Daily profit/loss calculation
- Sector allocation analysis
- Dividend tracking
- Performance comparison vs benchmark indices

**Portfolio format (JSON):**
```json
{
  "holdings": [
    {
      "symbol": "7203.T",
      "shares": 100,
      "avg_cost": 2500,
      "currency": "JPY"
    },
    {
      "symbol": "AAPL",
      "shares": 50,
      "avg_cost": 150,
      "currency": "USD"
    }
  ]
}
```

**Usage:**
```bash
# Analyze portfolio
python3 scripts/analyze.py --portfolio data/portfolio.json

# Export performance report
python3 scripts/analyze.py --portfolio data/portfolio.json --report performance.md
```

### 3. News & Earnings Summarization

Automatically summarize relevant financial news and earnings reports.

**Features:**
- Japanese: NIKKEI, Bloomberg Japan, company press releases
- US: Bloomberg, Reuters, MarketWatch
- Earnings call transcript analysis
- Key sentiment extraction

**Usage:**
```bash
# Get recent news for a stock
python3 scripts/fetch_yahoo.py --symbol 7203.T --news

# Summarize earnings report
python3 scripts/fetch_yahoo.py --symbol AAPL --earnings --quarter 2024Q4

# Sentiment analysis
python3 scripts/analyze.py --symbol 7203.T --sentiment --days 7
```

### 4. Technical Analysis

Calculate common technical indicators for trading decisions.

**Supported indicators:** See [references/indicators.md](references/indicators.md)

**Usage:**
```bash
# Single indicator
python3 scripts/analyze.py --symbol 7203.T --indicator macd

# Multiple indicators
python3 scripts/analyze.py --symbol AAPL --indicators macd,rsi,bollinger,ema

# Generate trading signals
python3 scripts/analyze.py --symbol 7203.T --signals --threshold 70
```

## Resources

### scripts/

**fetch_yahoo.py**
- Fetch stock data from Yahoo Finance
- Supports real-time, historical, and fundamentals
- Arguments: `--symbol`, `--market` (japan|us), `--period`, `--interval`, `--news`, `--earnings`

**analyze.py**
- Portfolio analysis and technical indicators
- Calculates profit/loss, allocation, indicators
- Arguments: `--portfolio`, `--symbol`, `--indicators`, `--sentiment`, `--signals`

### references/

**indicators.md** - Technical indicator definitions and calculation methods
- MA, EMA, Bollinger Bands
- MACD, RSI, Stochastic Oscillator
- Trading signals interpretation

**data_sources.md** - Available data sources and their coverage
- Japan: TOPIX, Mothers, JASDAQ
- US: NYSE, NASDAQ, AMEX

## Notes

- Japanese stocks use `.T` suffix (e.g., 7203.T for Toyota)
- US stocks use plain symbol (e.g., AAPL)
- Currency conversion uses JPY/USD rate from Yahoo Finance
- Historical data available from 1970 onwards for US stocks
