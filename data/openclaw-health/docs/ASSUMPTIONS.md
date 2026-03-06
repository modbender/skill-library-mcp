Assumptions and Scope

- This initial version prioritizes a working local CLI with sane fallbacks over perfect coverage.
- Connectors attempt to read credentials from 1Password via the `op` CLI if present, else environment variables, else return null metrics with an error.
- When credentials exist, connectors attempt **live API calls by default**.
  - Set `OPENCLAW_FORCE_SAMPLE=1` to force sample output (useful for offline/test environments).
- Normalized schema is intentionally small and will evolve. Unknown or unavailable fields are left as `null`.
- Dates use local date strings `YYYY-MM-DD` and are interpreted as full-day windows.
- The output location defaults to the repo root for `daily_health.json`. You can pass `--out` to change it.
