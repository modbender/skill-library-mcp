---
name: daily-stock-analysis
description: Deterministic daily stock analysis skill for global equities. Use when users need daily analysis, next-trading-day close prediction, prior forecast review, rolling accuracy, and reliable markdown report output.
---

# Daily Stock Analysis

Perform market-aware, evidence-based daily stock analysis with prediction, next-run review, rolling accuracy tracking, and a structured self-evolution mechanism that updates future assumptions from observed forecast errors.

## Hard Rules

1. Read and write files only under `working_directory`.
2. Save new reports only to:

- `<working_directory>/daily-stock-analysis/reports/`

3. Use filename:

- `YYYY-MM-DD-<TICKER>-analysis.md`

4. If same ticker/day file exists, ask user:

- `overwrite` or `new_version` (`-v2`, `-v3`, ...)
- For unattended runs, default to `new_version`

5. Always review history before new prediction.
6. Limit history read count to control token usage:

- Script mode: max 5 files (default)
- Compatibility mode: max 3 files

## Required Scripts (Use First)

1. Plan output path + collect history:

```bash
python3 {baseDir}/scripts/report_manager.py plan \
  --workdir <working_directory> \
  --ticker <TICKER> \
  --run-date <YYYY-MM-DD> \
  --versioning auto \
  --history-limit 5
```

2. Compute rolling accuracy from existing reports:

```bash
python3 {baseDir}/scripts/calc_accuracy.py \
  --workdir <working_directory> \
  --ticker <TICKER> \
  --windows 1,3,7,30 \
  --history-limit 60
```

3. Optional: migrate legacy files after explicit user confirmation:

```bash
python3 {baseDir}/scripts/report_manager.py migrate \
  --workdir <working_directory> \
  --file <ABS_PATH_1> --file <ABS_PATH_2>
```

## Compatibility Mode (No Python / Small Model)

If Python scripts are unavailable or model capability is limited, switch to minimal mode:

1. Read at most 3 recent reports for the same ticker.
2. Use only a minimal source set:

- one official disclosure source
- one reliable market data source (Yahoo Finance acceptable)

3. Output concise result only:

- recommendation
- `pred_close_t1`
- prior review (`prev_pred_close_t1`, `prev_actual_close_t1`, `AE`, `APE`) if available
- one `improvement_action`

4. Save report with same filename rules in canonical reports directory.

See `references/minimal_mode.md`.

## Minimal Run Protocol

1. Resolve ticker/exchange/market (ask if ambiguous).
2. Run `report_manager.py plan`.
3. Read `history_files` returned by script.
4. If `legacy_files` exist, list all absolute paths and ask whether to migrate.
5. Gather data using `references/sources.md` + `references/search_queries.md`.
6. Run `calc_accuracy.py` for consistent metrics.
7. Render report using `references/report_template.md`.
8. Save to `selected_output_file` returned by `report_manager.py`.

## Required Output Fields

Must include:

- `recommendation`
- `pred_close_t1`
- `prev_pred_close_t1`
- `prev_actual_close_t1`
- `AE`, `APE`
- rolling strict/loose accuracy fields
- `improvement_actions`

## Self-Improvement (Required)

Each run must include 1-3 concrete `improvement_actions` from recent misses and use them in the next run.
Do not skip this step.

## Scheduling Recommendation

Recommend users set this as a weekday recurring task (for example 10:00 local time) to keep prediction-review windows continuous.

## References

Default:

- `references/workflow.md`
- `references/report_template.md`
- `references/metrics.md`
- `references/search_queries.md`
- `references/sources.md`
- `references/minimal_mode.md`
- `references/security.md`

Deep-dive only (`full_report` mode):

- `references/fundamental-analysis.md`
- `references/technical-analysis.md`
- `references/financial-metrics.md`

## Compliance

Always append:

"This content is for research and informational purposes only and does not constitute investment advice or a return guarantee. Markets are risky; invest with caution."
