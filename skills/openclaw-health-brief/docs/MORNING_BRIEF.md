Morning Brief

Summary
- CLI: `./bin/health-brief --date YYYY-MM-DD [--out path] [--sources S1,S2]`
- Orchestrates connectors, normalizes data, writes `daily_health.json`, and prints a Markdown summary.

Sources: `whoop`, `oura`, `withings`.
Normalization Schema (simplified)
- date: string (YYYY-MM-DD)
- sources: { whoop?, oura?, withings? }
- metrics:
  - sleep: { total_seconds?, score? }
  - readiness: { score? }
  - activity: { steps?, calories?, minutes? }
  - resting_hr: number?
  - hrv_rmssd: number?
  - respiratory_rate: number?
  - spo2: number?
  - weight_kg: number?
  - body_fat_percent: number?

Examples
- `./bin/health-brief --date 2025-01-15`
- `./bin/health-brief --date 2025-01-15 --sources oura`
- `./bin/health-brief --date 2025-01-15 --out ./out/daily.json`

Notes
- If no credentials are available, connectors return null metrics and an error block. No data is fabricated.
- Add `--verbose` to see which sources contributed each metric.

