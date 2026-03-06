---
name: mootdx-china-stock-data
description: Fetch China A-share stock market data (bars, realtime quotes, tick-by-tick transactions) via mootdx/TDX protocol. Use when working with Chinese stock data, mootdx library, TDX quotes, intraday minute bars, transaction history, or real-time A-share market data.
---

# Mootdx China A-Share Stock Data Client

A wrapper around the `mootdx` library (TDX protocol) for fetching China A-share market data including K-line bars, real-time quotes, and tick-by-tick transaction records.

## Installation

```bash
pip install mootdx
```

> `mootdx` depends on `tdxpy` internally. Both are installed together.

### Verify & Demo

```bash
python scripts/setup_and_verify.py           # Install + verify + connectivity test
python scripts/setup_and_verify.py --check   # Verify only (skip install)
python scripts/setup_and_verify.py --demo    # Full API demo with real output
```

The `--demo` mode exercises every major API and prints real data — useful as a runnable reference for correct calling patterns.

## Critical: Time & Timezone Considerations

### Trading Hours (Beijing Time, UTC+8)

| Session | Time |
|---------|------|
| Morning | 09:30 - 11:30 (120 min) |
| Lunch break | 11:30 - 13:00 |
| Afternoon | 13:00 - 15:00 (120 min) |
| **Total** | **240 trading minutes/day** |

### Trading Time Bypass Patch

**Problem**: `mootdx` / `tdxpy` has a built-in `time_frame()` check that blocks API calls outside trading hours. On servers with non-Beijing timezone, this breaks even during valid trading hours.

**Solution**: Monkey-patch `tdxpy.hq.time_frame` to always return `True`:

```python
import tdxpy.hq
tdxpy.hq.time_frame = lambda: True
```

This patch is applied automatically during `MootdxClient.__init__()`. Without it, `transactions()` and `transaction()` calls will silently return empty results outside detected trading hours.

### Trading Calendar

When querying historical data, always check if a date is a trading day. Non-trading days (weekends, holidays) have no data. The client uses `TradingCalendarStrategy.is_trading_day(date_str)` for this — you must have a trading calendar service available.

### Date/Time Parameter Formats

| Parameter | Format | Example |
|-----------|--------|---------|
| `date` | `YYYYMMDD` | `"20250210"` |
| `time` | `HH:MM:SS` or `HH:MM` | `"10:30:00"` or `"10:30"` |

## Stock Code Format

mootdx uses **pure numeric codes** (TDX format). Convert from standard format:

| Standard Format | TDX Format | Market |
|----------------|------------|--------|
| `000001.SZ` | `000001` | Shenzhen |
| `600300.SH` | `600300` | Shanghai |
| `300750.SZ` | `300750` | Shenzhen (ChiNext) |
| `688001.SH` | `688001` | Shanghai (STAR) |

**Conversion**: Strip the `.SH` / `.SZ` / `.BJ` suffix.

> **Important**: mootdx does NOT support Beijing Stock Exchange (`.BJ`) stocks. Filter them out before calling.

## API Reference

### 1. Initialize Client

```python
from mootdx.quotes import Quotes
client = Quotes.factory(market='std')
```

### 2. `get_bars()` — K-Line / Candlestick Data

Fetch historical or real-time K-line bars.

```python
await client.get_bars(
    stock_code="000001.SZ",   # Standard format (auto-converted)
    frequency=7,               # K-line period (see table below)
    offset=240,                # Number of bars to fetch
    date="20250210",           # Optional: specific date (YYYYMMDD)
    time="10:30:00",           # Optional: specific time (HH:MM:SS)
    filter_by_time=True        # Filter to closest bar matching time
)
```

**Frequency codes:**

| Code | Period |
|------|--------|
| 7 | 1-minute bars |
| 8 | 1-minute bars (alternative) |
| 4 | Daily bars |
| 9 | Daily bars (alternative) |

**Return format** (list of dicts):

```python
{
    "stock_code": "000001.SZ",
    "datetime": "2025-02-10 10:30:00",
    "open": 12.50,
    "high": 12.65,
    "low": 12.45,
    "close": 12.60,
    "vol": 150000.0,
    "amount": 1890000.0
}
```

**Start position calculation**: For historical dates, the `start` parameter is calculated as the number of trading minutes (for 1-min bars) or trading days (for daily bars) between now and the target datetime. This accounts for:
- Whether today is a trading day
- Current trading session status (pre-market / in-session / post-market)
- Lunch break gap (11:30-13:00)

