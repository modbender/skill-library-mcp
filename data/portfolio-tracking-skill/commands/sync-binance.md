# /sync-binance — Sync from Binance

Fetch all balances from a configured Binance account and update the portfolio.

## Behavior

1. Run `npx tsx <skill-path>/scripts/data-store.ts load-config` to get config
2. Find the Binance wallet config. If none configured, tell the user to run `/setup` first
3. Run `npx tsx <skill-path>/scripts/binance-sync.ts sync <apiKey> <apiSecret>`
4. Load portfolio data via `data-store.ts load`
5. Merge results into current portfolio:
   - For each returned asset, find existing asset with same `symbol` and `source.type === 'binance'`
   - If found: update `quantity` (replace, not add)
   - If not found: create new asset with `source: { type: 'binance', walletName: <config name> }`
   - Remove assets that were previously synced from this Binance account but no longer appear (quantity dropped to 0)
6. Save data
7. Show summary:

```
Synced from Binance "My Binance":

Updated:
  BTC: 1.500 (was 1.200)
  ETH: 10.000 (was 8.500)

New:
  SOL: 50.000

Removed:
  DOGE (no longer held)

Total: 15 assets synced
```

## Notes

- Stablecoins (USDT, USDC, etc.) are classified as CASH type
- New assets get `currentPrice: 0` — remind user to run `/prices` after sync
- The `avgPrice` for synced assets is set to 0 (Binance doesn't provide cost basis)
- All Binance assets have `currency: 'USD'`
- If multiple Binance accounts are configured, ask which one to sync
