# Metrics Definition

Use these definitions consistently across all reports.

## 1. Core Error Metrics

Let:

- `pred` = predicted close for target session
- `actual` = official actual close for that session

Compute:

- Absolute Error (AE): `|pred - actual|`
- Absolute Percentage Error (APE): `|pred - actual| / actual * 100%`

## 2. Hit Criteria

Report two hit criteria in parallel:

- Strict hit: `APE <= 1%`
- Loose hit: `APE <= 2%`

These thresholds are the default correctness criteria for predicted close price.

## 3. Rolling Accuracy Windows

For each window `W` (1d, 3d, 7d, 30d, custom):

- `strict_accuracy_W = strict_hits_W / n_W`
- `loose_accuracy_W = loose_hits_W / n_W`

Where `n_W` is number of valid forecast/actual pairs in that window.

## 4. Optional Direction Accuracy

Let direction be sign of close-to-close return.

- Direction hit if predicted direction equals realized direction.
- `direction_accuracy_W = direction_hits_W / n_W`

Use only when direction labels are explicitly available.

## 5. Forecast Correctness Score (Optional)

For a single forecast, you may map APE to a score:

- `correctness_score = max(0, 100 - 50 * APE_percent)`

Examples:

- `APE = 0.8%` -> score `60`
- `APE = 1.5%` -> score `25`
- `APE >= 2.0%` -> score `0` (or near 0)

## 6. Sample Size and Insufficient Data Rules

1. Never pad missing samples.
2. If `n_W = 0`, output `N/A` for the window.
3. If `0 < n_W < target_window_size`, output partial result and annotate as partial.
4. Always display `n_W` beside each window metric.

## 7. Adjustment and Comparability Rules

1. Prefer adjusted price series when corporate actions materially affect comparability.
2. If non-adjusted close is used, state it explicitly.
3. Keep forecast and actual on the same price basis.

## 8. Improvement Trend Metrics

Track whether forecast quality is improving over time:

1. `delta_APE_7d_vs_prev7d`
- Difference between current 7-day average APE and previous 7-day average APE.

2. `delta_strict_hit_rate_7d`
- Change in strict hit rate versus previous 7-day block.

3. `trend_label`
- `improving`, `stable`, or `degrading` based on combined delta signals.

## 9. Reporting Format (Minimum)

Every report should include:

1. Prior-session review row:
- `prev_pred_close_t1`, `prev_actual_close_t1`, `AE`, `APE`, strict/loose hit status

2. Rolling table with at least:
- 1d, 3d, 7d, 30d, optional custom
- strict accuracy, loose accuracy, optional direction accuracy
- sample size `n`

3. One-line interpretation:
- whether model performance is improving, stable, or degrading

4. Improvement block:
- what changed from review
- what will be adjusted in next run
