# Open Claw Questrade Data Contracts

Use these contracts to keep monitoring snapshots and trade tickets consistent.

## 1) Symbol Set
- Keep symbols uppercase.
- Use comma-separated symbols for script input, example: `AAPL,MSFT,TSLA`.
- Reject empty symbols or unknown side/order fields.

## 2) Questrade CSV Input (`market_snapshot.py --questrade-csv`)
Accept flexible broker-export headers. Supported aliases:

- Symbol: `Symbol`, `Ticker`, `Security`, `Instrument`
- Last: `Last`, `LastPrice`, `Price`, `Mark`
- Bid: `Bid`, `BidPrice`
- Ask: `Ask`, `AskPrice`
- Volume: `Volume`, `Vol`
- Timestamp: `Timestamp`, `Time`, `UpdatedAt`, `Quote_Time`, `Quote Time`

Recommended CSV shape:

```csv
Symbol,Bid,Ask,Last,Volume,Timestamp
AAPL,195.10,195.14,195.12,984322,2026-02-19T15:24:31-05:00
MSFT,421.88,421.95,421.90,612345,2026-02-19T15:24:30-05:00
```

## 3) Snapshot Output JSON (`market_snapshot.py --format json`)
Top-level fields:
- `generated_at_utc`: ISO-8601 timestamp
- `count`: integer symbol count
- `rows`: list of per-symbol objects

Per-symbol fields:
- `symbol`
- `snapshot_time_utc`
- `symbol_status`: `ok`, `missing_yahoo`, `missing_questrade`, `missing_all_sources`
- Yahoo fields: `yahoo_price`, `yahoo_bid`, `yahoo_ask`, `yahoo_volume`, `yahoo_market_state`, `yahoo_exchange`, `yahoo_market_time_utc`
- Questrade fields: `questrade_last`, `questrade_bid`, `questrade_ask`, `questrade_volume`, `questrade_timestamp`
- Comparison fields: `price_delta_qt_minus_yahoo`, `price_delta_pct`

## 4) Snapshot Output CSV (`market_snapshot.py --format csv`)
Use this exact column order:

1. `symbol`
2. `snapshot_time_utc`
3. `symbol_status`
4. `yahoo_price`
5. `yahoo_bid`
6. `yahoo_ask`
7. `yahoo_volume`
8. `yahoo_market_state`
9. `yahoo_exchange`
10. `yahoo_market_time_utc`
11. `questrade_last`
12. `questrade_bid`
13. `questrade_ask`
14. `questrade_volume`
15. `questrade_timestamp`
16. `price_delta_qt_minus_yahoo`
17. `price_delta_pct`

## 5) Trade Checklist Input (`build_trade_checklist.py`)
Required:
- `--account-id`
- `--symbol`
- `--side` (`buy` or `sell`)
- `--quantity` (integer > 0)
- `--order-type` (`market`, `limit`, `stop`, `stop_limit`)
- `--policy-ack OPENCLAW_POLICY_ACK`
- `--confirm-user-authorized`
- `--confirm-manual-execution`
- `--confirm-no-secrets-shared`
- `--out`

Conditional:
- `--limit-price` required for `limit` and `stop_limit`
- `--stop-price` required for `stop` and `stop_limit`
- `--risk-cap-usd` required in `--environment live`
- `--data-age-seconds` required in `--environment live`
- `--allow-market-order-live` required for `--order-type market` in `--environment live`
- `--local-sensitive-storage-confirm` required with `--include-sensitive`

Optional:
- `--environment` (`paper`, `live`; default `live`)
- `--tif` (`day`, `gtc`, `gted`)
- `--max-data-age-seconds` (default `300`)
- `--observed-price-drift-pct`
- `--max-price-drift-pct` (default `1.0`)
- `--notes`

## 6) Trade Checklist Output
Markdown file with:
- Human-readable ticket summary
- Pre-trade hard checks
- Browser submission checklist
- Post-submission log placeholders
- Embedded JSON ticket payload

Privacy defaults:
- `account_id` is masked by default.
- Raw account identifier is included only when `--include-sensitive` is passed intentionally.

Special safety output:
- Includes `special_safety_check` block with pass-state details and thresholds used.
