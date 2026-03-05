---
name: open-market-data
description: Query free financial data APIs — stocks, crypto, macro, SEC filings
version: 0.1.0
tags: [finance, stocks, crypto, macro, sec, edgar, fred]
tools: [Bash]
metadata:
  openclaw:
    requires:
      bins: [node, omd]
    install:
      - kind: node
        package: open-market-data
        bins: [omd]
    homepage: https://github.com/anotb/open-market-data
    emoji: "\U0001F4C8"
---

# open-market-data (omd)

Unified CLI for free financial data. Queries 8 sources behind a single interface with automatic routing and fallback.

## Quick Reference

```bash
# Stock quotes
omd quote AAPL
omd quote AAPL MSFT GOOGL

# Search
omd search "Apple Inc"

# Financial statements
omd financials AAPL
omd financials AAPL -p quarterly -l 8

# Price history
omd history AAPL --days 90

# Earnings
omd earnings AAPL

# Dividends
omd dividends AAPL

# Options chain
omd options AAPL
omd options AAPL -t call

# SEC filings
omd filing AAPL --type 10-K --latest
omd filing TSLA --type 8-K -l 5

# Insider transactions
omd insiders AAPL

# Crypto
omd crypto BTC
omd crypto top 20
omd crypto history ETH -d 30

# Macroeconomic data
omd macro GDP
omd macro GDP --limit 12
omd macro search "unemployment rate"

# Output formats
omd --json quote AAPL
omd --plain quote AAPL

# Force specific source
omd quote AAPL --source finnhub
omd financials AAPL --source sec-edgar
omd macro NY.GDP.MKTP.CD --source worldbank

# Bypass cache
omd --no-cache quote AAPL

# See all sources and their status
omd sources

# Configure API keys
omd config set fredApiKey <key>
omd config show
```

## Sources

| Source | Key? | Best For |
|--------|------|----------|
| SEC EDGAR | No | Filings, XBRL financials, insider transactions |
| Yahoo Finance | No | Real-time quotes, price history, options, dividends |
| Binance | No | Crypto prices (non-US only) |
| CoinGecko | Free key | Crypto rankings, broader crypto coverage |
| FRED | Free key | GDP, unemployment, interest rates, 800K+ economic series |
| Finnhub | Free key | Real-time stock quotes, earnings data |
| Alpha Vantage | Free key | Stock quotes, financials, price history (25/day limit) |
| World Bank | No | Global economic indicators (GDP, unemployment, inflation) |

## When to Use --json

Use `--json` when you need to parse the output programmatically. Always place `--json` before the command:

```bash
omd --json quote AAPL
omd --json financials AAPL -p quarterly
omd --json crypto top 10
omd --json macro GDP --limit 5
```

## Configuration

API keys via env vars or CLI:

```bash
export FRED_API_KEY=your_key
export COINGECKO_API_KEY=your_key
export FINNHUB_API_KEY=your_key
export ALPHA_VANTAGE_API_KEY=your_key
export EDGAR_USER_AGENT="YourCompany you@email.com"

# Or use CLI config
omd config set fredApiKey your_key
omd config set coingeckoApiKey your_key
omd config set finnhubApiKey your_key
omd config set alphaVantageApiKey your_key
omd config show
```

## Routing

Commands automatically route to the best available source. If the top source fails or hits its rate limit, it falls back to the next one. Use `--source <name>` to force a specific provider.

| Data Type | Priority Order |
|-----------|---------------|
| Stock quotes | Yahoo → Finnhub → Alpha Vantage |
| Financials | SEC EDGAR → Yahoo → Alpha Vantage |
| Price history | Yahoo → Alpha Vantage |
| Earnings | Yahoo → Finnhub |
| Dividends | Yahoo |
| Options | Yahoo |
| SEC filings | SEC EDGAR |
| Insiders | SEC EDGAR |
| Crypto | Binance → CoinGecko |
| Macro/economic | FRED → World Bank |
| Search | SEC EDGAR → Yahoo → Finnhub → Alpha Vantage |
