---
name: umami-stats
description: Query Umami Cloud (v2) analytics data via API using an environment-provided API key. Use when agents need website traffic, pages, events, sessions, realtime, reports, or attribution data for analysis, planning, experiments, or monitoring. Includes read-only API querying patterns, endpoint selection guidance, and reusable scripts for flexible endpoint + time-range requests.
---

# Umami Stats (Read-only API skill)

Use this skill as a **data-access layer**: fetch Umami analytics data, then let the agent decide analysis/strategy.

## Required environment variables

- `UMAMI_API_KEY` (required)
- `UMAMI_BASE_URL` (optional, default: `https://api.umami.is`)
- `UMAMI_WEBSITE_ID` (optional default site)
- `UMAMI_DEPLOYMENT` (optional: `cloud` or `self-hosted`, default: `cloud`)

## API path conventions (explicit)

- **Umami Cloud:** `https://api.umami.is/v1/...`
- **Self-hosted Umami:** `https://<your-host>/api/...`

The script supports both:
- `--deployment cloud` → uses cloud behavior (`/v1` + `x-umami-api-key`)
- `--deployment self-hosted` → uses self-hosted behavior (`/api` + `Authorization: Bearer ...`)

## Read-only workflow

1. Pick endpoint from docs or `references/read-endpoints.md`.
2. Run `scripts/umami_query.py` with endpoint + params.
3. Use presets (`today`, `last7d`, etc.) or custom `startAt`/`endAt`.
4. Analyze returned JSON for the user task.

## Quick commands

```bash
# 1) List websites
python3 scripts/umami_query.py --endpoint /v1/websites

# 2) Website stats for last 7 days (default website from env)
python3 scripts/umami_query.py \
  --endpoint /v1/websites/{websiteId}/stats \
  --preset last7d

# 3) Top pages with explicit website id
python3 scripts/umami_query.py \
  --endpoint /v1/websites/{websiteId}/pageviews \
  --website-id "$UMAMI_WEBSITE_ID" \
  --preset last30d

# 4) Events series with custom window
python3 scripts/umami_query.py \
  --endpoint /v1/websites/{websiteId}/events/series \
  --param startAt=1738368000000 \
  --param endAt=1738972799000

# 5) Legacy path auto-mapping in cloud mode (/api/... -> /v1/...)
python3 scripts/umami_query.py --endpoint /api/websites/{websiteId}/stats --preset last7d

# 6) Self-hosted example (/v1/... auto-maps to /api/...)
python3 scripts/umami_query.py \
  --deployment self-hosted \
  --base-url "https://umami.example.com" \
  --endpoint /v1/websites/{websiteId}/stats \
  --preset last7d
```

## Natural trigger examples

- “How was traffic this week?”
- “Top pages in the last 30 days”
- “Show event trends for signup clicks”
- “Compare current week vs previous week”
- “Give me raw Umami data to build a marketing experiment plan”

## Notes

- Keep requests **read-only** (`GET`).
- Prefer explicit time windows for reproducibility.
- For unknown endpoints, consult `https://v2.umami.is/docs/api` and then query with the script.
- Prefer `/v1/...` endpoints in cloud mode, `/api/...` in self-hosted mode.
- Auth headers are mode-specific: cloud uses `x-umami-api-key`; self-hosted uses `Authorization: Bearer ...`.
- `metrics` endpoints require a `type` query param. The script now auto-defaults to `type=url` if omitted.
- For `/v1/reports/*` endpoints, the script auto-adds `websiteId` from `--website-id` / `UMAMI_WEBSITE_ID` when available.
- On Umami Cloud, `/v1/users/*` endpoints can return 403 for normal user API keys (expected in many accounts).

## Resources

- Endpoint map: `references/read-endpoints.md`
- Query helper: `scripts/umami_query.py`
