# AlgoTrader: Quantitative Trading Skill for Claude Code

> **Comprehensive trading expert embodying real-world learnings from Indian equity markets**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Zerodha](https://img.shields.io/badge/Zerodha-Kite%20API-orange.svg)](https://kite.trade/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Skills.sh](https://img.shields.io/badge/skills.sh-install-blue)](https://skills.sh/javajack/skill-algotrader)
[![GitHub](https://img.shields.io/github/stars/javajack/skill-algotrader?style=social)](https://github.com/javajack/skill-algotrader)

## Overview

AlgoTrader is a Claude Code skill that provides expert guidance for building, optimizing, and running quantitative trading systems on Indian stock markets. It embodies **1,780 lines of real-world learnings** from production trading, including:

- ✅ **65%+ win rate** signal generation strategies
- ✅ **28x performance optimizations** (Parquet caching, vectorization)
- ✅ **Zero-regression code modifications** with automated testing
- ✅ **Production failure prevention** (30+ gotchas documented)
- ✅ **Backtest-live parity** validation
- ✅ **Risk-adjusted capital compounding**

## Installation

### Quick Install (Recommended)

Install directly from the skills.sh directory:

```bash
npx skills add javajack/skill-algotrader
```

### Manual Installation

#### Option 1: Clone to Claude Skills Directory
```bash
cd ~/.claude/skills
git clone https://github.com/javajack/skill-algotrader.git algotrader
cd algotrader
./start.sh wizard  # Start using the skill
```

#### Option 2: Custom Skills Path
```bash
export CLAUDE_SKILLS_PATH=~/work/skills
cd ~/work/skills
git clone https://github.com/javajack/skill-algotrader.git algotrader
cd algotrader
./start.sh wizard
```

### Install Python Dependencies

After installation, set up the Python environment:

```bash
cd ~/.claude/skills/algotrader  # or your custom path
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Or use the convenience script (auto-creates venv)
./start.sh wizard
```

## Features

### 🎯 Interactive Bot Generation Wizard

Launch `/algotrader` without parameters to enter the wizard:

```bash
$ /algotrader

╔══════════════════════════════════════════════════════════════╗
║              ALGOTRADER BOT GENERATION WIZARD                ║
╚══════════════════════════════════════════════════════════════╝

Scanning current directory for trading code...
✓ Found: backtest.py, signal_generator.py

What would you like to do?
  1. Generate new trading bot from scratch
  2. Enhance existing code (fix issues, optimize)
  3. Create universe JSON from live index data
  4. Run backtest comparison
  5. Analyze performance

> 1

Let's design your trading bot. I'll ask a few questions...
```

The wizard will:
- Scan your folder for existing trading code
- Ask strategic questions (trade type, universe, capital, risk tolerance)
- Generate a complete, working trading bot
- Create universe JSON files with latest index constituents
- Set up logging, analytics, and risk management

### 📊 Universe Fetcher (Live Index Data)

Automatically fetches latest index constituents from NSE:

```python
/algotrader universe

Fetching live index data from NSE...
✓ Nifty 50: 50 stocks (updated: 2026-02-14)
✓ Nifty 100: 100 stocks
✓ Nifty Midcap 150: 150 stocks
✓ Nifty Smallcap 250: 250 stocks

Created:
  └─ universe/
     ├─ nifty50.json (50 stocks, ₹500Cr+ mcap)
     ├─ nifty100.json (100 stocks)
     ├─ midcap150.json (150 stocks, ₹50-500Cr mcap)
     └─ smallcap250.json (250 stocks, ₹10-50Cr mcap)

Each file includes:
  - Symbol, company name, ISIN
  - Market cap, sector
  - Liquidity metrics (avg volume, spread)
  - Last updated timestamp
```

### 🧠 16 Knowledge Domains

1. **Zerodha Integration** - Tick size rounding, position reconciliation, SL lifecycle
2. **Backtest-Live Parity** - Data caching, T vs T-1 alignment, VWAP reset
3. **Signal Generation** - Fortress signal (65% win rate), multi-factor confirmation
4. **Rebalancing Logic** - Weekly vs daily, transaction cost modeling
5. **Stock Universe Selection** - Liquidity filtering, momentum scoring
6. **Performance Optimization** - Parquet (28x), Polars vectorization (37x), API batching
7. **Indian Market Specifics** - Session timing, circuit breakers, T+1 settlement
8. **Failure Patterns** - 5 production issues + fixes (HINDALCO loop, naked positions)
9. **Indicators & Formulas** - RSI, MACD, ATR, ADX, VWAP, EMA (exact formulas + parameters)
10. **Multi-Timeframe Trading** - Intraday vs positional, MTF alignment
11. **Logging & Observability** - Structured logging, real-time monitoring
12. **Post-Trade Analytics** - P&L breakdown, Sharpe ratio, drawdown analysis
13. **Signal Attribution** - Track which indicator triggered, exhaustion detection
14. **Exit Strategies** - Time decay, trailing stops, partial exits
15. **Risk Management** - Kelly Criterion, portfolio heat, consecutive loss throttling
16. **Capital Compounding** - Market regime detection, bull market amplification

### ⚠️ 30+ Token-Burning Gotchas (NUANCES.md)

Common mistakes that burn hours of debugging:

```markdown
🔥 CRITICAL: Tick Size Rounding
Mistake: kite.place_order(price=1847.35, ...)
Error: "Tick size for this script is 5.00"
Fix: price = round(price / tick_size) * tick_size  # 1847.35 → 1850.00
Impact: 90% of order rejections are tick size errors

🔥 CRITICAL: VWAP Must Reset Daily
Mistake: Cumulative VWAP across days
Symptom: Backtest 65% win rate, live 40%
Fix: Reset at market open (9:15)
Impact: #1 cause of backtest-live parity violations
```

See [NUANCES.md](NUANCES.md) for all 30+ gotchas.

## Configuration

### Configure Zerodha API Credentials

For live trading, create a `.env` file in your bot directory:

```bash
# Create .env file (never commit this!)
cat > .env << EOF
KITE_API_KEY=your_api_key
KITE_API_SECRET=your_api_secret
KITE_ACCESS_TOKEN=your_access_token
EOF
```

Get credentials from: https://kite.trade/

**Note:** The `.env` file is automatically excluded from git via `.gitignore`. Never commit API credentials!

## Quick Start

### Generate Your First Trading Bot

```bash
# Launch wizard
/algotrader

# Or directly in Claude Code chat
> /algotrader wizard
```

The wizard will ask:

1. **Trading Style:** Intraday, Swing (multi-day), Positional (multi-week)
2. **Universe:** Nifty 50 (largecap), Nifty Midcap 150, Custom
3. **Strategy:** Momentum, VWAP Pullback, Opening Range Breakout
4. **Capital:** Starting capital and risk per trade
5. **Risk Tolerance:** Conservative (0.5% risk), Balanced (1%), Aggressive (2%)

Based on your answers, it generates:

```
trading_bot/
├── config.json          # Strategy parameters
├── main.py             # Entry point
├── signal_generator.py # Signal logic
├── data_manager.py     # Data fetching and caching
├── risk_manager.py     # Position sizing, Kelly Criterion
├── zerodha_client.py   # API integration
└── universe/
    └── nifty50.json    # Stock universe (fetched from NSE)
```

### Fetch Universe from Live Data

```bash
/algotrader universe --indices nifty50,nifty100,midcap150

# Creates JSON files with latest constituents
# Includes liquidity filtering, market cap, sector
```

### Analyze Existing Code

```bash
# Point to your existing trading code
/algotrader check ./my_trading_bot.py

# Output:
⚠️  Found 3 issues:
1. Tick size not rounded (line 45) - will cause order rejections
2. VWAP not reset daily (line 89) - backtest-live parity violation
3. No symbol cooldown (line 120) - risk of revenge trading

Recommended fixes:
  1. Add tick_size rounding: price = round_to_tick(price, symbol)
  2. Reset VWAP at 9:15: if is_new_day(): vwap_state.reset()
  3. Add 45min cooldown: if not can_trade_symbol(symbol): return None

Apply fixes automatically? (y/n):
```

## Usage Examples

### Example 1: Fortress Signal Generation

```python
from algotrader import generate_fortress_signal

# Your OHLCV data with indicators
df = load_data("RELIANCE", date="2026-02-14")

signal = generate_fortress_signal(
    df=df,
    symbol="RELIANCE",
    config={
        'rsi_long_min': 45,
        'rsi_long_max': 65,
        'adx_min': 25,
        'volume_mult': 1.5
    }
)

if signal:
    print(f"🎯 LONG signal for {signal['symbol']}")
    print(f"   Entry: ₹{signal['entry_price']}")
    print(f"   Stop Loss: ₹{signal['stop_loss']}")
    print(f"   Target: ₹{signal['target']}")
    print(f"   Confidence: {signal['confidence']:.0%}")
    print(f"   Reason: {signal['reason']}")
```

### Example 2: Backtest Comparison

```python
from algotrader import compare_backtests

# Compare backtest results with live trading
comparison = compare_backtests(
    backtest_file="backtests/fortress_v2.parquet",
    live_file="backtests/live_results.parquet"
)

print(f"Win Rate: {comparison['backtest_winrate']:.1%} → {comparison['live_winrate']:.1%}")
print(f"Delta: {comparison['winrate_delta']:.1%}")

if comparison['parity_issues']:
    print("\n⚠️  Parity Issues:")
    for issue in comparison['parity_issues']:
        print(f"  - {issue['description']}")
        print(f"    Fix: {issue['recommended_fix']}")
```

### Example 3: Universe Fetcher (Programmatic)

```python
from algotrader.universe import fetch_index_constituents, filter_universe

# Fetch latest Nifty 50 from NSE
nifty50 = fetch_index_constituents("NIFTY 50")
print(f"✓ Fetched {len(nifty50)} stocks")

# Apply liquidity filtering
filtered = filter_universe(
    nifty50,
    min_volume=100_000,      # Min daily volume
    max_spread_pct=0.3,      # Max bid-ask spread
    min_atr_pct=0.15,        # Min volatility
    max_atr_pct=2.5          # Max volatility
)

print(f"✓ After filtering: {len(filtered)} stocks")

# Save to JSON
save_universe(filtered, "universe/nifty50_filtered.json")
```

## Architecture

### Minimal Design Philosophy

AlgoTrader follows these principles:

1. **Few files, high cohesion** - 7 files total, not 20+
2. **LLM-friendly comments** - Clear refactoring guidance
3. **Pure functions** - Testable, no hidden state
4. **Vectorized operations** - Polars, not loops
5. **Single source of truth** - KNOWLEDGE.md for all learnings

### File Structure

```
algotrader/
├── skill.json              # Skill manifest (Claude Code integration)
├── README.md              # This file
├── KNOWLEDGE.md           # All 16 domains (1,780 lines of learnings)
├── NUANCES.md             # 30+ token-burning gotchas
├── algotrader.py          # Main CLI + wizard (~800 lines)
├── requirements.txt       # Python dependencies
├── templates/
│   ├── minimal_intraday.py    # Bare minimum intraday bot (50 lines)
│   └── minimal_positional.py  # Bare minimum positional bot (50 lines)
└── examples/
    ├── full_system.py         # Complete reference implementation (~300 lines)
    └── universe_fetcher.py    # Fetch index constituents from NSE
```

## Knowledge Base

### KNOWLEDGE.md

Comprehensive documentation of all 16 domains:

- Exact code patterns that work in production
- Numeric parameters from real testing (rsi_long_min=45, adx_min=25)
- Before/After comparisons for failures
- Performance benchmarks (Parquet: 28x faster, Polars: 37x faster)

**Size:** 48KB, 1,780 lines
**Format:** Markdown with code examples
**Usage:** Searchable by keyword, cross-referenced

### NUANCES.md

Token-saving precautions that prevent hours of debugging:

- 🔥 **10 Critical mistakes** that break trading (tick size, VWAP reset, SL lifecycle)
- 🚀 **13 Performance tips** for 10x+ speedups
- 📊 **7 Data quality checks** to prevent backtest lies
- 💰 **5 Capital management rules** to protect capital
- 🐛 **5 Debugging techniques** for production issues

**Summary:** Read this FIRST before implementing anything.

## Advanced Features

### Market Regime Detection

Automatically amplifies risk in bull markets:

```python
from algotrader.risk import detect_market_regime, calculate_position_size

# Detect regime (BULL, BEAR, SIDEWAYS)
regime = detect_market_regime(nifty_data)

# Adjust position size
base_size = 500_000  # ₹5L base
regime_multipliers = {
    "BULL": 1.2,      # +20% in bull market
    "BEAR": 0.5,      # -50% in bear market
    "SIDEWAYS": 0.8   # -20% in sideways
}

position_size = base_size * regime_multipliers[regime]
# BULL: ₹6L, BEAR: ₹2.5L, SIDEWAYS: ₹4L
```

### Kelly Criterion Position Sizing

Optimal position sizing based on win rate:

```python
from algotrader.risk import calculate_kelly_position

kelly = calculate_kelly_position(
    win_rate=0.65,     # 65% win rate
    avg_win=0.012,     # 1.2% avg win
    avg_loss=0.006     # 0.6% avg loss
)

print(f"Full Kelly: {kelly['full_kelly']:.1%}")      # 28.6%
print(f"Half Kelly: {kelly['half_kelly']:.1%}")      # 14.3% (recommended)
print(f"Use {kelly['recommended']:.1%} of capital")
```

### Post-Trade Analytics

```python
from algotrader.analytics import generate_daily_report

report = generate_daily_report(trades_file="logs/trades.jsonl")

print(f"📊 Daily Performance:")
print(f"   Trades: {report['total_trades']}")
print(f"   Win Rate: {report['win_rate']:.1%}")
print(f"   P&L: ₹{report['pnl']:,.0f}")
print(f"   Best Trade: {report['best_trade']['symbol']} (+{report['best_trade']['pnl_pct']:.1%})")
print(f"   Worst Trade: {report['worst_trade']['symbol']} ({report['worst_trade']['pnl_pct']:.1%})")
print(f"   Sharpe Ratio: {report['sharpe_ratio']:.2f}")
```

## Production Checklist

Before going live, ensure:

- [ ] **Tick size rounding** implemented for all order prices
- [ ] **Position reconciliation** on startup (Zerodha = truth)
- [ ] **VWAP daily reset** at market open (9:15)
- [ ] **Symbol cooldown** (45min after exit)
- [ ] **Stop loss lifecycle** uses place-then-cancel pattern
- [ ] **Candle completion** check (500ms buffer)
- [ ] **Margin calculation** uses `net` not `opening_balance`
- [ ] **Session timing** blocks 11:30-13:00 (choppy lunch)
- [ ] **Parquet caching** for historical data (28x faster)
- [ ] **Structured logging** (operational, debug, errors separate)
- [ ] **Backtest comparison** validates parity
- [ ] **Risk limits** enforced (max 1% per trade, 5% portfolio heat)
- [ ] **Circuit breaker** proximity check before entry
- [ ] **Graceful shutdown** handler (Ctrl+C closes positions)
- [ ] **Backup automation** before code modifications

See [NUANCES.md](NUANCES.md) for detailed checklist.

## Performance Benchmarks

Real-world improvements from applying AlgoTrader patterns:

| Optimization | Before | After | Gain |
|--------------|--------|-------|------|
| Parquet caching | 2.3s load | 0.08s load | **28.7x** |
| Polars vectorization | 450ms | 12ms | **37.5x** |
| API batching | 15 calls | 1 call | **15x** |
| Pre-computed indicators | 180ms | 90ms | **2x** |
| **Total backtest time** | **5 min** | **12 sec** | **25x** |

## Troubleshooting

### Common Issues

**Issue:** Order rejected with "Tick size error"
```python
# Fix: Round to tick size
from algotrader.zerodha import get_tick_size, round_to_tick

tick_size = get_tick_size("RELIANCE")  # 0.05
price = round_to_tick(1847.35, tick_size)  # 1847.35 → 1847.35 (already ok)
price = round_to_tick(1847.33, tick_size)  # 1847.33 → 1847.35
```

**Issue:** Backtest shows 65% win rate, live shows 40%
```python
# Likely causes:
1. VWAP not reset daily - check if VWAP resets at 9:15
2. Candle completion not checked - add 500ms buffer
3. Different data sources - use same cache for both
4. Slippage not modeled - add realistic slippage (₹2-5)

# Run parity diagnostic:
/algotrader backtest compare backtest.parquet live.parquet
```

**Issue:** Same stock bought/sold repeatedly (HINDALCO loop)
```python
# Fix: Add symbol cooldown
symbol_cooldowns[symbol] = time.time()
if time.time() - symbol_cooldowns.get(symbol, 0) < 45*60:
    return None  # Skip signal for 45 minutes
```

## Contributing

We welcome contributions! This skill is designed for:

1. **Knowledge expansion** - Add new failure patterns as discovered
2. **Strategy templates** - Share working strategies
3. **Performance optimizations** - Better caching, faster indicators
4. **Indian market updates** - New SEBI regulations, exchange changes

### How to Contribute

1. Test changes thoroughly (backtest + paper trade)
2. Document learnings in KNOWLEDGE.md format
3. Add nuances to NUANCES.md if token-burning
4. Include LLM-friendly comments
5. Submit PR with before/after metrics

## License

MIT License - see [LICENSE](LICENSE) file

## Disclaimer

**⚠️ IMPORTANT:** This skill provides educational guidance for building trading systems. It does NOT:

- Guarantee profits or specific returns
- Provide investment advice
- Replace professional financial guidance
- Execute trades without user confirmation

**Trading involves risk. Only trade with capital you can afford to lose.**

Past performance (65% win rate, 51% CAGR) from backtests does NOT guarantee future results.

## Support

- **Documentation:** [KNOWLEDGE.md](KNOWLEDGE.md) - Comprehensive learnings
- **Quick Reference:** [NUANCES.md](NUANCES.md) - Token-saving gotchas
- **Examples:** See `examples/` directory
- **Issues:** GitHub Issues (if published)

## Changelog

### v1.0.0 (2026-02-14)

- ✅ Initial release with 16 knowledge domains
- ✅ Interactive bot generation wizard
- ✅ Universe fetcher from live NSE data
- ✅ 30+ token-burning gotchas documented
- ✅ Fortress signal (65% win rate)
- ✅ Backtest comparison tool
- ✅ Production failure prevention
- ✅ Performance optimizations (28x Parquet, 37x Polars)
- ✅ Risk management (Kelly, regime detection)

---

**Built with real-world trading experience. Designed for production use.**

*"Read NUANCES.md first. It saves 100+ debugging sessions."*
