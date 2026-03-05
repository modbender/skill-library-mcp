# Stock Data Sources

## Japan Market (Yahoo! Finance Japan)

**Coverage:**
- TOPIX (First Section)
- Mothers (Emerging market)
- JASDAQ (Small-cap market)

**Data Types:**
- Real-time quotes
- Historical prices (daily/weekly/monthly)
- Company fundamentals
- Quarterly earnings
- Dividends

**Symbol Format:**
- XXXX.T (e.g., 7203.T for Toyota)
- XXXX (e.g., 4755 for Rakuten - some older symbols)

**Limitations:**
- Delay: ~15-20 minutes for real-time
- Pre-market data: Limited
- After-hours: Not available

## US Market (Yahoo Finance)

**Coverage:**
- NYSE (New York Stock Exchange)
- NASDAQ (National Association of Securities Dealers)
- AMEX (American Stock Exchange)

**Data Types:**
- Real-time quotes
- Historical prices (daily/weekly/monthly)
- Company fundamentals
- SEC filings (10-K, 10-Q)
- Analyst ratings and price targets
- Earnings calls

**Symbol Format:**
- Plain ticker (e.g., AAPL, GOOGL, TSLA)

**Limitations:**
- Delay: ~15 minutes for non-premium
- Pre-market/After-hours: Available but limited volume

## Currency Conversion

**JPY/USD Rate:**
- Source: Yahoo Finance
- Update frequency: Daily
- Usage: Convert USD holdings to JPY for unified portfolio reporting

**Other Pairs:**
- JPY/EUR
- USD/EUR
- USD/CNY

## Historical Data Availability

**Japan Stocks:**
- Daily data: From 2000 onwards
- Weekly/Monthly: From 1995 onwards

**US Stocks:**
- Daily data: From 1970 onwards
- Weekly/Monthly: From 1950 onwards

**Note:** Older data may have gaps for less liquid stocks.

## API Access

**Yahoo Finance:**
- Type: Unofficial API (HTML scraping)
- Rate limit: ~2000 requests/hour
- Authentication: Not required

**Official APIs (Alternative):**
- Alpha Vantage: 500 requests/day (free tier)
- IEX Cloud: 500,000 requests/month (free tier)
- Polygon.io: 5 requests/minute (free tier)
