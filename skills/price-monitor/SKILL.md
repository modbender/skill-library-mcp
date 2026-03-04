---
description: Track crypto and stock prices in real-time with configurable alerts and multi-currency support.
---

# Price Monitor

Real-time cryptocurrency & stock price tracking with alerts.

**Use when** checking crypto prices, setting price alerts, or monitoring market movements.

## Requirements

- Internet access (CoinGecko API — no API key needed for free tier)
- `curl` or `python3` for API calls
- Optional: `jq` for JSON parsing in shell

## Instructions

1. **Fetch current price** — Use CoinGecko API:
   ```bash
   curl -s "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true&include_market_cap=true" | jq .
   ```

2. **Support multiple assets** — Accept comma-separated coin IDs (e.g., `bitcoin,ethereum,solana`). Map common tickers:
   - BTC → `bitcoin`, ETH → `ethereum`, SOL → `solana`, XRP → `ripple`, ADA → `cardano`
   - Full list: `https://api.coingecko.com/api/v3/coins/list`

3. **Display as table**:
   ```
   | Asset    | Price (USD)  | 24h Change | Market Cap     |
   |----------|-------------|------------|----------------|
   | Bitcoin  | $97,432.10  | +2.3%      | $1.92T         |
   | Ethereum | $3,245.67   | -0.8%      | $390B          |
   ```

4. **Price alerts** — Store in `~/.openclaw/price-alerts.json`:
   ```json
   [{"coin": "bitcoin", "condition": ">", "target": 100000, "currency": "usd", "created": "ISO8601"}]
   ```
   Check alerts on heartbeat or invocation. Remove triggered alerts after notifying.

5. **Historical data** — Use `/coins/{id}/market_chart?vs_currency=usd&days=7` for trend analysis.

6. **Multi-currency** — Support `vs_currencies` param for JPY, EUR, GBP, etc. Default: USD.

## Edge Cases & Troubleshooting

- **Rate limiting**: CoinGecko free tier allows ~30 req/min. Cache responses for 60s minimum.
- **Unknown coin ID**: Search `/coins/list` endpoint first. Suggest close matches if not found.
- **API down**: Retry once after 5s. Report error clearly if still failing.
- **Stale data**: CoinGecko may lag 1-3 min on free tier — note this in output.

## Security

- No API keys to protect on free tier.
- If using a paid CoinGecko key, never expose it in output or logs.
- Validate user input for coin IDs (alphanumeric and hyphens only).

## Notes

- For stocks, use Yahoo Finance endpoints or suggest `curl` with `query1.finance.yahoo.com`.
- Store alerts in a JSON file, not in memory (survives restarts).
