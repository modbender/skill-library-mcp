---
name: tearsheet-generator
description: >
  Generate professional tearsheets with custom SVG visualizations using the QuantStats library.
  Creates performance reports with MAE analysis, leverage recommendations, and trade lists.
  Use when analyzing strategy performance or generating visual reports.
version: "1.1.0"
allowed-tools: Read, Write, Edit, Bash, Glob
---

# Tearsheet Generator Skill

## About

This skill generates custom tearsheets using the [QuantStats library](https://github.com/ranaroussi/quantstats) - a Python library for portfolio analytics.

**Key Features:**
- Custom SVG visualizations (returns, drawdowns, monthly heatmaps)
- Professional HTML tearsheets
- MAE (Maximum Adverse Excursion) analysis
- Leverage recommendations based on risk metrics
- Copyable strategy configurations

Generate comprehensive trading strategy tearsheets with:
- IBM Plex Mono font styling (QuantStats format)
- MAE (Max Adverse Excursion) percentile analysis (p90-p99)
- Optimal leverage recommendations with stop-loss levels
- Fixed Position (Static) vs Full Position (Dynamic) analysis
- 10%, 20%, 30% liquidation buffer calculations
- Full trade list with entry/exit details and MAE stats
- Copyable strategy config text boxes
- Multiple leverage scenario comparisons (1x, 10x, 15x, 20x)

## Quick Start

```bash
# Generate tearsheet from trades CSV
/generate-tearsheet SOL_MTF_EMA_001 --trades ./trades.csv --capital 10000

# Verify backtest with Nautilus Trader
/verify-backtest SOL_MTF_EMA_001 --trades ./trades.csv

# Test optimal leverage configuration
/verify-mae-lev SOL_MTF_EMA_001 --leverage p95
```

## Commands

### /generate-tearsheet
Generate a complete tearsheet with all analysis sections.

### /verify-backtest
Verify tearsheet results against Nautilus Trader for accuracy validation.

### /verify-mae-lev
Run backtest with optimal leverage config derived from MAE analysis.

## Output Files

Each tearsheet generation produces:
- `{strategy}_comparison.html` - Full HTML tearsheet
- `{strategy}_comparison_metrics.json` - JSON metrics for programmatic access

## Key Sections

### 1. Key Performance Metrics
- B&H, Fix1x, Dyn1x, Fix10x, Dyn10x columns
- Cumulative Return, CAGR, Sharpe, Sortino, Max DD, Calmar
- Intratrade risk metrics with liquidation distance

### 2. MAE Analysis & Optimal Leverage
- MAE distribution table (min, mean, p50, p75, p90-p99, max)
- Safe leverage recommendations per percentile
- Stop loss table with % PRICE movement (not position cost)

### 3. Fixed Position (Static) Analysis
- Leverage table: 5x, 10x, 15x, 20x, 25x, 30x
- Columns: Liq @ %Price, Rec. SL, Max Loss, +10% Buffer, +20% Buffer, Risk Level

### 4. Full Position (Dynamic) Analysis
- Warning about compounding risk
- Leverage table: 1x, 2x, 3x, 5x, 10x
- Recommendation per leverage level

### 5. Buffer Analysis Summary
- +10%, +20%, +30% buffers above worst MAE
- Safety check for 10x, 15x, 20x leverage

### 6. Full Trade List
- All trades with entry/exit times, prices, side, PnL, MAE, MFE, duration
- Scrollable table with sticky headers
- Summary row with averages

### 7. Strategy Configuration
- Original config text box (copyable JSON)
- MAE-optimized config text box (copyable JSON)
- Backtest methodology description

## Dependencies

- Python 3.10+
- pandas, numpy, matplotlib
- StrategyComparisonTearsheet from backtesting.tearsheets

## Installation

The skill uses the tearsheet generator at:
`/Users/DanBot/Desktop/dev/Backtests/backtesting/tearsheets/strategy_comparison_tearsheet.py`

Ensure this path is accessible or update the script paths accordingly.
