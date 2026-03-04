# /sync-ibkr — Sync from Interactive Brokers

Fetch positions and cash balances from IBKR via Flex Query.

## Behavior

1. Run `npx tsx <skill-path>/scripts/data-store.ts load-config` to get config
2. Find the IBKR wallet config. If none configured, tell the user to run `/setup` first
3. Run `npx tsx <skill-path>/scripts/ibkr-sync.ts sync <token> <queryId>`
   - This may take 10-30 seconds (Flex Query generation + polling)
   - Inform the user it's in progress
4. Load portfolio data via `data-store.ts load`
5. Merge results into current portfolio:
   - Match by `symbol` and `source.type === 'ibkr'`
   - Update existing: `quantity`, `avgPrice`, `currentPrice`
   - Add new assets with `source: { type: 'ibkr', walletName: <config name> }`
   - Cash balances are added as CASH type assets
   - Remove assets no longer present in IBKR
6. Save data
7. Show summary:

```
Synced from IBKR "My IBKR":

Positions:
  AAPL: 150 shares @ $153.67 avg (mark: $175.00) — USSTOCK
  0700.HK: 200 shares @ $350.00 avg (mark: $380.00) — HKSTOCK

Cash:
  USD: $5,000.50
  HKD: HK$12,000.00

Trades (recent):
  2024-06-15 BUY AAPL × 100 @ $170.50
  2024-06-10 SELL 0700.HK × 50 @ $375.00

Total: 4 assets synced
```

## Notes

- IBKR provides cost basis (`avgPrice`) and mark price (`currentPrice`)
- HK stocks from SEHK are padded to 4 digits with .HK suffix (e.g., 700 → 0700.HK)
- The Flex Query must include: OpenPositions, CashReport, and Trades sections
- If the query times out (error 1019), the script retries automatically up to 10 times
