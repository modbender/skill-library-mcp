# Fin Intel Hub

**Author:** xuan622  
**Repository:** https://github.com/xuan622/fin-intel-hub  
**License:** MIT  
**Language:** Python  

OpenClaw skill for comprehensive financial intelligence and analytics.

**🌏 Multi-language Support:** [English](#fin-intel-hub) | [简体中文 / 繁體中文](README_CN.md)

## Features

- **SEC Filings** — Retrieve 10-K, 10-Q, 8-K filings from EDGAR
- **Market Data** — Stock prices, earnings, fundamentals (Alpha Vantage + Yahoo Finance)
- **Asian Markets** — Hong Kong, Tokyo, Taiwan, Korea, Shanghai, Shenzhen exchanges
- **Indices & Futures** — 15+ global indices, commodity futures
- **Crypto On-Chain** — DeFi TVL, exchange flows, gas prices (DeFiLlama, CoinGecko)
- **News Sentiment** — Financial news analysis with sentiment scoring (NewsAPI)
- **Macro Data** — Fed rates, CPI, unemployment, GDP (FRED API)

## Quick Start

### 1. Install

#### Method A: Install via Clawhub (Recommended)
```bash
npx clawhub install fin-intel-hub
```

#### Method B: Manual Installation
Clone or download the repository to your OpenClaw skills directory:
```bash
git clone https://github.com/xuan622/fin-intel-hub.git ~/.openclaw/skills/fin-intel-hub
```

Or download and extract to `~/.openclaw/skills/fin-intel-hub/`.

### 2. Get API Keys (Optional)

**No API keys required to start!** The skill works out-of-the-box with Yahoo Finance for global stock data.

Add API keys to unlock additional features:

| Service | Purpose | Free Tier | Get Key |
|---------|---------|-----------|---------|
| **Yahoo Finance** | **Global stocks, indices, futures** | **Unlimited** | **No key needed** ✅ |
| Alpha Vantage | US stocks, earnings | 25 calls/day | [alphavantage.co](https://www.alphavantage.co/support/#api-key) |
| NewsAPI | Financial news sentiment | 100 requests/day | [newsapi.org](https://newsapi.org/register) |
| FRED | Macroeconomic data | 120 requests/min | [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html) |
| DeFiLlama | DeFi TVL, crypto data | Unlimited | N/A |

### 3. Set Environment Variables (Optional)

```bash
# Optional - only if you want these features
export ALPHA_VANTAGE_API_KEY="your_key"
export NEWS_API_KEY="your_key"
export FRED_API_KEY="your_key"
```

Or add to your `~/.bashrc` or `~/.zshrc` for persistence.

## Usage

### SEC Filings
```python
from scripts.sec_filings import get_recent_filings, get_latest_10k

# Get recent 10-K filings
filings = get_recent_filings("AAPL", form="10-K", limit=5)

# Get latest 10-K summary
latest = get_latest_10k("TSLA")
```

### Market Data
```python
from scripts.market_data import get_price_history, get_quote, get_company_overview

# Price history
prices = get_price_history("AAPL", days=30)

# Real-time quote
quote = get_quote("TSLA")

# Company fundamentals
overview = get_company_overview("MSFT")
```

### Asian Markets
```python
from scripts.yahoo_finance import get_hong_kong_stock, get_tokyo_stock, get_taiwan_stock

# Hong Kong - Tencent (0700.HK)
prices = get_hong_kong_stock("0700", period="1y")

# Tokyo - Toyota (7203.T)
prices = get_tokyo_stock("7203", period="1y")

# Taiwan - TSMC (2330.TW)
prices = get_taiwan_stock("2330", period="1y")

# Korea - Samsung (005930.KS)
from scripts.yahoo_finance import get_korea_stock
prices = get_korea_stock("005930", period="1y")

# China - Shanghai/Shenzhen
from scripts.yahoo_finance import get_shanghai_stock, get_shenzhen_stock
prices = get_shanghai_stock("600519")  # Kweichow Moutai
prices = get_shenzhen_stock("000001")  # Ping An Bank
```

### Indices & Futures
```python
from scripts.yahoo_finance import get_sp500, get_nasdaq, get_nikkei225, get_hang_seng
from scripts.yahoo_finance import get_crude_oil, get_gold, get_sp500_futures

# Major Indices
sp500 = get_sp500(period="1y")
nasdaq = get_nasdaq(period="1y")
nikkei = get_nikkei225(period="1y")
hang_seng = get_hang_seng(period="1y")
vix = get_vix(period="1mo")  # Fear index

# Futures
oil_futures = get_crude_oil(period="6mo")
gold_futures = get_gold(period="6mo")
sp_futures = get_sp500_futures(period="1mo")

# List all available
from scripts.yahoo_finance import list_available_indices, list_available_futures
indices = list_available_indices()   # 15+ global indices
futures = list_available_futures()   # 15+ futures contracts
```

### Crypto On-Chain
```python
from scripts.crypto_onchain import get_defi_tvl, get_top_exchanges, get_exchange_flows

# DeFi TVL
tvl = get_defi_tvl()  # Global
tvl_aave = get_defi_tvl("aave")  # Specific protocol

# Top exchanges
exchanges = get_top_exchanges(10)
```

### News Sentiment
```python
from scripts.sentiment_news import get_sentiment_summary

# Sentiment analysis for a ticker
sentiment = get_sentiment_summary(ticker="AAPL", days=7)
print(f"Sentiment: {sentiment['sentiment_label']}")  # Bullish/Bearish/Neutral
```

### Macro Data
```python
from scripts.macro_data import get_macro_dashboard, get_fed_rate, get_cpi

# Full dashboard
dashboard = get_macro_dashboard()

# Individual indicators
fed_rate = get_fed_rate()
cpi = get_cpi()
unemployment = get_unemployment()
```

## Project Structure

```
fin-intel-hub/
├── SKILL.md                  # Skill documentation
├── README.md                 # This file
├── SECURITY.md               # Security hardening checklist
├── scripts/
│   ├── sec_filings.py        # SEC EDGAR integration
│   ├── market_data.py        # Alpha Vantage (US stocks)
│   ├── yahoo_finance.py      # Yahoo Finance (global/Asian stocks)
│   ├── crypto_onchain.py     # DeFiLlama, CoinGecko (crypto)
│   ├── sentiment_news.py     # NewsAPI (news + sentiment)
│   └── macro_data.py         # FRED API (macro indicators)
└── references/               # API documentation (optional)
```

## API Key Tiers

All APIs used have free tiers suitable for personal/research use:

### No Key Required (Works Out-of-the-Box)
- **Yahoo Finance**: Unlimited - Global stocks, Asian markets, indices, futures, commodities
- **DeFiLlama**: Unlimited - DeFi TVL, crypto on-chain data
- **CoinGecko**: Free tier available - Crypto exchange data

### Optional Keys (Unlock Additional Features)
- **Alpha Vantage**: 25 API calls/day free - US stocks, earnings (Yahoo Finance covers stocks)
- **NewsAPI**: 100 requests/day free - Financial news sentiment analysis
- **FRED**: 120 requests/minute free - US macroeconomic indicators

For higher limits, upgrade directly with the API providers.

## Security

- ✅ **Input Validation** - All ticker symbols sanitized (SQL injection prevention)
- ✅ **Rate Limiting** - Automatic throttling for all APIs (25/day Alpha Vantage, etc.)
- ✅ **Secure Logging** - Sensitive data (API keys, tokens) auto-redacted
- ✅ **Safe Errors** - No stack traces or sensitive info leaked to users
- ✅ **API Keys** - Environment variables only, no hardcoded secrets

See `SECURITY.md` for detailed security documentation.

## Disclaimer

**IMPORTANT: READ THIS DISCLAIMER CAREFULLY BEFORE USING THIS SKILL**

### Not Financial Advice
This skill is for **informational and educational purposes only**. All data, analysis, and information provided through this skill should not be construed as financial advice, investment recommendations, or trading recommendations.

### No Liability
The authors, contributors, and maintainers of this skill:
- **Are not financial advisors** and do not provide investment advice
- **Assume no liability** for any losses, damages, or financial harm resulting from the use of this skill
- **Make no guarantees** about the accuracy, completeness, or timeliness of the data
- **Are not responsible** for any trading decisions, investment losses, or financial consequences

### Data Accuracy
- Data is sourced from third-party APIs (Yahoo Finance, Alpha Vantage, etc.)
- We do not control, verify, or guarantee the accuracy of external data
- Data may be delayed, incomplete, or contain errors
- Always verify critical information with official sources before making financial decisions

### Risk Warning
- **Investing involves substantial risk**, including possible loss of principal
- Past performance does not guarantee future results
- Options trading, crypto trading, and stock trading carry significant risk
- Do not trade with money you cannot afford to lose

### Professional Advice
Always consult with a **qualified financial advisor** before making investment decisions. This skill is not a substitute for professional financial advice tailored to your specific situation.

### Jurisdiction
This skill is provided "as is" without warranty of any kind. By using this skill, you agree that any disputes shall be governed by applicable laws and that you use this skill at your own risk.

**By using this skill, you acknowledge and agree to this disclaimer.**

## License

MIT - Free to use, modify, and distribute.

## Contributing

This is a Boring Life project. Built by AI, guided by humans.

---

**Built with 🏗️ by David (CTO, Boring Life)**
