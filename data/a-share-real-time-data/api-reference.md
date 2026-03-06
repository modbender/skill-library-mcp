# Mootdx API Reference — Detailed

## Time Calculation Logic

### 1-Minute Bar Start Position Calculation

When fetching 1-minute bars for a **specific historical datetime**, the `start` parameter must be calculated as the total number of trading minutes between "now" and the target datetime.

#### Algorithm

```
total_offset = today_minutes + middle_trading_days * 240 + target_day_minutes
```

Where:
- **today_minutes**: Trading minutes elapsed today
  - If today is NOT a trading day: `0`
  - If before 09:30: `0`
  - If between 09:30-11:30: `current_time - 09:30` (in minutes)
  - If between 11:30-13:00: `120` (full morning session)
  - If between 13:00-15:00: `120 + (current_time - 13:00)`
  - If after 15:00: `240` (full day)

- **middle_trading_days**: Number of complete trading days between target date and today (exclusive of both endpoints)

- **target_day_minutes**: Minutes from target time to 15:00 close on the target date
  - Calculated using `_calculate_minutes_to_market_close(target_time)`
  - Accounts for morning session (09:30-11:30) and afternoon session (13:00-15:00) separately
  - Lunch break (11:30-13:00) is excluded from the count

#### Intraday Minute Calculation

To calculate trading minutes between two times on the same day:

```python
def calculate_intraday_minutes(start_time, end_time):
    """
    Trading sessions:
      Morning:   09:30 - 11:30
      Afternoon: 13:00 - 15:00
    Lunch break (11:30-13:00) is excluded.
    """
    total = 0
    # Morning overlap
    morning_start = max(start_time, time(9, 30))
    morning_end = min(end_time, time(11, 30))
    if morning_end > morning_start:
        total += (morning_end - morning_start) in minutes

    # Afternoon overlap
    afternoon_start = max(start_time, time(13, 0))
    afternoon_end = min(end_time, time(15, 0))
    if afternoon_end > afternoon_start:
        total += (afternoon_end - afternoon_start) in minutes

    return total
```

### Daily Bar Start Position Calculation

For daily bars, `start` is the index in the most-recent-first list of trading days:
- Today → `start = 0`
- Previous trading day → `start = 1`
- N trading days ago → `start = N`

Uses the trading calendar to skip weekends/holidays.

### Time Filtering Behavior

When both `date` and `time` are provided to `get_bars()`:

1. **Trading day + valid time** → Filter to the bar closest to the specified time
2. **Non-trading day** → Return the closing bar (15:00) of the nearest prior trading day
3. **Future date** → Return the closing bar of the most recent trading day
4. **Today + before market open** → Return latest available data (start=0)

The `filter_by_time` parameter controls whether time filtering is applied:
- `True` (default): Returns the single bar closest to the specified time
- `False`: Returns all fetched bars without filtering (useful for batch operations)

---

## Complete Method Signatures

### `get_bars()`

```python
async def get_bars(
    stock_code: str,           # "000001.SZ" format
    frequency: int = 7,        # 4=daily, 7=1min, 8=1min, 9=daily
    offset: int = 240,         # Number of bars
    date: Optional[str] = None,     # "YYYYMMDD" or None for latest
    time: Optional[str] = None,     # "HH:MM:SS" or "HH:MM" or None
    filter_by_time: bool = True     # Filter results to nearest bar
) -> List[Dict[str, Any]]
```

### `get_realtime_quote()`

```python
async def get_realtime_quote(
    stock_code: str            # "000001.SZ" — SH/SZ only, no BJ
) -> Dict[str, Any]
```

Returns empty dict `{}` for unsupported exchanges (BJ) or errors.

### `get_realtime_quotes()`

```python
async def get_realtime_quotes(
    stock_codes: List[str]     # ["000001.SZ", "600300.SH"]
) -> List[Dict[str, Any]]
```

Uses native mootdx batch capability. BJ stocks are silently skipped.

### `get_batch_bars()`

```python
async def get_batch_bars(
    stock_codes: List[str],
    date: Optional[str] = None,
    time: Optional[str] = None,
    max_concurrent: int = 10   # Concurrency limit via asyncio.Semaphore
) -> Dict[str, List[Dict[str, Any]]]
```

Internally calls `get_bars()` per stock with `filter_by_time=False`.

### `get_batch_realtime_quotes()`

```python
async def get_batch_realtime_quotes(
    stock_codes: List[str],
    max_concurrent: int = 20   # Deprecated, kept for compatibility
) -> Dict[str, Dict[str, Any]]
```

Delegates to `get_realtime_quotes()`. Returns `{stock_code: quote_data}`.

### `get_transactions_history()`

```python
async def get_transactions_history(
    stock_code: str,
    date: str,                 # Required: "YYYYMMDD"
    start: int = 0,
    offset: int = 1000
) -> List[Dict[str, Any]]
```

### `get_transactions_realtime()`

```python
async def get_transactions_realtime(
    stock_code: str,
    start: int = 0,
    offset: int = 1000
) -> List[Dict[str, Any]]
```

### `get_transactions_with_fallback()`

```python
async def get_transactions_with_fallback(
    stock_code: str,
    start: int = 0,
    offset: int = 1000,
    use_history_fallback: bool = True   # Try history if realtime is empty
) -> List[Dict[str, Any]]
```

---

## Market Detection

Stock codes are auto-detected to their exchange:

| Prefix | Exchange |
|--------|----------|
| `000`, `001`, `002`, `003`, `300` | Shenzhen (SZ) |
| `600`, `601`, `603`, `605`, `688` | Shanghai (SH) |
| Other | Default to Shenzhen |

---

## Rate Limiting

Default rate limit: **0.005 seconds** between API calls (200 calls/sec theoretical max).

The `BaseDataSource` parent class provides `_rate_limit_wait()` for automatic throttling. Some methods (like `get_bars`) have rate limiting commented out for performance — re-enable if experiencing connection drops.

---

## Error Handling

All methods follow the pattern:
1. Try the operation
2. On failure, call `_handle_error(exception, context_message)` which logs and returns empty results (`[]` or `{}`)
3. Never raise exceptions to callers — always return empty data on failure

This design ensures batch operations continue even if individual stock queries fail.
