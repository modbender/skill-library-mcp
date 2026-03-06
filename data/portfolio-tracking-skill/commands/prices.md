# /prices — Refresh All Prices

Batch-refresh current prices for all assets in the active portfolio.

## Behavior

1. Run `npx tsx <skill-path>/scripts/data-store.ts load` to get data
2. Get the current portfolio's assets
3. Pipe the assets JSON to `npx tsx <skill-path>/scripts/fetch-prices.ts refresh` via stdin
4. Simultaneously run `npx tsx <skill-path>/scripts/fetch-prices.ts fx` for exchange rates
5. For each asset, update `currentPrice` from the returned price map
6. Update `exchangeRates` in data
7. Set `lastPriceRefresh` to current ISO timestamp
8. Save data via `data-store.ts save`
9. Show a summary of updated prices:

```
Prices refreshed at 2024-01-15T10:30:00Z

Updated:
  BTC:  $67,500 (was $65,000, +3.8%)
  AAPL: $175.50 (was $170.00, +3.2%)
  ...

FX Rates: 1 USD = 7.25 CNY = 7.81 HKD

Failed (no price found):
  OBSCURE_TOKEN
```

## Notes

- CASH assets (USD, CNY, HKD) are always priced at 1 in their native currency — skip them
- If an asset's price fetch fails, keep the existing `currentPrice` unchanged
- Show which assets failed to update
- The `refresh` command deduplicates symbols automatically
