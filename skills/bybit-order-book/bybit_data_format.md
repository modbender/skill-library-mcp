# ByBit Order Book Data Reference

## Data Sources

**Order book snapshots** are only available from the JavaScript-rendered page:
```
https://www.bybit.com/derivatives/en/history-data
```

**Trade data** (not order book) is available from the open file server:
```
https://public.bybit.com/trading/{SYMBOL}/{SYMBOL}{YYYY-MM-DD}.csv.gz
```

## Download Constraints

- Max **7 calendar days** per download request
- Max **5 symbols** selected simultaneously
- Page uses **Cloudflare protection** — requires undetected-chromedriver or similar
- No authentication required

## Raw File Format

Filename pattern: `{YYYY-MM-DD}_{SYMBOL}_ob500.data.zip`

Inside each ZIP: a single `.data` file in **JSONL format** (one JSON object per line).

### JSONL Schema

```json
{
  "topic": "orderbook.500.BTCUSDT",
  "type": "snapshot",
  "ts": 1725321601755,
  "data": {
    "s": "BTCUSDT",
    "b": [["59116.70", "9.490"], ...],
    "a": [["59116.80", "6.618"], ...],
    "u": 28259371,
    "seq": 231805146756
  },
  "cts": 1725321601749
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `ts` | int | System timestamp (ms epoch) |
| `cts` | int | Matching engine timestamp (ms epoch, more accurate) |
| `data.s` | str | Symbol |
| `data.b` | array | Bids, descending by price. Each: `["price", "size"]` |
| `data.a` | array | Asks, ascending by price. Each: `["price", "size"]` |
| `data.u` | int | Update ID |
| `data.seq` | int | Cross-sequence number |

### Important Notes

- Prices and sizes are **strings** — convert with `float()` or `Decimal()`
- Snapshots at ~**100ms** intervals (~860,000/day)
- Bids sorted **descending** (index 0 = best bid)
- Asks sorted **ascending** (index 0 = best ask)
- `cts` is preferred for time-series alignment

## Storage Estimates

| Depth | Per Day (compressed) | Per Day (Parquet) | Per Month |
|-------|---------------------|-------------------|-----------|
| 500 (raw) | ~1 GB | ~3 GB | ~30 GB |
| 50 (filtered) | N/A | ~300 MB | ~9 GB |
| 50 @ 1s sample | N/A | ~5 MB | ~150 MB |

## Processed Parquet Schema

After `process_orderbook.py`, columns include:

- `timestamp`, `cts`, `symbol`
- `bid_price_0` through `bid_price_49`, `bid_size_0` through `bid_size_49`
- `ask_price_0` through `ask_price_49`, `ask_size_0` through `ask_size_49`
- `best_bid`, `best_ask`, `mid_price`, `spread`, `spread_bps`
- `total_bid_volume`, `total_ask_volume`, `volume_imbalance`
- `microprice`
