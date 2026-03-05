# Polymarket API Reference

## Search for markets

```
GET https://gamma-api.polymarket.com/events?search=<query>&limit=10&active=true
```

Response: array of event objects. Each event has a `markets` array. Relevant fields per market:
- `question` — market title
- `conditionId` — unique ID used to fetch prices
- `outcomePrices` — JSON string: `["<yes_prob>", "<no_prob>"]` (decimals, e.g. `"0.68"`)
- `slug` — URL slug
- `active` / `closed` — filter to open markets only

## Fetch a specific market by conditionId (use this for price checks)

```
GET https://clob.polymarket.com/markets/<conditionId>
```

Returns a single market object. Key fields:
- `question` — market title
- `tokens` — array of `{outcome, price, token_id}`. Find `outcome == "Yes"` for Yes probability.
- `active`, `closed` — market state
- `market_slug` — use to build URL: `https://polymarket.com/event/<market_slug>`

Note: The Gamma API (`gamma-api.polymarket.com/markets?conditionId=`) does NOT filter reliably by conditionId. Always use the CLOB API for individual market lookups.

## Market URL

```
https://polymarket.com/event/<event-slug>
```

The event slug comes from the event object, not the market. If you only have the market slug, use:
```
https://polymarket.com/event/<market-slug>
```

## Notes

- `outcomePrices` is always `["yes_price", "no_price"]` — first value is Yes
- Prices are decimals 0–1 (0.68 = 68%)
- Closed/resolved markets still return data with fixed prices (0 or 1)
- No API key required for read-only access
