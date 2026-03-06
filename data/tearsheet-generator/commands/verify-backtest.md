---
name: verify-backtest
description: Verify backtest results with Nautilus Trader for accuracy validation
argument-hint: "[strategy_name] [--trades PATH] [--compare-metrics]"
---

# Verify Backtest Command

Validates tearsheet results against Nautilus Trader backtest for accuracy.

## Usage

```bash
/verify-backtest SOL_MTF_EMA_001 --trades /path/to/trades.csv
```

## Verification Steps

1. **Load Original Results**
   - Read tearsheet JSON metrics
   - Extract trade statistics and scenario results

2. **Run Nautilus Trader Verification**
   - Execute equivalent backtest in Nautilus Trader
   - Use same strategy parameters and data period

3. **Compare Results**
   - Total return within 5% tolerance
   - Win rate within 2% tolerance
   - Max drawdown within 10% tolerance
   - Trade count exact match

4. **Generate Verification Report**
   - Create verification JSON with comparison
   - Update tearsheet with verification status
   - Flag discrepancies for investigation

## Example Implementation

```python
import json

# Load tearsheet metrics
with open(f"{strategy_name}_comparison_metrics.json") as f:
    tearsheet_data = json.load(f)

# Run Nautilus verification
nautilus_results = run_nautilus_backtest(
    strategy=strategy_name,
    trades_csv=trades_path,
    initial_capital=tearsheet_data['initial_capital']
)

# Compare
verification = {
    'status': 'PASSED' if all_within_tolerance else 'FAILED',
    'tearsheet_results': tearsheet_data['scenarios']['fixed_1x'],
    'nautilus_results': nautilus_results,
    'comparison': {
        'return_diff': abs(ts_return - nt_return),
        'dd_diff': abs(ts_dd - nt_dd),
        'trade_count_match': ts_trades == nt_trades
    }
}
```

## Output

Creates `{strategy_name}_nautilus_verification.json` with:
- Verification status (PASSED/FAILED/PENDING)
- Side-by-side comparison of metrics
- Recommendations for discrepancies

## Tolerance Thresholds

| Metric | Tolerance | Notes |
|--------|-----------|-------|
| Total Return | ±5% | Relative difference |
| Win Rate | ±2% | Absolute difference |
| Max Drawdown | ±10% | Relative difference |
| Trade Count | Exact | Must match exactly |
| Sharpe Ratio | ±0.5 | Absolute difference |
