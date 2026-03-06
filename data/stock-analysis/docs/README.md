# Documentation

## Stock Analysis v6.1

This folder contains detailed documentation for the Stock Analysis skill.

## Contents

| Document | Description |
|----------|-------------|
| [CONCEPT.md](./CONCEPT.md) | Philosophy, ideas, and design rationale |
| [USAGE.md](./USAGE.md) | Practical usage guide with examples |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Technical implementation details |
| [HOT_SCANNER.md](./HOT_SCANNER.md) | 🔥 Viral trend detection (NEW) |

## Quick Links

### For Users

Start with **[USAGE.md](./USAGE.md)** — it has practical examples for:
- Basic stock analysis
- Comparing stocks
- Crypto analysis
- Dividend investing
- Portfolio management
- Watchlist & alerts

### For Understanding

Read **[CONCEPT.md](./CONCEPT.md)** to understand:
- Why 8 dimensions?
- How scoring works
- Contrarian signals
- Risk detection philosophy
- Limitations we acknowledge

### For Developers

Check **[ARCHITECTURE.md](./ARCHITECTURE.md)** for:
- System overview diagram
- Data flow
- Caching strategy
- File structure
- Performance optimization

## Quick Start

```bash
# Analyze a stock
uv run scripts/analyze_stock.py AAPL

# Fast mode (2-3 seconds)
uv run scripts/analyze_stock.py AAPL --fast

# Dividend analysis
uv run scripts/dividends.py JNJ

# Watchlist
uv run scripts/watchlist.py add AAPL --target 200
uv run scripts/watchlist.py check
```

## Key Concepts

### The 8 Dimensions

1. **Earnings Surprise** (30%) — Did they beat expectations?
2. **Fundamentals** (20%) — P/E, margins, growth, debt
3. **Analyst Sentiment** (20%) — Professional consensus
4. **Historical Patterns** (10%) — Past earnings reactions
5. **Market Context** (10%) — VIX, SPY/QQQ trends
6. **Sector Performance** (15%) — Relative strength
7. **Momentum** (15%) — RSI, 52-week range
8. **Sentiment** (10%) — Fear/Greed, shorts, insiders

### Signal Thresholds

| Score | Recommendation |
|-------|----------------|
| > +0.33 | **BUY** |
| -0.33 to +0.33 | **HOLD** |
| < -0.33 | **SELL** |

### Risk Flags

- ⚠️ Pre-earnings (< 14 days)
- ⚠️ Post-spike (> 15% in 5 days)
- ⚠️ Overbought (RSI > 70 + near 52w high)
- ⚠️ Risk-off mode (GLD/TLT/UUP rising)
- ⚠️ Geopolitical keywords
- ⚠️ Breaking news alerts

## Disclaimer

⚠️ **NOT FINANCIAL ADVICE.** For informational purposes only. Always do your own research and consult a licensed financial advisor.
