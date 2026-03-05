# Kalshi API Notes

## Authentication

Uses RSA-PSS request signing:

1. Generate message: `${timestampMs}${METHOD}${pathWithPrefix}`
   - Timestamp in milliseconds
   - Method uppercase (GET, POST, DELETE)
   - Path includes /trade-api/v2 prefix
   - Query params stripped before signing

2. Sign with RSA-PSS (SHA-256, MGF1-SHA256, saltlen=digest)

3. Headers:
   - `KALSHI-ACCESS-KEY`: API key UUID
   - `KALSHI-ACCESS-TIMESTAMP`: millisecond timestamp
   - `KALSHI-ACCESS-SIGNATURE`: base64 signature

## Base URLs

- **Production**: `https://api.elections.kalshi.com/trade-api/v2`
- **Demo**: `https://demo-api.kalshi.co/trade-api/v2`

The CLI uses production by default.

## Data Format Conventions

### Monetary Fields

**Balance/Portfolio API** returns integers in CENTS:

- `balance: 42069` = $420.69
- `portfolio_value: 50000` = $500.00

**Market/Order APIs** use FixedPointDollars (strings, 4dp):

- `yes_bid_dollars: "0.6500"` = 65¢
- `no_ask_dollars: "0.3600"` = 36¢
- `last_price_dollars: "0.6200"` = 62¢

### Volume/Quantity Fields

**FixedPointCount** (strings, 2dp):

- `volume_fp: "12345.00"` = 12,345 contracts
- `open_interest_fp: "8500.50"` = 8,500.5 contracts

### Timestamps

ISO 8601 format:

- `close_time: "2025-03-15T16:00:00Z"`
- `created_time: "2025-02-13T22:30:15Z"`

## Common API Patterns

### Pagination

Endpoints that return lists use cursor-based pagination:

```json
{
  "cursor": "eyJza2lwIjoxMDB9",
  "markets": [ ... ]
}
```

Pass `cursor` param to get next page. When `cursor` is empty/null, you've reached the end.

### Status Filters

Markets have lifecycle statuses:

- `open` - Currently tradeable
- `closed` - Trading ended, awaiting resolution
- `settled` - Resolved and paid out

Use `status` param to filter.

### Market Tickers

Format: `{SERIES}-{DATE}-{STRIKE}`

- Series: Event category (e.g., KXBTCD = Bitcoin daily)
- Date: Expiration (e.g., 26FEB14 = Feb 14, 2026)
- Strike: Threshold (e.g., B55500 = "Bitcoin > $55,500")

Always uppercase.

## Rate Limits

Not explicitly documented, but be reasonable:

- Batch requests when possible
- Cache trending/search results (they don't change second-to-second)
- Don't poll order status in tight loops

## Error Handling

API returns structured errors:

```json
{
  "code": "INSUFFICIENT_BALANCE",
  "message": "Account balance too low for this order",
  "service": "orders"
}
```

Common codes:

- `INSUFFICIENT_BALANCE` - Not enough cash
- `MARKET_CLOSED` - Can't trade on closed market
- `INVALID_ORDER` - Bad params (price out of range, etc.)
- `ORDER_NOT_FOUND` - Order ID doesn't exist or already canceled

## Gotchas

1. **Price validation** - Must be 1-99 cents. 0 and 100 are invalid.

2. **Position tracking** - You must track what you own. The API won't prevent you from selling more than you have (it'll just fail).

3. **Market resolution** - Markets can resolve early under certain conditions. Check `can_close_early` field.

4. **Fractional contracts** - Some markets support fractional trading (`fractional_trading_enabled`). Most don't.

5. **Order fills** - Limit orders may partially fill. Check `fill_count` vs `initial_count`.

## Web URLs

Market web pages follow pattern:
`https://kalshi.com/markets/{series_ticker_lowercase}`

Example:

- `event_ticker: "KXBTCD-26FEB14"`
- `series_ticker: "KXBTCD"`
- URL: `https://kalshi.com/markets/kxbtcd`

The CLI doesn't generate these, but they're useful for sharing.
