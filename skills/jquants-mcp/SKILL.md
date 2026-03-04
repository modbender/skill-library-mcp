---
name: jquants-mcp
description: "Access JPX stock market data via J-Quants API — search stocks, get daily OHLCV prices, financial summaries (revenue, profit, EPS, ROE), and earnings calendar for Tokyo Stock Exchange (TSE) listed companies. Japan stock price data."
metadata: {"openclaw":{"emoji":"💹","requires":{"bins":["jquants-mcp"],"env":["JQUANTS_MAIL_ADDRESS","JQUANTS_PASSWORD"]},"install":[{"id":"uv","kind":"uv","package":"jquants-mcp","bins":["jquants-mcp"],"label":"Install jquants-mcp (uv)"}],"tags":["japan","stock","jpx","tse","price","ohlcv","finance","mcp","jquants"]}}
---

# J-Quants: JPX Stock Market Data

Access Tokyo Stock Exchange (TSE) listed stock data via the official J-Quants API. Search stocks, get daily OHLCV prices, financial summaries, and earnings announcement calendar.

**Important: This tool is for personal use only.** Data redistribution is prohibited by J-Quants Terms of Service. https://jpx-jquants.com/termsofservice

## Use Cases

- Search for TSE-listed stocks by code or company name
- Get daily OHLCV price data for any stock
- Retrieve financial summaries (revenue, profit, EPS, ROE)
- Check upcoming earnings announcement dates
- Compare financial metrics across companies

## Commands

### Search stocks
```bash
# By stock code
jquants-mcp search 7203

# By company name (Japanese)
jquants-mcp search トヨタ

# JSON output
jquants-mcp search ソニー --json-output
```

### Get stock prices
```bash
# Default: last 30 days
jquants-mcp price 7203

# With date range
jquants-mcp price 7203 --start-date 2024-01-01 --end-date 2024-12-31

# JSON output
jquants-mcp price 7203 --json-output
```

### Get financial data
```bash
jquants-mcp financials 7203
jquants-mcp financials 6758 --json-output
```

### Get earnings calendar
```bash
# Default: next 30 days
jquants-mcp calendar

# With date range
jquants-mcp calendar --start-date 2024-04-01 --end-date 2024-06-30
```

### Test connectivity
```bash
jquants-mcp test
```

## Workflow

1. `jquants-mcp search <company>` → find stock code
2. `jquants-mcp price <code>` → get price history
3. `jquants-mcp financials <code>` → get financial data
4. `jquants-mcp calendar` → check earnings dates

## Setup

- Requires `JQUANTS_MAIL_ADDRESS` and `JQUANTS_PASSWORD` environment variables
- Free account registration: https://jpx-jquants.com/
- Python package: `pip install jquants-mcp` or `uv tool install jquants-mcp`

## Terms of Service

By using this tool, you agree to the J-Quants Terms of Service.
Data is for personal use only — redistribution is prohibited.
