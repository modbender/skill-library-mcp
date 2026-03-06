# ClawWatch API Notes & Quirks

## CoinPaprika (Primary Crypto)

- **Free tier:** No API key needed. 10 calls/sec, 20,000 credits/month.
- **Use CoinPaprika IDs** (e.g., `btc-bitcoin`) not symbols (`BTC`). ClawWatch handles this mapping automatically.
- **Batch prices:** `/tickers` returns ALL ~2,500 coins in one call → filter locally. ONE API call regardless of watchlist size.
- **ID format:** `{symbol_lowercase}-{name_lowercase_hyphenated}` — e.g., `btc-bitcoin`, `eth-ethereum`, `sol-solana`.
- **Coin list:** Cache `/coins` response locally, refresh weekly.
- **Supports EUR:** Add `?quotes=USD,EUR` to `/tickers`.
- **Extra data:** 1h, 24h, 7d, 30d percent changes, ATH price and date.

## CoinCap (Fallback Crypto)

- **Free tier:** 200 req/min without key, 500/min with free key from coincap.io.
- **No API key required** — works out of the box.
- **IDs are lowercase names:** `bitcoin`, `ethereum`, `solana`.
- **⚠️ Returns numbers as strings** — always parse to float.
- **Supports `ids` param:** `GET /assets?ids=bitcoin,ethereum` for filtered requests.
- **No EUR prices** — USD only. Use as fallback, not primary.
- **Convert from CoinPaprika IDs:** Strip the symbol prefix: `btc-bitcoin` → `bitcoin`.

## yfinance (Yahoo Finance)

- **No API key required** — scrapes Yahoo Finance public endpoints.
- **Fragile:** Can break when Yahoo changes their page layout. Always wrapped in try/except.
- **Rate limits:** Undocumented. Random 1-3s delays between calls. Can get 429 errors.
- **Batch:** Use `yf.download()` for batch fetching, not individual `Ticker` objects.
- **`.info` is slow:** ~1-2 sec per ticker (full page scrape). Only use for deep info, not routine price checks.
- **International stocks:** Append exchange suffix: `SAP.DE` (XETRA), `7203.T` (Tokyo), etc.
- **Personal use only** per Yahoo ToS.

## Alternative.me Fear & Greed

- **Completely free**, no key needed.
- **60 requests/minute** limit.
- **Updates daily** — cache for 1 hour is plenty.
- **Scale:** 0-24 Extreme Fear, 25-49 Fear, 50-74 Greed, 75-100 Extreme Greed.

## Finnhub (Stock Fallback)

- **Free API key** required (60 calls/min).
- **No batching** — one call per ticker.
- **Use only as fallback** when yfinance fails.
- **Quote fields:** `c`=current, `d`=change, `dp`=percent change, `h`=high, `l`=low, `o`=open.

## Monthly Budget (20 assets, check every 4h)

| API | Daily Calls | Monthly Calls | Free Limit |
|-----|-------------|---------------|------------|
| CoinPaprika | ~6 | ~180 | 20,000 credits/mo |
| CoinCap | 0 (fallback) | ~0 | 200/min |
| yfinance | ~60 | ~1,800 | Unofficial |
| Fear & Greed | ~6 | ~180 | Unlimited |
| Finnhub | 0 (fallback) | ~0 | 60/min |
