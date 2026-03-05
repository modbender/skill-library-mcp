---
name: generate-tearsheet
description: Generate a comprehensive QuantStats-style tearsheet with MAE analysis
argument-hint: "[strategy_name] [--trades PATH] [--config PATH] [--capital AMOUNT] [--output DIR]"
---

# Generate Tearsheet Command

Generate a professional trading strategy tearsheet with comprehensive analysis.

## Usage

```bash
# Basic usage
/generate-tearsheet SOL_MTF_EMA_001 --trades /path/to/trades.csv

# With custom capital and output
/generate-tearsheet SOL_MTF_EMA_001 --trades ./trades.csv --capital 10000 --output ./tearsheets

# With strategy config
/generate-tearsheet SOL_MTF_EMA_001 --trades ./trades.csv --config ./strategy_config.json
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| strategy_name | Yes | Name of the strategy (used in output filenames) |
| --trades | Yes | Path to trades CSV file |
| --config | No | Path to strategy config JSON |
| --capital | No | Initial capital (default: 10000) |
| --output | No | Output directory (default: ./tearsheets) |

## Trades CSV Format

Required columns:
- `side` - LONG/SHORT or BUY/SELL
- `entry_time` - Entry timestamp
- `exit_time` - Exit timestamp
- `entry_price` - Entry price
- `exit_price` - Exit price
- `gross_pnl_pct` or `pnl_pct` - Trade P&L percentage
- `mae_pct` or `mae` - Max Adverse Excursion percentage

Optional columns:
- `net_pnl_pct` - Net P&L after fees
- `mfe_pct` or `mfe` - Max Favorable Excursion
- `duration_hours` or `bars` - Trade duration
- `reason_open` - Entry reason
- `reason_close` - Exit reason

## Implementation

```python
import sys
import pandas as pd
sys.path.insert(0, '/Users/DanBot/Desktop/dev/Backtests')
from backtesting.tearsheets.strategy_comparison_tearsheet import StrategyComparisonTearsheet

# Load trades
trades_df = pd.read_csv(trades_path)

# Generate tearsheet
tearsheet = StrategyComparisonTearsheet(
    strategy_name=strategy_name,
    trades_df=trades_df,
    initial_capital=capital,
    output_dir=output_dir,
    strategy_dir=strategy_dir  # Optional: for config file links
)

html_path, json_path = tearsheet.generate()
print(f"Generated: {html_path}")
print(f"Metrics: {json_path}")
```

## Output

The command generates:

1. **HTML Tearsheet** (`{strategy}_comparison.html`)
   - Two-column QuantStats layout
   - IBM Plex Mono font
   - SVG charts (cumulative returns, underwater, rolling metrics)
   - MAE analysis with leverage recommendations
   - Fixed vs Dynamic position analysis
   - Full trade list
   - Copyable config text boxes

2. **JSON Metrics** (`{strategy}_comparison_metrics.json`)
   - All scenario results (1x, 10x, 15x, 20x - fixed & dynamic)
   - Trade statistics
   - MAE distribution and percentiles
   - Leverage recommendations
   - Stop loss recommendations

## Example Output

```
✓ Generated comparison tearsheet for SOL_MTF_EMA_001
  HTML: ./tearsheets/SOL_MTF_EMA_001_comparison.html
  JSON: ./tearsheets/SOL_MTF_EMA_001_comparison_metrics.json

Scenarios:
  SOL Buy & Hold: -42.3% return, 63.1% max DD
  Fixed 1x: 988.4% return, 0.2% max DD
  Dynamic 1x: 1.7M% return, 0.6% max DD
  Fixed 10x: 9.9K% return, 0.4% max DD
  Dynamic 10x: >999Sep% return, 6.3% max DD
```
