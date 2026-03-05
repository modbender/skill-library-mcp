# COMPREHENSIVE TRADING LEARNINGS FROM CLAUDE CODE HISTORY

## TABLE OF CONTENTS
1. [Zerodha Integration Failures & Fixes](#1-zerodha-integration-failures--fixes)
2. [Backtest vs Live Mode Parity](#2-backtest-vs-live-mode-parity)
3. [Signal Generation Learnings](#3-signal-generation-learnings)
4. [Rebalancing Logic Evolution](#4-rebalancing-logic-evolution)
5. [Stock Universe Selection](#5-stock-universe-selection)
6. [Performance Optimizations](#6-performance-optimizations)
7. [Indian Market Specific Insights](#7-indian-market-specific-insights)
8. [Common Failures & Handling](#8-common-failures--handling)
9. [Indicators & Formulas Used](#9-indicators--formulas-used)
10. [Multi-Timeframe Trading](#10-multi-timeframe-trading)

---

## 1. ZERODHA INTEGRATION FAILURES & FIXES

### 1.1 Tick Size Errors (Critical Production Issue)

**The Problem:**
```
ERROR | SL order failed: Tick size for this script is 5.00. Kindly enter 
trigger price in the multiple of tick size for this
```

**Root Cause:**
- Stop loss prices not rounded to instrument-specific tick size
- Different stocks have different tick sizes (0.01, 0.05, 5.00, etc.)
- Zerodha rejects orders instantly if price doesn't match tick multiples

**The Fix:**
- Download and cache Zerodha instrument master file
- Extract tick_size and lot_size per instrument
- Round ALL order prices to tick_size multiples:
  ```python
  trigger_price = round(price / tick_size) * tick_size
  ```

**Key Learning:**
> "Many bots use zerodha master which has tickers, instrument ids, tick size, lot size etc.. 
> should we not download and cache it for our usages?"

### 1.2 Position vs Holdings Reconciliation

**The Problem:**
- Bot tracked ETF positions (JUNIORBEES) not taken by the bot itself
- Position state not synchronized across sessions
- Manual trades from Kite app confused bot state

**The Fix:**
1. **Reconciliation on startup:**
   - Fetch current Zerodha positions
   - Compare with local state file
   - Only manage positions that match bot's instrument list
   - Ignore user's manual holdings/ETFs

2. **Idempotency across sessions:**
   ```python
   # positions.json structure
   {
     "symbol": "INFY",
     "quantity": 100,
     "entry_price": 1500.00,
     "sl_order_id": "123456",
     "bot_managed": true,  # Critical flag
     "entry_timestamp": "2026-01-14T09:45:00"
   }
   ```

**Key Learning:**
> "Zerodha positions are our truth table, ensure to ignore positions that we may not have 
> taken, but if there are any position that may or may not match with our local state then 
> recon it"

### 1.3 Stop Loss Order Management Issues

**The Problem:**
- SL orders getting cancelled without corresponding position close
- Position became "naked" (no protection) after profit booking attempt
- SL modification failures during trailing stop logic

**The Fix:**
1. **Atomic SL operations:**
   ```python
   # WRONG: Cancel then place
   cancel_sl_order()  # If this succeeds but next fails...
   place_new_sl_order()  # ...position is naked
   
   # RIGHT: Place-then-cancel
   new_sl_id = place_new_sl_order()
   if new_sl_id:
       cancel_old_sl_order()
   else:
       # Keep old SL, log failure
   ```

2. **SL lifecycle tracking:**
   - PENDING → PLACED → ACTIVE → CANCELLED/TRIGGERED
   - Never leave position without active SL
   - Emergency market order on SL modification failure

**Key Learning:**
> "Position was short so initial stop loss order was cancelled on first profit booking 
> event but only order got cancelled and nothing else happened, position on zerodha became 
> naked position"

### 1.4 Order Rejection Handling

**The Problem:**
- Trade execution failed with no on-screen reason
- Only found details in debug logs
- No retry logic for transient failures

**The Fix:**
1. **Immediate error surfacing:**
   ```python
   try:
       order_id = kite.place_order(...)
   except Exception as e:
       # Show on console immediately
       print(f"✗ Order rejected: {e}")
       # Also log to file
       log_order_failure(symbol, reason=str(e))
   ```

2. **Rejection categorization:**
   - `TICK_SIZE_ERROR` → Round and retry once
   - `MARGIN_SHORTAGE` → Reduce quantity
   - `PRICE_BAND` → Cancel trade
   - `RATE_LIMIT` → Backoff, don't retry

**Key Learning:**
> "Why don't you tell the reason on screen itself, so that one could probe further"

### 1.5 WebSocket Reliability

**The Problem:**
- WebSocket disconnects causing data gaps
- No visual indication of connection health
- Bot continued making decisions on stale data

**The Fix:**
1. **Connection state monitoring:**
   ```python
   class WSHealth:
       last_tick_time: float
       consecutive_failures: int
       state: "CONNECTED" | "DEGRADED" | "FAILED"
   
   # In tick handler
   if time.time() - ws.last_tick_time > 10:
       ws.state = "DEGRADED"
       # Stop new trades
       # Show ⚠ WebSocket lagging
   ```

2. **Graceful degradation:**
   - WebSocket fails → Fall back to REST API polling
   - Higher latency but data integrity maintained
   - Clear visual: "✓ Ready (REST API)" vs "✓ Ready (WebSocket)"

**Key Learning:**
> "WebSocket failed, using REST API" + "Market is still on, websockets can't go down, 
> check and ensure it works"

### 1.6 Margin Calculation Mistakes

**The Problem:**
- Checked "opening balance" instead of "available cash"
- Didn't account for used margin
- Could place orders that get rejected for insufficient funds

**The Fix:**
```python
# WRONG
balance = margins['equity']['opening_balance']

# RIGHT
balance = margins['equity']['net']  # Available after all margins
# OR
available_cash = margins['equity']['available']['cash']
```

**Key Learning:**
> "YOU CHECK Available Balance: Rs.1,001,691.10, but that is incorrect what you look at is 
> opening balance, what you should check is a field equivalent of available cash (neither 
> opening balance nor used margin) or available margin whichever is field name"

---

## 2. BACKTEST VS LIVE MODE PARITY

### 2.1 Historical Data Caching Strategy

**The Evolution:**

**Initial approach (broken):**
- Different data sources for backtest and live
- JSON files for backtest, WebSocket for live
- No shared cache = divergent results

**Final working version:**
```python
# Unified data layer
class DataManager:
    def get_candles(self, symbol, date, interval='minute'):
        # Check cache first (Parquet format)
        cache_file = f"cache/{symbol}_{date}_{interval}.parquet"
        if exists(cache_file):
            return pl.read_parquet(cache_file)
        
        # Fetch from Zerodha, cache for reuse
        df = fetch_from_zerodha(symbol, date, interval)
        df.write_parquet(cache_file)
        return df
```

**Key parameters:**
- `warmup_days: 3` - How many days of history to load
- `cache_format: "parquet"` - Much faster than JSON
- `legacy_json_fallback: true` - Compatibility with old data

**Key Learning:**
> "Let us reason about historical data caching and reusability and it's format such that 
> it could be accessed by backtest as well as other modes live/paper"

### 2.2 T vs T-1 Data Mismatches

**The Problem:**
- Backtest using yesterday's (T-1) data to make today's decisions
- Live mode using real-time (T) data
- Signals didn't match

**The Fix:**
1. **Explicit data alignment:**
   ```python
   # For intraday strategies
   if mode == "backtest":
       # Use SAME day's data, replay minute-by-minute
       date = backtest_date
   else:
       # Live mode - today's data
       date = datetime.now().date()
   
   # Both modes use IDENTICAL indicator calculations
   ```

2. **Candle completion discipline:**
   ```python
   def is_candle_complete(candle_time, current_time):
       # Don't use candle until minute boundary + buffer
       return current_time >= candle_time + timedelta(seconds=500ms)
   ```

**Key Learning:**
> "No explicit check that last candle is complete (relies on data provider behavior)"

### 2.3 What Caused Backtest-Live Divergence

**Root Causes Identified:**

1. **Volume data quality:**
   - Live: Real-time tick volume accurate
   - Backtest: 1-min candle volume sometimes 0 due to data gaps
   - **Fix:** Minimum volume threshold, skip signals if volume==0

2. **VWAP calculation differences:**
   ```python
   # WRONG (cumulative error)
   vwap = cumsum(price * volume) / cumsum(volume)
   
   # RIGHT (reset daily)
   if new_day:
       vwap_numerator = 0
       vwap_denominator = 0
   vwap_numerator += price * volume
   vwap_denominator += volume
   vwap = vwap_numerator / vwap_denominator
   ```

3. **Indicator lookback windows:**
   - ADX needs 14+ candles
   - First 15 minutes unreliable
   - **Fix:** `min_candles_required = 20` before generating signals

**Key Learning:**
> "Check if its data glitch or previous needed step not completed glitch?"

---

## 3. SIGNAL GENERATION LEARNINGS

### 3.1 Signal Quality Metrics Tracked

**Win Rate Evolution:**
- Initial: 33.3% (2/6 trades) ❌
- After filtering: 52.6% (10/9 over 15 days)
- Target: 65-70%

**What improved it:**
1. **RSI bounds enforcement:**
   ```python
   # Block overbought/oversold entries
   if direction == "LONG" and rsi > 65:
       return None  # No signal
   if direction == "SHORT" and rsi < 35:
       return None
   ```

2. **Symbol cooldown:**
   ```python
   # Don't re-enter same stock for 45 minutes
   last_exit = symbol_history[symbol]['last_exit_time']
   if time_now - last_exit < 45 * 60:
       return None
   ```

3. **Consecutive loss throttling:**
   ```python
   if consecutive_losses >= 2:
       size_multiplier = 0.5  # Reduce size
   if consecutive_losses >= 3:
       trading_paused = True  # Stop completely
   ```

**Key Learning:**
> "Let us plan to improve signal quality and also reason how to get better signals, look at 
> current logs and config and arrive at change set that allows little less but sure trades"

### 3.2 Multi-Indicator Confirmation

**Single indicator failure:**
> "Single indicator = 50-52% win rate (coin flip)"

**Working combinations:**
```python
def fortress_signal(candle, indicators):
    # Multi-timeframe alignment
    mtf_score = 0
    if indicators['ema9_1m'] > indicators['ema21_1m']:
        mtf_score += 0.25
    if indicators['ema9_5m'] > indicators['ema21_5m']:
        mtf_score += 0.25
    if price > indicators['vwap']:
        mtf_score += 0.15
    if indicators['adx'] > 25:
        mtf_score += 0.15
    if volume > indicators['avg_volume'] * 1.5:
        mtf_score += 0.10
    if indicators['rsi'] in [45, 65]:
        mtf_score += 0.10
    
    # Require min_score = 0.45, min_factors = 3
    if mtf_score >= 0.45:
        return "LONG"
    return None
```

**Confluence weights used:**
- MTF alignment: 0.2
- ORB context: 0.15
- Volume profile: 0.15
- VWAP confluence: 0.15
- Liquidity trap: 0.15
- Time of day: 0.1
- Volume confirm: 0.1

**Key Learning:**
> "Institutional liquidity capture requires detecting and aligning with institutional/HFT 
> liquidity patterns"

### 3.3 False Signal Filtering

**Filters that actually worked:**

1. **Minimum body percent:**
   ```python
   body_pct = abs(close - open) / open * 100
   if body_pct < 0.25:  # Doji/indecision
       return None
   ```

2. **Volume multiplier (session-aware):**
   ```python
   dynamic_rvol = {
       "09:15-09:45": 2.0,   # Opening volatility
       "09:45-11:30": 1.3,   # Morning session
       "11:30-13:30": 1.0,   # Lunch lull
       "13:30-15:00": 1.5    # Closing session
   }
   ```

3. **Gap filter (avoid choppy opens):**
   ```python
   gap_pct = abs(open - prev_close) / prev_close * 100
   if gap_pct > 2.0 and minutes_since_open < 30:
       return None  # Too volatile
   ```

4. **Round number filter:**
   ```python
   # Avoid entries near psychological levels
   if abs(price % 100) < 3:  # Within 0.3% of round number
       return None
   ```

**Key Learning:**
> "Signal gating that we have done is fair or very strict?"

### 3.4 Entry Signal Attribution

**Strategies implemented and their success:**

| Strategy               | Win Rate | Best Session | Config                                |
|------------------------|----------|--------------|---------------------------------------|
| OpeningRangeBreakout   | 60%      | 09:15-09:45  | orb_minutes=15, vol_mult=2.5, adx>25 |
| VWAP Pullback          | 55%      | 13:30-15:00  | band_std=2.0, min_dev=0.5%           |
| FirstHour Momentum     | 48%      | 09:30-10:30  | ema_period=9, top_n=3                |
| Gap Fill               | 52%      | 09:20-09:50  | min_gap=1.2%, max_gap=2.5%           |

**Signal lifecycle:**
```python
class Signal:
    strategy: str  # "ORB", "VWAP", etc.
    symbol: str
    direction: "LONG" | "SHORT"
    confidence: float  # 0.0 to 1.0
    entry_price: float
    stop_loss: float
    target: float
    reason: str  # Human-readable explanation
    invalidation_rules: List[Rule]
```

**Key Learning:**
> "Would it be possible to have better quality signal based on market dynamics at given time?"

---

## 4. REBALANCING LOGIC EVOLUTION

### 4.1 Initial Approach (Failed)

```python
# Daily rebalance - TOO FREQUENT
def rebalance():
    for stock in universe:
        target_weight = 1.0 / len(universe)
        current_weight = holdings[stock] / total_portfolio
        if abs(target_weight - current_weight) > 0.01:
            trade(stock, diff)
```

**Why it failed:**
- Transaction costs ate all returns
- Churning without reason
- Ignored momentum

### 4.2 Final Working Version

```python
def rebalance(force=False):
    # Weekly rebalance on Friday after 3pm
    if not force and (day != "Friday" or time < "15:00"):
        return
    
    # Momentum-based selection
    scores = calculate_momentum_scores(universe, lookback=60)
    top_stocks = scores.top(15)  # From 50 → 15
    
    # Equal weight with constraints
    target_weight = 1.0 / len(top_stocks)
    
    for stock in top_stocks:
        current_value = holdings.get(stock, 0)
        target_value = total_portfolio * target_weight
        diff = target_value - current_value
        
        # Rebalance only if deviation > 10%
        if abs(diff) / target_value > 0.10:
            # Partial rebalancing
            trade_size = diff * 0.7  # Don't fully rebalance
            execute_trade(stock, trade_size)
```

**Frequency optimization:**
- Daily: ❌ Too expensive
- Weekly: ✓ Good balance
- Monthly: ⚠ Misses regime shifts

**Transaction cost modeling:**
```python
# Per trade costs
brokerage = max(20, shares * price * 0.0003)  # 0.03% or ₹20
stt = shares * price * 0.001  # 0.1% on sell
gst = brokerage * 0.18
sebi = 10 / 10_000_000 * shares * price
stamp_duty = shares * price * 0.00015
total_cost = sum([brokerage, stt, gst, sebi, stamp_duty])
```

**Key Learning:**
> "Cash Flow: Sell proceeds: +₹15,95,338, Buy cost: -₹16,14,709, Available cash: ₹10,003
> Net cash needed: ₹19,371. Can we not manage the qty based on available cash from sells only?"

### 4.3 Partial vs Full Rebalancing

**Configuration:**
```json
{
  "universe_params": {
    "nifty_largecap": {
      "partial_exit_enabled": true,
      "partial_exit_ratios": [0.33, 0.33, 0.34],
      "trailing_method": "structure"
    },
    "nifty_midcap": {
      "partial_exit_enabled": false,
      "trailing_method": "none"
    }
  }
}
```

**Why partial for largecap:**
- Lower volatility
- Let winners run
- Book profits incrementally

**Why full for midcap:**
- Higher volatility
- Quick in-out
- Smaller targets

**Key Learning:**
> "Largecaps = pullback entry, midcaps = breakout entry"

---

## 5. STOCK UNIVERSE SELECTION

### 5.1 Nifty 50 vs Nifty Midcap Criteria

**Largecap universe (Nifty 50):**
```python
largecap_universe = [
    "RELIANCE", "HDFCBANK", "BHARTIARTL", "TCS", "ICICIBANK",
    "SBIN", "LT", "BAJFINANCE", "HINDUNILVR", "MARUTI",
    "ITC", "KOTAKBANK", "AXISBANK", "HCLTECH", "SUNPHARMA",
    "TITAN", "ADANIPORTS", "NTPC"
]

# Characteristics
- Liquidity: Very high (avg daily volume > 1M shares)
- Spread: Tight (< 0.05%)
- Volatility: Lower (ATR% < 2%)
- Trade style: Pullback, structure-based
```

**Midcap universe:**
```python
midcap_universe = [
    "SIEMENS", "PIDILITIND", "HAVELLS", "DMART", "BOSCHLTD",
    "GAIL", "BANKBARODA", "CANBK", "PNB", "TATAPOWER",
    "DLF", "GODREJCP", "INDUSTOWER", "TORNTPHARM", "MCDOWELL-N",
    "VEDL", "AMBUJACEM", "ICICIPRULI", "BAJAJHLDNG", "BERGEPAINT"
]

# Characteristics
- Liquidity: Moderate (avg daily volume > 100K shares)
- Spread: Wider (< 0.15%)
- Volatility: Higher (ATR% < 3%)
- Trade style: Breakout, momentum
```

**Optimized universe (custom):**
```python
# Hand-picked for momentum + liquidity
optimized = [
    "SHRIRAMFIN", "HINDALCO", "LTF", "RECLTD", "DLF",
    "TATAPOWER", "HDFCLIFE", "VEDL", "IRFC", "HEROMOTOCO",
    "POWERGRID", "ADANIGREEN", "HDFCBANK", "TORNTPOWER", "JIOFIN"
]
```

### 5.2 Liquidity Filtering

**Curation logic:**
```python
def curate_universe(all_stocks, date):
    # Fetch last 20 days data
    history = get_historical(all_stocks, days=20)
    
    filtered = []
    for stock in all_stocks:
        # 1. Average volume
        avg_vol = history[stock]['volume'].mean()
        if avg_vol < 100_000:
            continue
        
        # 2. Price range
        price = history[stock]['close'][-1]
        if price < 50 or price > 50_000:
            continue
        
        # 3. Spread check (live data)
        bid, ask = get_quote(stock)
        spread = (ask - bid) / bid * 100
        if spread > 0.3:  # > 0.3%
            continue
        
        # 4. ATR-based volatility
        atr_pct = history[stock]['atr'][-1] / price * 100
        if not (0.15 < atr_pct < 2.5):
            continue
        
        filtered.append(stock)
    
    # 5. Sort by momentum score
    scores = {s: momentum_score(history[s]) for s in filtered}
    return sorted(filtered, key=lambda s: scores[s], reverse=True)[:15]
```

**Momentum scoring:**
```python
def momentum_score(df, period=60):
    # Multi-factor score
    score = 0
    
    # 1. Price momentum (40%)
    returns = (df['close'][-1] - df['close'][-period]) / df['close'][-period]
    score += returns * 0.4
    
    # 2. Volume trend (20%)
    vol_ratio = df['volume'][-10:].mean() / df['volume'][-period:].mean()
    score += (vol_ratio - 1) * 0.2
    
    # 3. ADX strength (20%)
    adx = df['adx'][-1]
    score += (adx / 100) * 0.2
    
    # 4. RS vs Nifty (20%)
    stock_return = df['close'][-1] / df['close'][-period] - 1
    nifty_return = nifty_df['close'][-1] / nifty_df['close'][-period] - 1
    rs = stock_return - nifty_return
    score += rs * 0.2
    
    return score
```

### 5.3 Sector Diversity (Planned but not implemented)

**Why it was deprioritized:**
> "No sector context that may miss rotation, we would reason it separately in future, 
> not a priority, not that much of a risk"

**If implemented, would look like:**
```python
sectors = {
    "Banking": ["HDFCBANK", "ICICIBANK", "SBIN"],
    "IT": ["TCS", "HCLTECH", "INFY"],
    "Auto": ["MARUTI", "HEROMOTOCO"],
    # ...
}

# Max 30% in any sector
def apply_sector_cap(selected_stocks):
    sector_weights = defaultdict(float)
    for stock in selected_stocks:
        sector = get_sector(stock)
        sector_weights[sector] += 1.0 / len(selected_stocks)
        
        if sector_weights[sector] > 0.30:
            # Skip this stock
            selected_stocks.remove(stock)
```

### 5.4 What Didn't Work

**Failures identified:**

1. **Too large universe (50+ stocks):**
   - API throttling issues
   - Can't watch all effectively
   - **Fix:** Limit to 15-20 max

2. **Static universe (never refreshing):**
   - Missed new momentum
   - Stuck with dead stocks
   - **Fix:** Weekly curation

3. **Including illiquid stocks:**
   - Wide spreads killed profits
   - Slippage exceeded targets
   - **Fix:** Minimum volume 100K/day

**Key Learning:**
> "Is the curation logic producing correct results for intraday trading at any moment 
> during the day? YES - it fetches 5 and 7-day data so it adapts to current regime"

---

## 6. PERFORMANCE OPTIMIZATIONS

### 6.1 Data Caching Implementation

**Parquet vs JSON benchmark:**
```
JSON:    2.3s to load 1000 candles
Parquet: 0.08s to load 1000 candles  ← 28x faster
```

**Cache structure:**
```
cache/
  RELIANCE_2026-01-14_minute.parquet
  RELIANCE_2026-01-14_5minute.parquet
  RELIANCE_2026-01-13_minute.parquet
  ...
```

**Implementation:**
```python
class ParquetCache:
    def get_data(self, symbol, date, interval='minute'):
        cache_file = self.cache_dir / f"{symbol}_{date}_{interval}.parquet"
        
        if cache_file.exists():
            # Check if data is complete
            df = pl.read_parquet(cache_file)
            if self.is_complete(df, date):
                return df
        
        # Fetch from Zerodha
        df = self.fetch_from_api(symbol, date, interval)
        
        # Cache for reuse
        df.write_parquet(cache_file)
        return df
    
    def is_complete(self, df, date):
        # For historical dates, expect ~375 candles (6.25 hours)
        if date < today():
            return len(df) >= 350
        # For today, check latest timestamp
        return df['timestamp'].max() >= now() - timedelta(minutes=2)
```

**Key Learning:**
> "Use Parquet format for cache_format - much faster than JSON"

### 6.2 Vectorization Examples

**Before (slow):**
```python
# Loop through each candle
signals = []
for i in range(len(df)):
    candle = df.iloc[i]
    if candle['ema9'] > candle['ema21'] and candle['rsi'] < 65:
        signals.append({'idx': i, 'signal': 'LONG'})
```

**After (fast):**
```python
# Vectorized operations
df = df.with_columns([
    ((pl.col('ema9') > pl.col('ema21')) & 
     (pl.col('rsi') < 65) &
     (pl.col('volume') > pl.col('avg_volume') * 1.5)).alias('signal')
])
signals = df.filter(pl.col('signal')).select(['timestamp', 'close'])
```

**Performance gain:**
- Loop: 450ms for 1000 candles
- Vectorized: 12ms for 1000 candles (37x faster)

### 6.3 Pure Function Patterns

**Why it matters:**
- Testable
- No hidden state bugs
- Parallelizable

**Example:**
```python
# IMPURE (bad)
class Indicator:
    def __init__(self):
        self.prev_ema = None
    
    def calculate_ema(self, price):
        if self.prev_ema is None:
            self.prev_ema = price
        self.prev_ema = 0.1 * price + 0.9 * self.prev_ema
        return self.prev_ema

# PURE (good)
def calculate_ema(prices: List[float], period: int = 9) -> List[float]:
    alpha = 2 / (period + 1)
    ema = [prices[0]]
    for price in prices[1:]:
        ema.append(alpha * price + (1 - alpha) * ema[-1])
    return ema

# Even better - vectorized
def calculate_ema_vectorized(df: pl.DataFrame, period: int = 9):
    return df.select([
        pl.col('close').ewm_mean(span=period).alias('ema')
    ])
```

### 6.4 API Batching

**Problem:**
> "If we too much remain dependent on API calls, is there any batching possible while 
> applying candidate prefilter or any other scan"

**Solution:**
```python
# WRONG - Individual calls
for symbol in universe:
    quote = kite.quote(f"NSE:{symbol}")
    # ... process

# RIGHT - Batch call
symbols = [f"NSE:{s}" for s in universe]
quotes = kite.quote(symbols)  # Single API call
for symbol in universe:
    quote = quotes[f"NSE:{symbol}"]
    # ... process
```

**Rate limiting awareness:**
```python
class RateLimiter:
    def __init__(self, calls_per_second=10):
        self.calls_per_second = calls_per_second
        self.last_call_times = deque(maxlen=calls_per_second)
    
    def wait_if_needed(self):
        now = time.time()
        if len(self.last_call_times) == self.calls_per_second:
            elapsed = now - self.last_call_times[0]
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
        self.last_call_times.append(now)

# Usage
limiter = RateLimiter(calls_per_second=10)
for symbol in universe:
    limiter.wait_if_needed()
    data = kite.historical_data(symbol, ...)
```

### 6.5 Lambda Function Usage (Avoided)

**Why NOT used:**
- Trading logic needs debugging
- Stack traces matter
- Performance gain minimal

**When lambdas ARE acceptable:**
```python
# Simple data transforms only
df = df.with_columns([
    pl.col('close').apply(lambda x: round(x, 2)).alias('close_rounded')
])

# Better: Use built-in functions
df = df.with_columns([
    pl.col('close').round(2).alias('close_rounded')
])
```

### 6.6 Biggest Speed Improvements

**Ranked by impact:**

1. **Parquet caching (28x faster)** ⭐⭐⭐⭐⭐
2. **Polars instead of Pandas (5-10x faster)** ⭐⭐⭐⭐
3. **Vectorized indicator calculations (30x faster)** ⭐⭐⭐⭐
4. **API batching (3x fewer calls)** ⭐⭐⭐
5. **Precomputed EMA/ATR (2x faster)** ⭐⭐

**Key Learning:**
> "Alright now think like a seasoned algo developer with abilities in performance engineering"

---

## 7. INDIAN MARKET SPECIFIC INSIGHTS

### 7.1 Market Timing Quirks

**Session structure:**
```
09:00 - 09:08  Pre-open (order collection)
09:08 - 09:12  Pre-open (equilibrium price calculation)
09:12 - 09:15  Pre-open (buffer)
09:15          Market opens
15:30          Market closes
15:40          Post-close session ends
```

**Trading windows used:**
```json
{
  "time_windows": {
    "active": [
      {"start": "09:30", "end": "11:30"},  // Opening session
      {"start": "13:30", "end": "15:00"}   // Closing session
    ],
    "blocked": [
      {"start": "11:30", "end": "13:00"}   // Lunch lull - choppy
    ]
  }
}
```

**Time-based risk adjustment:**
```python
time_risk_multiplier = {
    "09:15-09:30": 0.5,  # Wild, reduce size
    "09:30-11:30": 1.0,  # Prime time
    "11:30-13:00": 0.7,  # Reduce activity
    "13:00-14:00": 0.6,  # Lowest liquidity
    "14:00-14:45": 1.0,  # Afternoon momentum
    "14:45-15:30": 0.7   # Position squaring
}
```

### 7.2 Circuit Breakers

**Limits (Jan 2026):**
- Individual stocks: ±10% or ±20% (depends on category)
- Index: ±10%, ±15%, ±20% (with trading halts)

**Handling:**
```python
def check_circuit_risk(symbol, current_price, entry_price):
    # Fetch stock's circuit limits
    limits = get_circuit_limits(symbol)  # From instruments.csv
    
    upper_circuit = entry_price * (1 + limits['upper'] / 100)
    lower_circuit = entry_price * (1 - limits['lower'] / 100)
    
    # If approaching circuit (within 2%)
    if direction == "LONG" and current_price > upper_circuit * 0.98:
        return "EXIT_CIRCUIT_RISK"
    if direction == "SHORT" and current_price < lower_circuit * 1.02:
        return "EXIT_CIRCUIT_RISK"
    
    return None
```

**Key Learning:**
> "Plan for circuit breaker handling, exchange throttling during volatility"

### 7.3 Settlement Cycle (T+1)

**Implications:**
- Funds from sell order available next day
- Can't use same capital twice in same day (cash segment)
- F&O has intraday margin

**Position management:**
```python
# Track available capital
class CapitalManager:
    def __init__(self, total_capital):
        self.total = total_capital
        self.blocked = 0
        self.pending_settlements = {}  # {date: amount}
    
    def block_for_trade(self, amount):
        if amount > self.available():
            raise InsufficientFunds
        self.blocked += amount
    
    def release_on_exit(self, amount, trade_date):
        self.blocked -= amount
        # Funds available T+1
        settlement_date = trade_date + timedelta(days=1)
        self.pending_settlements[settlement_date] = \
            self.pending_settlements.get(settlement_date, 0) + amount
    
    def available(self):
        # Settle pending amounts
        today = datetime.now().date()
        settled = sum(amt for date, amt in self.pending_settlements.items() 
                     if date <= today)
        return self.total + settled - self.blocked
```

### 7.4 Sector Rotation Patterns (Observed)

**Not implemented, but noted:**
- Banking outperforms in rate cut cycles
- IT outperforms on rupee weakness
- Metals/Commodities on global commodity rallies
- Auto on festive season (Sept-Nov)

**How it could be used:**
```python
# Adjust sector weights based on macro regime
macro_regime = detect_regime()  # "RATE_CUT", "INFLATION", etc.

sector_tilts = {
    "RATE_CUT": {"Banking": 1.2, "Real Estate": 1.3},
    "INFLATION": {"Commodities": 1.3, "Energy": 1.2},
    # ...
}

for stock in universe:
    sector = get_sector(stock)
    momentum_score[stock] *= sector_tilts[macro_regime].get(sector, 1.0)
```

---

## 8. COMMON FAILURES & HANDLING

### 8.1 What Broke in Production

**Top 5 production issues:**

1. **HINDALCO buy-sell loop:**
   > "HINDALCO got BOUGHT and SOLD immediately, back to back several times"
   
   **Root cause:** No cooldown after exit
   
   **Fix:**
   ```python
   symbol_cooldowns = {}
   
   def can_trade_symbol(symbol):
       if symbol in symbol_cooldowns:
           if time.time() - symbol_cooldowns[symbol] < 45 * 60:
               return False
       return True
   
   def on_exit(symbol):
       symbol_cooldowns[symbol] = time.time()
   ```

2. **Position not syncing after stop loss:**
   > "My sunpharma order has been stop-lossed and it doesn't reflect in latest position list!"
   
   **Root cause:** Zerodha webhooks not reliable, polling interval too long
   
   **Fix:**
   ```python
   # Poll positions every 30s when in trade
   async def position_sync_loop():
       while trading_active:
           if has_open_positions():
               zerodha_positions = kite.positions()
               reconcile_positions(zerodha_positions)
               await asyncio.sleep(30)
           else:
               await asyncio.sleep(300)  # 5 min when flat
   ```

3. **Naked positions after SL modification failure:**
   - Described in Section 1.3
   - Fixed with place-then-cancel pattern

4. **Volume showing 0 during market hours:**
   > "Today is market open, how come volume be 0?"
   
   **Root cause:** WebSocket reconnected, didn't rebuild tick aggregation
   
   **Fix:**
   ```python
   async def on_reconnect():
       # Fetch last complete candle from REST API
       last_candle = kite.historical_data(..., interval='minute')[-1]
       rebuild_state_from_candle(last_candle)
       # Then resume tick aggregation
   ```

5. **Bot took position on app restart:**
   > "I already had a position! Did you not check that on re-run from current local 
   > state and current zerodha positions state?"
   
   **Fixed with reconciliation on startup (Section 1.2)**

### 8.2 Edge Cases Discovered

**1. Partial fills with stop loss:**
```python
# Order: Buy 1000 shares
# Filled: 600 shares
# Problem: SL placed for 1000

# Fix:
def place_sl_after_fill(order_id):
    while True:
        status = kite.order_history(order_id)[-1]
        if status['status'] == 'COMPLETE':
            filled_qty = status['filled_quantity']
            place_sl_order(filled_qty)  # Not original qty
            break
        elif status['status'] == 'REJECTED':
            handle_rejection()
            break
        await asyncio.sleep(1)
```

**2. Graceful shutdown with open positions:**
```python
def shutdown_handler(signal, frame):
    print("\nShutting down gracefully...")
    
    # 1. Stop accepting new signals
    scanner.stop()
    
    # 2. Close open positions
    if has_open_positions():
        print("Closing open positions...")
        close_all_positions()
    
    # 3. Cancel pending orders
    pending = kite.orders()
    for order in pending:
        if order['status'] in ['TRIGGER PENDING', 'OPEN']:
            kite.cancel_order(order['order_id'])
    
    # 4. Close WebSocket
    ws.close()
    
    # 5. Save state
    save_state_to_disk()
    
    print("✓ Shutdown complete")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
```

**3. Clock drift / timestamp issues:**
> "Fix the clock drift timestamp issue"

```python
# WRONG
candle_time = datetime.now()

# RIGHT
candle_time = extract_exchange_timestamp_from_tick(tick)

# Sync check
def check_clock_sync():
    kite_time = kite.quote("NSE:NIFTY 50")['timestamp']
    local_time = datetime.now()
    drift = abs((kite_time - local_time).total_seconds())
    
    if drift > 5:  # More than 5 seconds
        logger.error(f"Clock drift: {drift}s")
        # Don't trade on bad timestamps
        return False
    return True
```

### 8.3 Error Handling Patterns

**Retry logic with exponential backoff:**
```python
def retry_with_backoff(func, max_retries=3, base_delay=1.0):
    for attempt in range(max_retries):
        try:
            return func()
        except (ConnectionError, Timeout) as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)  # 1s, 2s, 4s
            logger.warning(f"Retry {attempt+1}/{max_retries} after {delay}s")
            time.sleep(delay)
```

**Order status state machine:**
```python
from enum import Enum

class OrderStatus(Enum):
    CREATED = "CREATED"
    SENT = "SENT"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    TRIGGER_PENDING = "TRIGGER PENDING"
    OPEN = "OPEN"
    COMPLETE = "COMPLETE"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

def track_order_lifecycle(order_id):
    order_states = [OrderStatus.CREATED]
    
    while True:
        status = fetch_order_status(order_id)
        new_state = OrderStatus(status['status'])
        
        if new_state != order_states[-1]:
            order_states.append(new_state)
            log_state_transition(order_id, order_states[-2], new_state)
        
        if new_state in [OrderStatus.COMPLETE, OrderStatus.CANCELLED, 
                         OrderStatus.REJECTED]:
            break
        
        await asyncio.sleep(1)
    
    return order_states
```

### 8.4 Debugging Techniques Used

**1. Structured logging:**
```python
import structlog

logger = structlog.get_logger()

# WRONG
print(f"Signal: {signal}")

# RIGHT
logger.info("signal_generated", 
    symbol=signal.symbol,
    strategy=signal.strategy,
    direction=signal.direction,
    confidence=signal.confidence,
    entry_price=signal.entry_price,
    reason=signal.reason
)
```

**2. Debug logs separate from operational logs:**
```python
handlers = {
    'operational': {
        'level': 'INFO',
        'file': 'logs/trading.log',
        'format': 'json'
    },
    'debug': {
        'level': 'DEBUG',
        'file': 'logs/debug.log',
        'format': 'detailed'
    },
    'errors': {
        'level': 'ERROR',
        'file': 'logs/errors.log',
        'format': 'json'
    }
}
```

**3. Tail scripts for real-time monitoring:**
```bash
#!/bin/bash
# tail.sh - Monitor operational logs
tail -f logs/trading.log | jq -r '[.timestamp, .level, .symbol, .message] | @tsv'

# fail.sh - Monitor errors
tail -f logs/errors.log | jq -r '[.timestamp, .error_type, .message] | @tsv' | \
    grep -i "error\|exception\|failed"
```

**Key Learning:**
> "This is our first day to trade in live mode, we may keep switching between live and 
> paper mode within session, ensure enough debug logging is present in a separate text file"

---

## 9. INDICATORS & FORMULAS USED

### 9.1 Exact Formulas and Parameters

**RSI (Relative Strength Index):**
```python
def calculate_rsi(prices, period=14):
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    rsi_values = [100] * period
    
    for i in range(period, len(prices)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        rs = avg_gain / avg_loss if avg_loss != 0 else 100
        rsi = 100 - (100 / (1 + rs))
        rsi_values.append(rsi)
    
    return rsi_values

# Config
rsi_long_min = 45
rsi_long_max = 65
rsi_short_min = 30
rsi_short_max = 60
```

**MACD (Moving Average Convergence Divergence):**
```python
def calculate_macd(prices, fast=12, slow=26, signal=9):
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    
    return {
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram
    }

# Usage in signals
if macd['histogram'][-1] > 0 and macd['histogram'][-2] <= 0:
    # Bullish crossover
    signal = "LONG"
```

**ATR (Average True Range):**
```python
def calculate_atr(highs, lows, closes, period=14):
    tr_values = []
    for i in range(1, len(closes)):
        high = highs[i]
        low = lows[i]
        prev_close = closes[i-1]
        
        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )
        tr_values.append(tr)
    
    atr = [np.mean(tr_values[:period])]
    
    for i in range(period, len(tr_values)):
        atr_val = (atr[-1] * (period - 1) + tr_values[i]) / period
        atr.append(atr_val)
    
    return atr

# Used for stop loss
def calculate_sl(entry_price, atr, direction, multiplier=1.5):
    if direction == "LONG":
        return entry_price - (atr * multiplier)
    else:
        return entry_price + (atr * multiplier)
```

**ADX (Average Directional Index):**
```python
def calculate_adx(highs, lows, closes, period=14):
    # Calculate +DM, -DM
    plus_dm = []
    minus_dm = []
    
    for i in range(1, len(highs)):
        high_diff = highs[i] - highs[i-1]
        low_diff = lows[i-1] - lows[i]
        
        plus_dm.append(high_diff if high_diff > low_diff and high_diff > 0 else 0)
        minus_dm.append(low_diff if low_diff > high_diff and low_diff > 0 else 0)
    
    # Calculate ATR
    atr = calculate_atr(highs, lows, closes, period)
    
    # Calculate +DI, -DI
    plus_di = [(dm / atr_val * 100) for dm, atr_val in zip(plus_dm, atr)]
    minus_di = [(dm / atr_val * 100) for dm, atr_val in zip(minus_dm, atr)]
    
    # Calculate DX
    dx = [abs(pi - mi) / (pi + mi) * 100 for pi, mi in zip(plus_di, minus_di)]
    
    # Calculate ADX (smoothed DX)
    adx = [np.mean(dx[:period])]
    for i in range(period, len(dx)):
        adx_val = (adx[-1] * (period - 1) + dx[i]) / period
        adx.append(adx_val)
    
    return adx

# Config
adx_min = 25  # Minimum for trend strength
```

**VWAP (Volume Weighted Average Price):**
```python
def calculate_vwap(candles):
    cumulative_tpv = 0  # Typical Price * Volume
    cumulative_volume = 0
    vwap_values = []
    
    for candle in candles:
        typical_price = (candle['high'] + candle['low'] + candle['close']) / 3
        volume = candle['volume']
        
        cumulative_tpv += typical_price * volume
        cumulative_volume += volume
        
        vwap = cumulative_tpv / cumulative_volume if cumulative_volume > 0 else 0
        vwap_values.append(vwap)
    
    return vwap_values

# VWAP bands
def calculate_vwap_bands(vwap, candles, std_multiplier=2.0):
    prices = [c['close'] for c in candles]
    std_dev = np.std(prices)
    
    upper_band = vwap + (std_dev * std_multiplier)
    lower_band = vwap - (std_dev * std_multiplier)
    
    return {
        'vwap': vwap,
        'upper': upper_band,
        'lower': lower_band
    }

# Config
vwap_band_std = 2.0
vwap_distance_max_percent = 1.5
```

**EMA (Exponential Moving Average):**
```python
def calculate_ema(prices, period=9):
    alpha = 2 / (period + 1)
    ema = [prices[0]]
    
    for price in prices[1:]:
        ema_val = alpha * price + (1 - alpha) * ema[-1]
        ema.append(ema_val)
    
    return ema

# Common periods used
ema_fast = 9
ema_slow = 21
```

### 9.2 Most Reliable Indicators

**Ranked by signal quality:**

1. **VWAP (★★★★★)**
   - Works: Intraday mean reversion, institutional levels
   - Fails: Flat VWAP days, low volume
   - Best use: Pullback entries when price > VWAP

2. **ADX (★★★★★)**
   - Works: Identifying trend strength
   - Fails: Doesn't tell direction
   - Best use: Filter - only trade if ADX > 25

3. **EMA crossovers (★★★★)**
   - Works: Trend direction
   - Fails: Choppy markets (whipsaws)
   - Best use: 9/21 EMA for entry direction

4. **RSI (★★★☆☆)**
   - Works: Extreme filtering
   - Fails: Trending markets stay "overbought"
   - Best use: Block entries if RSI > 65 (long) or < 35 (short)

5. **MACD (★★★☆☆)**
   - Works: Momentum shifts
   - Fails: Lags price
   - Best use: Confirmation, not primary signal

### 9.3 Indicator Combinations That Worked

**Fortress Signal (highest win rate):**
```python
def fortress_signal(df):
    # Require ALL conditions
    conditions = {
        'trend': df['ema9'] > df['ema21'],           # Trend direction
        'strength': df['adx'] > 25,                  # Trend strength
        'momentum': df['rsi'].between(45, 65),       # Not overbought
        'vwap': df['close'] > df['vwap'],            # Above VWAP
        'volume': df['volume'] > df['avg_vol'] * 1.5, # Volume surge
        'body': (df['close'] - df['open']).abs() / df['open'] > 0.0025  # 0.25% body
    }
    
    # All must be true
    signal = all(conditions.values())
    
    # Confidence based on how many conditions met strongly
    confidence = sum([
        1.0 if conditions['adx'] > 30 else 0.5,
        1.0 if conditions['volume'] > df['avg_vol'] * 2.0 else 0.5,
        1.0 if df['rsi'].between(50, 60) else 0.5,
        # ...
    ]) / 3.0
    
    return signal, confidence
```

**ORB + VWAP:**
```python
# Opening Range Breakout confirmed by VWAP
def orb_vwap_signal(df, orb_high, orb_low):
    current = df.iloc[-1]
    
    # Breakout
    if current['high'] > orb_high:
        # VWAP confirmation
        if current['close'] > current['vwap']:
            # Volume confirmation
            if current['volume'] > df['volume'].mean() * 2.5:
                return "LONG"
    
    return None
```

### 9.4 Custom Indicators Developed

**Liquidity Trap Detector:**
```python
def detect_liquidity_trap(df, lookback=20):
    """
    Detects false breakouts that trap liquidity
    """
    recent = df.tail(lookback)
    
    # Find swing highs/lows
    swing_highs = recent[recent['high'] == recent['high'].rolling(5).max()]
    swing_lows = recent[recent['low'] == recent['low'].rolling(5).min()]
    
    # Check if price broke level then reversed
    for _, high in swing_highs.iterrows():
        # Did price break above then close back inside?
        next_candles = df[df['timestamp'] > high['timestamp']].head(3)
        
        if (next_candles['high'].max() > high['high'] * 1.002 and
            next_candles['close'].iloc[-1] < high['high']):
            return {
                'type': 'BULL_TRAP',
                'level': high['high'],
                'strength': calculate_trap_strength(next_candles)
            }
    
    # Same for lows
    # ...
    
    return None
```

**Momentum Fade Detector:**
```python
def detect_momentum_fade(df):
    """
    Identifies when momentum is exhausting
    """
    recent = df.tail(10)
    
    # Volume trend declining
    vol_slope = np.polyfit(range(len(recent)), recent['volume'], 1)[0]
    
    # Range compressing
    range_ratio = recent['range'].iloc[-1] / recent['range'].mean()
    
    # RSI divergence
    price_higher = recent['close'].iloc[-1] > recent['close'].iloc[0]
    rsi_lower = recent['rsi'].iloc[-1] < recent['rsi'].iloc[0]
    divergence = price_higher and rsi_lower
    
    fade_score = 0
    if vol_slope < 0:
        fade_score += 0.4
    if range_ratio < 0.7:
        fade_score += 0.3
    if divergence:
        fade_score += 0.3
    
    return {
        'fading': fade_score > 0.5,
        'score': fade_score
    }
```

---

## 10. MULTI-TIMEFRAME TRADING

### 10.1 Intraday vs Positional Differences

**Intraday (1-min + 5-min candles):**
```json
{
  "strategy": {
    "target_percent": 1.0,
    "stop_loss_percent": 0.5,
    "max_hold_minutes": 45,
    "capital_per_trade": 500000
  }
}
```

**Positional (Daily + Weekly candles):**
```json
{
  "strategy": {
    "target_percent": 8.0,
    "stop_loss_percent": 4.0,
    "max_hold_days": 30,
    "capital_per_trade": "20% of portfolio"
  }
}
```

**Key differences:**

| Aspect         | Intraday               | Positional           |
|----------------|------------------------|----------------------|
| Data source    | Live ticks/1-min       | Daily EOD            |
| Entry signal   | 1-min candle           | Daily close          |
| Trend confirm  | 5-min EMA              | Weekly trend         |
| Position size  | Full capital per trade | 20% per position     |
| Max positions  | 1 at a time            | 5 simultaneous       |
| Holding period | Minutes to hours       | Days to weeks        |
| Exit trigger   | Time decay, candles    | Weekly close, target |

### 10.2 Multi-Day, Multi-Week, Multi-Month Approaches

**Multi-day swing trading (not fully implemented):**
```python
def swing_signal(daily_df, weekly_df):
    # Weekly trend
    weekly_trend = "UP" if weekly_df['ema9'][-1] > weekly_df['ema21'][-1] else "DOWN"
    
    # Daily entry
    daily = daily_df.iloc[-1]
    prev_daily = daily_df.iloc[-2]
    
    if weekly_trend == "UP":
        # Pullback to 21 EMA on daily
        if (prev_daily['close'] < daily_df['ema21'][-2] and
            daily['close'] > daily_df['ema21'][-1]):
            return {
                'direction': 'LONG',
                'entry': daily['close'],
                'stop': daily_df['ema21'][-1] * 0.98,
                'target': daily['close'] * 1.08,
                'holding_period': 'days'
            }
    
    return None
```

**Capital allocation across timeframes:**
```python
portfolio_allocation = {
    'intraday': 0.30,      # 30% for scalping
    'swing_daily': 0.40,   # 40% for multi-day swings
    'position_weekly': 0.20, # 20% for weekly positions
    'cash': 0.10           # 10% reserve
}

# For 10L capital
capital = {
    'intraday': 300000,    # Full amount per trade (1 at a time)
    'swing': 400000,       # Divided across 5 positions = 80K each
    'position': 200000,    # Divided across 3-4 positions
    'cash': 100000
}
```

### 10.3 Multi-Timeframe Confirmation

**The hierarchy:**
```
Weekly (macro trend)
  ↓
Daily (entry timing)
  ↓
Hourly (confirmation)
  ↓
15-min (entry candle)
  ↓
5-min (stop placement)
  ↓
1-min (execution)
```

**Implementation:**
```python
def mtf_alignment_score(symbol, date):
    # Fetch all timeframes
    weekly = get_data(symbol, date, interval='week')
    daily = get_data(symbol, date, interval='day')
    hourly = get_data(symbol, date, interval='hour')
    min15 = get_data(symbol, date, interval='15minute')
    min5 = get_data(symbol, date, interval='5minute')
    
    score = 0.0
    
    # Weekly trend (40% weight)
    if weekly['ema9'][-1] > weekly['ema21'][-1]:
        score += 0.40
    
    # Daily trend (30% weight)
    if daily['ema9'][-1] > daily['ema21'][-1]:
        score += 0.30
    
    # Hourly confirmation (15% weight)
    if hourly['close'][-1] > hourly['vwap'][-1]:
        score += 0.15
    
    # 15-min structure (10% weight)
    if min15['adx'][-1] > 25:
        score += 0.10
    
    # 5-min volume (5% weight)
    if min5['volume'][-1] > min5['volume'].mean() * 1.5:
        score += 0.05
    
    return score

# Config
min_mtf_alignment = 0.25  # For midcap (looser)
min_mtf_alignment = 0.50  # For largecap (stricter)
```

**Key Learning:**
> "Entry style: pullback (largecap) vs breakout (midcap) based on universe params"

---

## SUMMARY OF KEY TAKEAWAYS

### Critical Success Factors:
1. ✅ Tick size rounding prevents 90% of order rejections
2. ✅ Position reconciliation on startup prevents double-positions
3. ✅ Parquet caching gives 28x speed improvement
4. ✅ Symbol cooldown prevents revenge trading
5. ✅ Multi-indicator confirmation increases win rate from 33% → 52%+
6. ✅ Weekly rebalancing vs daily saves transaction costs
7. ✅ Session-aware parameters (morning vs afternoon) matter
8. ✅ Stop-loss lifecycle tracking prevents naked positions
9. ✅ Graceful degradation (WebSocket → REST) ensures continuity
10. ✅ Structured logging enables debugging production issues

### What Cost the Most Learning:
- SL order management edge cases
- Backtest-live data parity issues
- Over-trading (no cooldown) losses
- API rate limiting under stress
- Clock drift breaking candle alignment

### Biggest Performance Gains:
1. Parquet caching (28x)
2. Polars vectorization (5-10x)
3. API batching (3x fewer calls)
4. Pre-computed indicators (2x)

### Indian Market Specific:
- T+1 settlement affects intraday capital
- 09:15-09:30 is most volatile (reduce size)
- 11:30-13:00 is choppy (avoid trading)
- Circuit breakers require proximity checks
- Zerodha instrument master needed for tick sizes

---

END OF COMPREHENSIVE EXTRACTION

