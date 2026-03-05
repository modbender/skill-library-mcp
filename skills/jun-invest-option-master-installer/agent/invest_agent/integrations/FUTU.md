# Futu OpenAPI 接入（富途证券）

Primary reference:
- https://openapi.futunn.com/futu-api-doc/intro/intro.html

## Requirements
- Python SDK: `futu-api`
  - Recommended: create venv under `invest_agent/.venv` and install there.
- Ensure OpenD (FutuOpenD) is running and reachable from this host.

## Permission fallback
- If US ETF quotes (e.g., SPY/QQQ) are not permitted via Futu, keep options via Futu but fetch ETF/index spot data via public skills (preferred) or web_fetch/web_search as temporary fallback.

## Goal
Use Futu OpenAPI as the primary market/broker data source for the Data role (prices, options chain, calendar where available).

## Pending inputs (will ask only when needed)
- Connection method (OpenD gateway location / local vs remote)
- Credentials / account environment (paper vs live)
- Market permissions enabled (US options / quotes)

## Integration plan (programmatic)
- Create a thin adapter module that provides:
  - get_quotes(tickers, asof)
  - get_iv_surface_or_chain(ticker, dte_range)
  - get_calendar_events(window)
  - healthcheck() + latency measurement
- Adapter must annotate every value with source + timestamp.

## Risk/Policy notes
- Data role only: facts and confidence scoring; no trade opinions.
- Do not place orders; execution remains human-only.
