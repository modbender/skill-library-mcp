# /portfolio — View & Manage Portfolio

Manage investment portfolios stored locally in `~/.portfolio-tracker/data.json`.

## Behavior

When invoked without arguments, show the current portfolio summary.

### Default: Show Portfolio Summary

1. Run `npx tsx <skill-path>/scripts/data-store.ts load` to get data
2. Find the current portfolio (by `currentPortfolioId`)
3. For each asset, calculate:
   - **Value** = `quantity × currentPrice`
   - **P&L** = `(currentPrice - avgPrice) × quantity`
   - **P&L %** = `(currentPrice - avgPrice) / avgPrice × 100`
4. Convert all values to `displayCurrency` using `exchangeRates`
5. Group assets by type (CRYPTO, USSTOCK, HKSTOCK, ASHARE, CASH)
6. Show a summary table:

```
Portfolio: Main (USD)
Last refreshed: 2024-01-15T10:30:00Z

| Symbol | Type    | Qty    | Price    | Value      | P&L       | P&L %  |
|--------|---------|--------|----------|------------|-----------|--------|
| BTC    | CRYPTO  | 1.500  | $67,500  | $101,250   | +$11,250  | +12.5% |
| AAPL   | USSTOCK | 100    | $175.50  | $17,550    | +$2,550   | +17.0% |
| ...    |         |        |          |            |           |        |

Total: $118,800
```

7. Show allocation breakdown by asset type (percentage of total)

### Sub-commands

Users may ask to:

- **"add [symbol]"** — Search for an asset, confirm details, ask for quantity and avg price, then add it
- **"remove [symbol or id]"** — Remove an asset from the portfolio
- **"edit [symbol or id]"** — Edit quantity, avg price, or other fields
- **"list portfolios"** — Show all portfolios with their asset counts
- **"create [name]"** — Create a new portfolio
- **"switch [name or id]"** — Switch active portfolio
- **"delete [name or id]"** — Delete a portfolio (cannot delete the last one)
- **"currency [USD/CNY/HKD]"** — Change display currency

### Adding an Asset

1. Use `fetch-prices.ts search <query>` to find matching symbols
2. Present results and ask user to confirm the right one
3. Ask for quantity and average purchase price (or use current price as default)
4. Fetch current price via `fetch-prices.ts crypto/stock <symbol>`
5. Generate a unique ID and add to the portfolio
6. Save data

### Removing/Editing

1. Load data
2. Find the asset by symbol (case-insensitive) or by ID
3. If multiple matches, ask user to disambiguate
4. Apply changes and save

## Notes

- Always save data after modifications using `data-store.ts save` (pipe JSON to stdin)
- When displaying values, respect the `displayCurrency` setting
- Treat SGOV as a cash equivalent for grouping and display purposes
