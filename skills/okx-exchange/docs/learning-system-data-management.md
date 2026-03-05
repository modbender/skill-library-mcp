# OKX Learning System — Data Management

## Data File Overview

| File | Purpose | Size Control |
|------|---------|--------------|
| `okx-learning-model.json` | Core learning model | Fixed structure, ~2 KB |
| `okx-trade-journal.json` | Trade records | Up to 1,000 entries; older entries compressed |
| `okx-monitoring-log.json` | Monitor sessions | Up to 100 sessions |
| `okx-lessons.json` | Learned lessons | Grows continuously, ~1 KB per entry |
| `okx-patterns.json` | Trade patterns | Keyed by coin × signal × market regime |

---

## Data Compression Strategy

### 1. Trade Record Compression

```
Raw entry (per trade):
{
  "id": "abc123",
  "coin": "BTC-USDT-SWAP",
  "entry_price": 67000,
  "exit_price": 67500,
  "pnl_pct": 0.75,
  "pnl_usdt": 50,
  "hold_time_hours": 2.5,
  ...
}

Compressed (statistical summary):
{
  "period_start": "2026-02-27T20:00:00",
  "period_end": "2026-02-28T20:00:00",
  "total_trades": 50,
  "winning_trades": 32,
  "losing_trades": 18,
  "total_pnl_usdt": 234.5,
  "avg_win_pct": 4.2,
  "avg_loss_pct": -2.1,
  "compressed_at": "2026-03-06T20:00:00"
}
```

**Compression rules:**
- Keep the most recent **1,000 trades** in full detail
- When the count exceeds 1,000 → compress older entries into statistical summaries
- Raw data is deleted after compression; only summaries are retained

### 2. Monitor Session Compression

```
Each session records:
- Signal counts (BUY / SELL / HOLD)
- Price range (high / low / open / close)
- Average RSI
- Detected market regime
- Strategy effectiveness evaluation

Retention policy:
- Keep the most recent 100 sessions in full detail
- Beyond 100 → merge into daily summaries
```

### 3. Time-Based Cleanup

| Data Age | Action |
|----------|--------|
| 0–7 days | Keep full detail |
| 7–30 days | Compress to statistical summary |
| 30–90 days | Retain core patterns only |
| 90+ days | Delete |

---

## Lesson Extraction

### 1. Automatic Lesson Capture

**Trigger conditions:**
```python
# Large loss (> 5%)
if pnl_pct < -5:
    lesson = {
        "type": "large_loss",
        "lesson": f"Lost {pnl_pct:.1f}% using {signal} signal in {market_regime} market",
        "action": f"Tighten stop-loss for {coin} or reduce weight for this signal",
        "avoid_condition": {"coin": coin, "signal": signal, "market_regime": market_regime}
    }

# Large win (> 10%)
if pnl_pct > 10:
    lesson = {
        "type": "large_win",
        "lesson": f"Gained {pnl_pct:.1f}% using {signal} signal in {market_regime} market",
        "action": f"Increase position size for {coin} in this market regime",
        "replicate_condition": {...}
    }

# Quick win (< 1h hold, > 5% gain)
if hold_time < 1 and pnl_pct > 5:
    lesson = {
        "type": "quick_win",
        "lesson": f"{coin} achieved quick +{pnl_pct:.1f}% gain",
        "action": "This coin is well-suited for short-term strategies"
    }
```

### 2. Pattern Recognition

**Recognition dimensions:**
```
Pattern key = coin × signal type × market regime
Example: "BTC-USDT-SWAP_BUY_strong_bull"

Tracked metrics:
- Trade count
- Win rate
- Average P&L
- Max consecutive wins / losses

Pattern classifications:
- successful: win rate >= 60%
- failed: win rate <= 30%
- neutral: 30% < win rate < 60%
```

### 3. Applying Lessons

**Pre-trade checks:**
```python
# Check whether to avoid
should_avoid, reason = should_avoid_trade(coin, signal, market_regime)
if should_avoid:
    return f"Avoid trade: {reason}"

# Check optimal conditions
suggestions = get_optimal_conditions(coin, signal, market_regime)
if suggestions:
    return f"Recommended trade: {suggestions}"
```

---

## Error Avoidance System

### 1. Real-Time Checks

