# Operations and execution

## Suggested execution cadence

- Hourly: last hour, run with a small delay (e.g., minute 15).
- Daily: previous day after midnight (e.g., 01:30).
- Weekly: previous week, e.g. Monday 02:00.
- Monthly: previous month, day 1 at 03:00.
- Sleep: last 30h, run morning and/or night.
- Cross-alerts: use outputs from hourly/daily/weekly/monthly/sleep.

## Data quality rules

- `rel=high`: n_instances >= 20 and source complete.
- `rel=medium`: n_instances 5-19 or partial data.
- `rel=low`: n_instances < 5 or important caveats.
- `rel=unavailable`: no data or not computable.

## Outputs

All scripts emit JSON to stdout and optionally write files via `--output-dir`.
