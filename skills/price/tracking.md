# Price Tracking Setup

## Watchlist Management

Items on watchlist tracked continuously:

```
## ~/price/watchlist.md

### Active Watches

| Item | Current | Target | 90-day Low | Platform | Since |
|------|---------|--------|------------|----------|-------|
| Sony WH-1000XM5 | $348 | $299 | $298 | Amazon | 2024-01 |
| Flight LAX→TYO Oct | $1,245 | $900 | $876 | Google Flights | 2024-02 |
```

## Alert Configuration

In `~/price/config.md`:

```
## Alert Preferences

threshold_default: 10%    # Alert when drops 10% from tracked
urgent_deals: true        # Notify immediately for all-time lows
quiet_hours: 22:00-08:00  # No notifications during sleep
digest_time: 09:00        # Daily price summary
platforms:
  - amazon
  - bestbuy
  - google_flights
```

## Price History Format

Store in `~/price/history/[item-slug].md`:

```
## Sony WH-1000XM5 Price History

| Date | Price | Platform | Note |
|------|-------|----------|------|
| 2024-02-14 | $348 | Amazon | Current |
| 2024-02-01 | $328 | Amazon | Presidents Day sale |
| 2024-01-15 | $298 | Best Buy | All-time low |
```

## Data Sources

| Source | Coverage | Update Frequency | Notes |
|--------|----------|------------------|-------|
| CamelCamelCamel | Amazon only | Real-time | Free, reliable |
| Keepa | Amazon | Real-time | Charts, alerts |
| Google Flights | Flights | Continuous | Good for tracking |
| Pricewatch sites | Various | Daily | Aggregators |

## Adding Items to Track

When user says "track this":

1. Identify product (URL, name, or description)
2. Find canonical identifier (ASIN, SKU, model)
3. Check current price across platforms
4. Look up historical data if available
5. Add to watchlist with target (user-specified or suggest based on history)
6. Confirm tracking started

## Alert Triggers

- **Target hit** — Price drops to or below user target
- **All-time low** — New record low price
- **Significant drop** — >15% drop from tracked price
- **Sale detection** — Known sale event starting (Black Friday, Prime Day)
- **Ending soon** — Sale ending within 24h, price still good

## Purchase Decision Logging

After user makes decision, log for learning:

```
## ~/price/purchases.md

| Date | Item | Price | Verdict | Outcome |
|------|------|-------|---------|---------|
| 2024-02-14 | XM5 | $298 | Bought | ✅ Good - still at $348 |
| 2024-02-01 | TV | $899 | Waited | ❌ Went up to $999 |
```

Use history to improve future recommendations.