Automatically applied before every trade:
```
1. Check the lesson library
   → Is there a recorded loss under these exact conditions?

2. Check failed patterns
   → Is the win rate for this coin + signal + regime below 30%?

3. Validate parameters
   → Are the current SL/TP levels consistent with historical optima?
```

### 2. Error Classification

| Error Type | Detection | Avoidance Strategy |
|------------|-----------|-------------------|
| Signal divergence | Consecutive same-direction signals with price moving opposite | Reduce signal weight |
| Overtrading | Multiple losses in a short window | Enforce a cooldown period |
| Bad parameters | Stop-loss triggers too frequently | Dynamically widen stop-loss |
| Regime misread | Trend strategy applied in a ranging market | Improve market regime detection |

### 3. Lessons Persisted as JSON

```json
{
  "lesson_id": "lesson_001",
  "type": "signal_divergence",
  "observation": "46 consecutive SELL signals; price moved +418 points against signal",
  "conclusion": "MA/MACD generates consecutive false signals in a ranging market",
  "action_taken": "Reduced MA/MACD weight (50% → 30%)",
  "avoid_condition": {
    "market_regime": "ranging",
    "signal": "SELL",
    "timeframe": "1H"
  },
  "created_at": "2026-02-27T21:00:00"
}
```

---

## Replicating Successful Trades

### 1. Successful Pattern Store

```json
{
  "pattern_id": "pattern_eth_bull_001",
  "coin": "ETH-USDT-SWAP",
  "signal": "BUY",
  "market_regime": "strong_bull",
  "trades": 15,
  "wins": 12,
  "losses": 3,
  "win_rate": 0.80,
  "avg_pnl": 8.5,
  "pattern_type": "successful",
  "replicate_when": {
    "rsi_range": [30, 60],
    "macd_positive": true,
    "volume_above_avg": true
  }
}
```

### 2. Pattern Activation

When market conditions match a successful pattern:
```
- Automatically increase position size (e.g. 30 USDT → 50 USDT)
- Widen take-profit target (e.g. 15% → 20%)
- Prioritize execution
```

### 3. Parameter Auto-Optimization

Based on historical performance:
```
If ETH win rate is 80% in bull markets:
  → Raise ETH position cap by 50%
  → Widen ETH stop-loss to 4%
  → Raise ETH take-profit to 20%

If LINK win rate is 25% in ranging markets:
  → Lower LINK position cap by 50%
  → Or avoid LINK trading entirely
```

---

## Learning System Workflow

```
Trade completes
    ↓
Record trade details
    ↓
Extract lessons → Update lesson library
    ↓
Update pattern stats → Identify successful / failed patterns
    ↓
Compress old data → Keep file sizes stable
    ↓
Before next trade: check lesson library and pattern store
    ↓
Adjust parameters and decisions based on historical experience
```

---

## Commands

```bash
# View learning status
python3 okx_learning.py status

# View recorded lessons
python3 okx_learning.py lessons

# View recognized patterns
python3 okx_learning.py patterns

# Check whether a trade should be avoided
python3 okx_learning.py check BTC-USDT-SWAP BUY strong_bull

# Analyze and suggest parameter optimizations
python3 okx_learning.py analyze

# Remove expired data
python3 okx_learning.py cleanup

# Manually compress old data
python3 okx_learning.py compress
```

---

## Storage Estimates

| File | Initial Size | Annual Growth | Est. After 5 Years |
|------|-------------|---------------|--------------------|
| learning-model.json | 2 KB | ~0 | 2 KB |
| trade-journal.json | 100 KB | ~500 KB (compressed) | 500 KB |
| monitoring-log.json | 50 KB | ~200 KB | 200 KB |
| lessons.json | 1 KB | ~50 KB (500 lessons) | 250 KB |
| patterns.json | 1 KB | ~20 KB (200 patterns) | 100 KB |
| **Total** | **~154 KB** | **~1 MB/year** | **~5 MB** |

With compression and cleanup, data growth is fully contained.

---

## Key Benefits

1. **No data bloat** — automatic compression and periodic cleanup
2. **Lessons accumulate** — lessons and patterns are retained permanently
3. **Errors are not repeated** — avoid conditions are checked before every trade
4. **Successes are replicated** — high-win-rate patterns are identified and reused
5. **Parameters self-optimize** — adjusted based on actual historical performance
6. **Fully auditable** — every decision is backed by historical evidence
