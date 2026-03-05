---
name: fin-intel-hub
description: Comprehensive financial intelligence hub for SEC filings, crypto on-chain data, news sentiment, macro indicators, and global stock markets (US, China, Hong Kong, Taiwan, Japan, Korea). Use when users need to: (1) Retrieve SEC EDGAR filings (10-K, 10-Q, 8-K), (2) Monitor crypto on-chain metrics and whale alerts, (3) Analyze financial news sentiment, (4) Access macroeconomic indicators (Fed rates, CPI, unemployment), (5) Get global stock prices including Asian markets (HKEX, Tokyo, Taiwan, Korea, Shanghai, Shenzhen), or any financial data research and analysis tasks.
author: xuan622
source: https://github.com/xuan622/fin-intel-hub
license: MIT
environment_variables:
  - name: ALPHA_VANTAGE_API_KEY
    description: Optional - Alpha Vantage API key for US stock data
    required: false
  - name: NEWS_API_KEY
    description: Optional - NewsAPI key for news sentiment analysis
    required: false
  - name: FRED_API_KEY
    description: Optional - FRED API key for macroeconomic data
    required: false
  - name: GLASSNODE_API_KEY
    description: Optional - Glassnode API key for enhanced crypto exchange flow data
    required: false
  - name: ETHERSCAN_API_KEY
    description: Optional - Etherscan API key for Ethereum gas price data
    required: false
  - name: WHALE_ALERT_API_KEY
    description: Optional - Whale Alert API key for whale transaction monitoring
    required: false
requirements: |
  No pip packages required. Uses only Python standard library + requests.
---

# Fin Intel Hub

Financial intelligence hub for OpenClaw. Supports global markets including US, China, Hong Kong, Taiwan, Japan, and Korea.

## Features

- **SEC Filings**: Retrieve 10-K, 10-Q, 8-K filings from EDGAR
- **Global Market Data**: US stocks (Alpha Vantage) + Asian markets (Yahoo Finance)
- **Asian Markets**: Hong Kong, Tokyo, Taiwan, Korea, Shanghai, Shenzhen
- **Crypto On-Chain**: Monitor wallet flows, exchange inflows/outflows
- **News Sentiment**: Aggregate sentiment from financial news sources
- **Macro Dashboard**: Fed rates, CPI, unemployment data

## API Keys (Optional)

All API keys are **optional**. The skill works without any keys using Yahoo Finance for stock data.
Add keys to unlock additional features:

| Service | Purpose | Free Tier | Required? |
|---------|---------|-----------|-----------|
| Yahoo Finance | Global/Asian stocks, indices, futures, commodities | Unlimited | **No** |
| Alpha Vantage | US stocks, earnings | 25 calls/day | Optional |
| NewsAPI | Financial news sentiment | 100 requests/day | Optional |
| FRED API | Macroeconomic data | Unlimited | Optional |
| DeFiLlama | Crypto on-chain data | Unlimited | **No** |

## Quick Start

### SEC Filings
```python
from scripts.sec_filings import get_recent_filings

# Get last 5 10-K filings for Apple
filings = get_recent_filings(ticker="AAPL", form="10-K", limit=5)
```

### Stock Prices
```python
from scripts.market_data import get_price_history

# Get 30-day price history
prices = get_price_history(ticker="TSLA", days=30)
```

### Crypto Data
```python
from scripts.crypto_onchain import get_exchange_flows

# Monitor exchange inflows/outflows
flows = get_exchange_flows(exchange="binance", days=7)
```

## Scripts Reference

- `scripts/sec_filings.py` - SEC EDGAR integration
- `scripts/market_data.py` - US stock prices and earnings (Alpha Vantage)
- `scripts/yahoo_finance.py` - Global/Asian stock prices (Yahoo Finance)
- `scripts/crypto_onchain.py` - Blockchain data via DeFiLlama/CoinGecko
- `scripts/sentiment_news.py` - News sentiment analysis
- `scripts/macro_data.py` - FRED macroeconomic indicators

### Asian Market Examples
```python
from scripts.yahoo_finance import get_hong_kong_stock, get_tokyo_stock, get_taiwan_stock

# Hong Kong - Tencent
prices = get_hong_kong_stock("0700", period="1y")

# Tokyo - Toyota
prices = get_tokyo_stock("7203", period="1y")

# Taiwan - TSMC
prices = get_taiwan_stock("2330", period="1y")
```

### Indices & Futures Examples
```python
from scripts.yahoo_finance import get_sp500, get_nikkei225, get_vix
from scripts.yahoo_finance import get_crude_oil, get_gold, list_available_indices

# Global indices (15+ available)
sp500 = get_sp500(period="1y")
nasdaq = get_nasdaq(period="1y")
nikkei = get_nikkei225(period="1y")
hang_seng = get_hang_seng(period="1y")
vix = get_vix(period="1mo")  # Fear index

# Futures (15+ available)
oil_futures = get_crude_oil(period="6mo")
gold_futures = get_gold(period="6mo")
sp_futures = get_sp500_futures(period="1mo")
natural_gas = get_natural_gas(period="6mo")

# List all available
indices = list_available_indices()
futures = list_available_futures()
```

For detailed API documentation and data schemas, see `references/`.
