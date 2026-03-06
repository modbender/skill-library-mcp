# Search Query Templates (Concise)

Use these templates with search engines and `site:` filters.

Detailed source list is in `references/sources.md`.

## 1) Identity and Listing

- `<COMPANY> ticker symbol exchange`
- `<TICKER> exchange listing market`

## 2) Official Filings and Disclosures

- `<TICKER> official filings latest`
- `<COMPANY> investor relations latest release`
- `site:sec.gov <TICKER> 10-Q OR 10-K OR 8-K`
- `site:hkexnews.hk <TICKER> announcement`
- `site:sse.com.cn <TICKER> 公告`
- `site:szse.cn <TICKER> 公告`

## 3) Market Data and Price Context

- `site:finance.yahoo.com <TICKER> quote`
- `<TICKER> latest close open high low volume`
- `<TICKER> 52 week range market cap`

## 4) News and Analyst Context

- `site:reuters.com <TICKER> earnings guidance`
- `site:bloomberg.com <TICKER> stock news`
- `<TICKER> analyst rating target price`

## 5) Technical Context

- `<TICKER> RSI MACD moving average`
- `<TICKER> support resistance trend`

## 6) Macro Context (if used in thesis)

- `<MARKET> benchmark index today`
- `<MARKET> central bank policy rate outlook`
- `US 10Y yield today`

## Data Quality Rules

1. Prefer Tier-1 official sources first.
2. Cross-check critical values with two independent sources.
3. Record source URL and timestamp in report.
