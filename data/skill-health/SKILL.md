---
name: skill-health
description: "Analyze wearable health CSV exports (steps, heart rate, sleep, calories, SpO2, exercise, distance) and produce compact JSON reports for hourly, daily, weekly, monthly, sleep (last 30h) and cross-temporal alerts. Use when running or packaging Skill Health analyses and when explaining output semantics, data quality, or known caveats."
---

# Skill Health

## Use

Run analysis scripts from `scripts/` with a `--data-path` (ZIP or folder) or `--data-dir` (directory holding health_data_*). Each script prints JSON to stdout and can also write a file with `--output-dir`.

Minimal examples:

```bash
python scripts/run_sleep.py --data-path data/health_data_latest.zip --output-dir outputs
python scripts/run_daily.py --data-path data/health_data_latest.zip --output-dir outputs
python scripts/run_cross_alerts.py --outputs-dir outputs --output-dir outputs
```

## Notes

- Sleep metrics use suffix `last_{window_hours}h` (default `last_30h`).
- Outputs are compact JSON (`time_window` uses `s/e/r`, `data_quality` uses `cov/rel`).
- Dependencies: Python 3.10+ and `pandas`.

## References

- `references/overview.md` (data schemas, outputs, key decisions)
- `references/operations.md` (execution windows, quality rules)
