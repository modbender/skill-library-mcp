---
name: verify-mae-lev
description: Run new backtest with optimal leverage config from MAE analysis
argument-hint: "[strategy_name] [--leverage LEVEL] [--stop-loss PCT] [--validate]"
---

# Verify MAE Leverage Command

Runs a new backtest with optimal leverage configuration derived from MAE analysis.

## Usage

```bash
# Use p95-safe leverage (conservative)
/verify-mae-lev SOL_MTF_EMA_001 --leverage p95

# Use specific leverage with recommended stop loss
/verify-mae-lev SOL_MTF_EMA_001 --leverage 10x --stop-loss 6.4

# Validate against original results
/verify-mae-lev SOL_MTF_EMA_001 --validate
```

## Process

1. **Load MAE Analysis**
   - Read `{strategy}_comparison_metrics.json`
   - Extract MAE percentiles and leverage recommendations

2. **Generate Optimal Config**
   ```python
   mae_data = metrics['mae_analysis']

   # For p95-safe (survives 95% of trades)
   p95_mae = mae_data['distribution']['p95']
   safe_leverage = mae_data['leverage_recommendations']['p95']['safe_leverage']

   # Get recommended stop loss
   sl_data = mae_data['stop_loss_recommendations'][f'{int(safe_leverage)}x']
   recommended_sl = sl_data['recommended_stop_loss_price_pct']
   ```

3. **Run New Backtest**
   - Apply optimal leverage to strategy
   - Set stop loss based on recommendations
   - Execute with Nautilus Trader

4. **Compare Results**
   - Original metrics vs optimized
   - Risk-adjusted return improvement
   - Liquidation proximity reduction

## Output Files

- `{strategy}_optimized_config.json` - New strategy configuration
- `{strategy}_optimized_tearsheet.html` - New tearsheet with optimal settings
- `{strategy}_optimization_report.txt` - Comparison and recommendations

## Leverage Levels (Granular p90-p99)

| Level | Description | Risk Profile |
|-------|-------------|--------------|
| `p50` | Survives 50% of trades | Very aggressive |
| `p75` | Survives 75% of trades | Aggressive |
| `p90` | Survives 90% of trades | Moderate-High |
| `p91` | Survives 91% of trades | Moderate |
| `p92` | Survives 92% of trades | Moderate |
| `p93` | Survives 93% of trades | Moderate |
| `p94` | Survives 94% of trades | Moderate-Conservative |
| `p95` | Survives 95% of trades | Conservative |
| `p96` | Survives 96% of trades | Conservative |
| `p97` | Survives 97% of trades | Very conservative |
| `p98` | Survives 98% of trades | Very conservative |
| `p99` | Survives 99% of trades | Ultra conservative |
| `max` | Survives worst trade | Safest |

## Stop Loss Terminology

**IMPORTANT**: All stop loss values are in **% PRICE movement**, not % of position cost.

| Term | Meaning |
|------|---------|
| **SL @ %Price** | Price movement that triggers stop loss (e.g., 6.4% for 10x) |
| **Liq @ %Price** | Price movement that causes liquidation (e.g., 8.0% for 10x) |
| **% of Margin** | Actual loss as percentage of your position cost |

**Example at 10x leverage:**
- Entry: $100
- SL @ 6.4% price: Exit at $93.60
- Loss: 6.4% × 10 = 64% of margin
- Remaining: 36% of your position

## Buffer Analysis

Use buffer options to add safety margin above worst historical MAE:

| Buffer | Description | Use Case |
|--------|-------------|----------|
| +10% | MAE × 1.1 | Standard safety margin |
| +20% | MAE × 1.2 | Conservative approach |
| +30% | MAE × 1.3 | Ultra-safe for volatile markets |

## Example Report

```
OPTIMAL LEVERAGE ANALYSIS - SOL_MTF_EMA_001
==========================================

MAE Distribution:
  p50: 0.16% -> Safe leverage: >100x
  p75: 0.28% -> Safe leverage: >100x
  p90: 0.46% -> Safe leverage: >100x
  p95: 0.62% -> Safe leverage: >100x
  p99: 1.07% -> Safe leverage: 59.7x
  max: 2.13% -> Safe leverage: 30.0x

FIXED POSITION RECOMMENDATIONS:
  Conservative (p99): Use 20x with 3.2% SL
  Moderate (p95): Use 20x with 3.2% SL
  Aggressive (max): Use 20x with 3.2% SL

DYNAMIC POSITION RECOMMENDATIONS:
  1x ONLY recommended due to compounding risk

BUFFER ANALYSIS:
  +10% buffer (2.34% SL): Safe for 10x, 15x, 20x
  +20% buffer (2.56% SL): Safe for 10x, 15x, 20x
  +30% buffer (2.77% SL): Safe for 10x, 15x, 20x
```
