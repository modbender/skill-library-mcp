---
name: stock_data
description: "Fetch comprehensive stock data from Simplywall.st. Use when user asks about stock prices, valuation, financials, dividend, or investment analysis for any global stock."
metadata:
  openclaw:
    emoji: "📈"
    version: "1.3.0"
    author: "OpenClaw Community"
    requires: {}
  changelog:
    - "v1.3.0 - Switch to direct HTTP fetch (no API key required), reliable data extraction from SimplyWall.st"
---

# Stock Data - Simplywall.st

Fetch comprehensive stock data from Simplywall.st for any global stock.

## When to Use

- User asks about stock prices ("Berapa harga saham ADRO?")
- User wants valuation analysis ("ADRO undervalued atau overvalued?")
- User needs financial data ("Berapa revenue BBCA?")
- User wants dividend info ("Berapa dividend yield TLKM?")
- User asks for investment analysis ("Bagaimana analisa NVDA?")

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| ticker | string | Yes | Stock ticker symbol (e.g., ADRO, AAPL, BBRI) |
| exchange | string | No | Exchange hint (e.g., IDX, NASDAQ, NYSE) |

## Output Structure

```json
{
  "success": true,
  "ticker": "ADRO",
  "exchange": "IDX",
  "data": {
    "company": {
      "name": "PT Alamtri Resources Indonesia Tbk",
      "description": "Company description...",
      "country": "Indonesia",
      "founded": 2004,
      "website": "www.alamtri.com"
    },
    "price": {
      "lastSharePrice": 2300,
      "currency": "IDR",
      "return7D": 0.036,
      "return1Yr": 0.055
    },
    "valuation": {
      "marketCap": 3908.23,
      "peRatio": 13.07,
      "pbRatio": 0.85,
      "pegRatio": 0.41,
      "intrinsicDiscount": -39.06,
      "status": "overvalued"
    },
    "financials": {
      "eps": 0.0104,
      "roe": 8.77,
      "roa": 3.09,
      "debtEquity": 0.12
    },
    "dividend": {
      "yield": 13.48,
      "futureYield": 5.64,
      "payingYears": 10,
      "payoutRatio": 1.88
    },
    "forecast": {
      "earningsGrowth1Y": 0.51,
      "roe1Y": 9.74,
      "analystCount": 10
    },
    "snowflake": {
      "value": 3,
      "future": 6,
      "past": 2,
      "health": 6,
      "dividend": 4
    },
    "recentEvents": [
      {
        "title": "Investor sentiment improves...",
        "description": "..."
      }
    ],
    "fetchedAt": "2026-02-22T08:30:00Z"
  }
}
```

## Example Usage

```
User: "Cek saham ADRO gimana?"
→ Call stock_data(ticker="ADRO")

User: "What's Apple's P/E ratio?"
→ Call stock_data(ticker="AAPL", exchange="NASDAQ")

User: "Berapa dividend yield TLKM?"
→ Call stock_data(ticker="TLKM")
```

## Supported Exchanges

| Exchange | Code | Example Tickers |
|----------|------|-----------------|
| Indonesia | IDX | ADRO, BBRI, BBCA, TLKM |
| US NASDAQ | NASDAQ | AAPL, NVDA, GOOGL |
| US NYSE | NYSE | JPM, BAC, WMT |
| Australia | ASX | BHP, CBA, RIO |
| UK | LSE | HSBA, BP, SHEL |
| Canada | TSX | RY, TD, CNR |
| Singapore | SGX | DBS, OCBC |

## Data Source

- Direct HTTP fetch from SimplyWall.st
- Parses `__REACT_QUERY_STATE__` data embedded in HTML
- No API key required
- Price data updated daily
- Fair value estimates based on proprietary model
- Use as guide only, not investment advice

## Technical Details

This skill uses direct HTTP requests to fetch SimplyWall.st pages, then parses the `__REACT_QUERY_STATE__` data embedded in the HTML to extract structured stock information including:
- Company基本信息
- Current price and returns
- Valuation metrics (PE, PB, PEG, market cap)
- Financial ratios (ROE, ROA, EPS, debt/equity)
- Dividend information (yield, payout ratio)
- Forecast data (growth estimates, analyst count)
- Snowflake ratings (5-point scoring system)
- Recent company events