### 3. `get_realtime_quote()` — Single Stock Real-Time Quote

```python
await client.get_realtime_quote(stock_code="000001.SZ")
```

**Returns** (dict): Price, OHLC, volume, amount, and full Level-2 order book (5-level bid/ask):

```python
{
    "stock_code": "000001.SZ",
    "price": 12.60,
    "last_close": 12.50,
    "open": 12.45, "high": 12.65, "low": 12.40,
    "volume": 5000000, "amount": 63000000,
    "bid1": 12.59, "bid2": 12.58, ..., "bid5": 12.55,
    "ask1": 12.60, "ask2": 12.61, ..., "ask5": 12.65,
    "bid_vol1": 500, ..., "ask_vol5": 300,
    "pct_chg": 0.8
}
```

### 4. `get_realtime_quotes()` — Batch Real-Time Quotes

Native batch interface — much faster than looping `get_realtime_quote()`.

```python
await client.get_realtime_quotes(["000001.SZ", "600300.SH", "300750.SZ"])
```

**Returns** (list of dicts):

```python
{
    "stock_code": "000001.SZ",
    "trade_date": "2025-02-10",
    "open": 12.45, "high": 12.65, "low": 12.40, "close": 12.60,
    "pre_close": 12.50,
    "change": 0.15,
    "pct_chg": 1.2048,
    "vol": 5000000.0,
    "amount": 63000000.0,
    "is_realtime": true
}
```

> `pct_chg` is calculated from **today's open price**, not previous close.

### 5. `get_batch_bars()` — Batch K-Line Data

Parallel fetch K-line bars for multiple stocks with concurrency control.

```python
await client.get_batch_bars(
    stock_codes=["000001.SZ", "600300.SH"],
    date="20250210",
    time="10:30:00",
    max_concurrent=10
)
```

**Returns**: `Dict[str, List[Dict]]` — `{stock_code: [bar_data, ...]}`

### 6. `get_transactions_history()` — Historical Tick Data

Tick-by-tick transaction records for a specific historical date.

```python
await client.get_transactions_history(
    stock_code="000001.SZ",
    date="20250210",         # Required: YYYYMMDD
    start=0,
    offset=1000
)
```

**Returns** (list of dicts):

```python
{
    "stock_code": "000001.SZ",
    "time": "09:30:05",
    "price": 12.50,
    "vol": 100,
    "buyorsell": 0,          # 0=buy, 1=sell, 2=neutral
    "num": 5,                # Number of trades in this tick
    "volume": 100
}
```

### 7. `get_transactions_realtime()` — Real-Time Tick Data

Today's live tick-by-tick transaction stream.

```python
await client.get_transactions_realtime(
    stock_code="000001.SZ",
    start=0,
    offset=1000
)
```

Same return format as `get_transactions_history()`.

### 8. `get_transactions_with_fallback()` — Tick Data with Fallback

Tries real-time first, falls back to today's historical data if empty.

```python
await client.get_transactions_with_fallback(
    stock_code="000001.SZ",
    start=0, offset=1000,
    use_history_fallback=True
)
```

## Raw mootdx API (Low-Level)

If using `mootdx` directly without the wrapper:

```python
from mootdx.quotes import Quotes

client = Quotes.factory(market='std')

# K-line bars
df = client.bars(symbol="000001", frequency=7, start=0, offset=240)

# Real-time quotes (supports list of symbols for batch)
df = client.quotes(symbol="000001")
df = client.quotes(symbol=["000001", "600300"])

# Historical transactions
df = client.transactions(symbol="000001", start=0, offset=1000, date="20250210")

# Real-time transactions
df = client.transaction(symbol="000001", start=0, offset=1000)
```

> All raw APIs return **pandas DataFrames**.

## Common Pitfalls

1. **Empty results outside trading hours**: Apply the `time_frame` patch (see above)
2. **Beijing Exchange stocks**: `.BJ` codes are NOT supported — always filter them out
3. **Rate limiting**: Default rate limit is 0.005s between calls; adjust if connection drops
4. **Weekend/holiday queries**: Always validate against trading calendar before querying
5. **1-min bar offset calculation**: Must account for 240 trading minutes/day with lunch gap

## Additional Resources

- For detailed method signatures and time calculation logic, see [api-reference.md](api-reference.md)
