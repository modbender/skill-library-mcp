# Report Template (Strict)

Use this template exactly. Keep key names unchanged for downstream parsing.

```markdown
---
version: 1
run_date: <YYYY-MM-DD>
run_time_local: <YYYY-MM-DD HH:mm TZ>
mode: <daily|daily_minimal|full_report>
ticker: <TICKER>
exchange: <EXCHANGE>
market: <TEXT>
report_dir: <working_directory>/daily-stock-analysis/reports/
output_file: <YYYY-MM-DD-TICKER-analysis.md or -vN.md>
report_versioning_mode: <overwrite|new_version>
history_window_days: <N>

recommendation: <Buy|Hold|Sell|Watch>
recommendation_triggers: <ENTRY/EXIT/INVALIDATION SUMMARY>

pred_close_t1: <NUMBER>
pred_range_t1: <LOW-HIGH or N/A>
pred_confidence: <High|Medium|Low>
pred_assumptions: <SHORT TEXT>

prev_pred_close_t1: <NUMBER or N/A>
prev_actual_close_t1: <NUMBER or pending or N/A>
AE: <NUMBER or N/A>
APE: <PERCENT or N/A>
strict_hit: <true|false|N/A>
loose_hit: <true|false|N/A>

acc_1d_strict: <PERCENT or N/A>
acc_1d_loose: <PERCENT or N/A>
acc_3d_strict: <PERCENT or N/A>
acc_3d_loose: <PERCENT or N/A>
acc_7d_strict: <PERCENT or N/A>
acc_7d_loose: <PERCENT or N/A>
acc_30d_strict: <PERCENT or N/A>
acc_30d_loose: <PERCENT or N/A>
acc_custom_strict: <PERCENT or N/A>
acc_custom_loose: <PERCENT or N/A>

improvement_actions:
  - <ACTION_1>
  - <ACTION_2 or N/A>
  - <ACTION_3 or N/A>
status: <ok|pending_data|blocked>
status_note: <SHORT TEXT>
---

# Daily Stock Analysis - <TICKER> (<EXCHANGE>)

## 1) Market Snapshot
- Last/Close: <VALUE>
- Session Range: <LOW-HIGH>
- Volume/Volatility: <SUMMARY>
- Thesis: <BULLISH/NEUTRAL/BEARISH + concise rationale>

## 2) Recommendation
- Recommendation: <Buy/Hold/Sell/Watch>
- Trigger Conditions: <ENTRY/EXIT/INVALIDATION>
- Risk Controls: <SHORT TEXT>

## 3) Next Trading Day Prediction
- Point Forecast: <pred_close_t1>
- Range: <pred_range_t1>
- Confidence: <pred_confidence>
- Assumptions: <pred_assumptions>

## 4) Prior Forecast Review
- Previous Forecast: <prev_pred_close_t1>
- Actual Close: <prev_actual_close_t1>
- AE / APE: <AE> / <APE>
- Attribution: <WHY HIT OR MISS>

## 5) Rolling Accuracy
| Window | Strict | Loose |
|---|---:|---:|
| 1d | <acc_1d_strict> | <acc_1d_loose> |
| 3d | <acc_3d_strict> | <acc_3d_loose> |
| 7d | <acc_7d_strict> | <acc_7d_loose> |
| 30d | <acc_30d_strict> | <acc_30d_loose> |
| Custom | <acc_custom_strict> | <acc_custom_loose> |

## 6) Self-Improvement Actions for Next Run
1. <ACTION_1>
2. <ACTION_2 or N/A>
3. <ACTION_3 or N/A>

## 7) Sources (with timestamp)
- <SOURCE_1>
- <SOURCE_2>
- <SOURCE_3>

## 8) Disclaimer
This content is for research and informational purposes only and does not constitute investment advice or a return guarantee. Markets are risky; invest with caution.
```
