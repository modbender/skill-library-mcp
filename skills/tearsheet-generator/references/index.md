# Tearsheet Generator Reference Index

## Core Files

| File | Description |
|------|-------------|
| `skill.md` | Main skill documentation with commands and examples |
| `tearsheet_helpers.py` | Python helper module for MAE analysis and leverage recommendations |

## Reference Documents

| Document | Topics Covered |
|----------|----------------|
| `mae_analysis.md` | MAE theory, percentile calculations, risk scoring |
| `leverage_math.md` | Leverage formulas, buffer calculations, Kelly criterion |
| `html_templates.md` | CSS templates, HTML components, responsive design |

## Related Scripts

| Script | Location | Purpose |
|--------|----------|---------|
| `strategy_tearsheet.py` | `/scripts/` | Main tearsheet generation CLI |
| `generate_tearsheets.py` | `/scripts/` | Batch tearsheet generation with QuantStats |

## Quick Reference

### Generate Tearsheet
```bash
python scripts/strategy_tearsheet.py --strategy SOL_MTF --trades trades.csv --output ./tearsheets
```

### MAE Analysis
```python
from skills.tearsheet_generator.tearsheet_helpers import calculate_mae_percentiles, recommend_leverage

stats = calculate_mae_percentiles(trades)
recs = recommend_leverage(stats.p95)
```

### Liquidation Risk
```python
from skills.tearsheet_generator.tearsheet_helpers import analyze_liquidation_risk

risk = analyze_liquidation_risk(trades, leverage=10.0)
print(f"Survival rate: {risk.survival_rate}%")
```

## Key Formulas

| Metric | Formula |
|--------|---------|
| Liquidation Threshold | `100% / leverage` |
| Buffer Threshold | `(100% / leverage) * (1 - buffer)` |
| Max Safe Leverage | `100% / p95_mae * (1 - buffer)` |
| Leveraged Return | `base_return * leverage` |
| Dynamic Leverage | `max(1, base_lev * (1 - drawdown))` |

## Output Files

When generating a tearsheet, these files are created:

```
tearsheets/STRATEGY_NAME/
├── STRATEGY_NAME_comparison.html          # Main HTML tearsheet
├── STRATEGY_NAME_comparison_metrics.json  # JSON metrics export
├── tradelist.csv                          # Full trade list
└── strategy_config.py                     # Copyable Python config
```

## Integration Points

| Tool | Integration |
|------|-------------|
| Nautilus Trader | Load trades with `source_type="nautilus"` for verification badge |
| Ray Tune | Generate tearsheets for optimized configurations |
| QuantStats | Use alongside for additional statistical analysis |
| Hyperliquid | Apply recommended leverage via SDK patch |

## Common Issues

1. **Missing MAE data**: Falls back to using `return_pct` for losing trades
2. **Large numbers**: Automatically formatted with K/M/B/T/Q suffixes
3. **Extreme leverage returns**: Capped display at `>10^100`
4. **Monthly gaps**: Check trade date range for continuity
