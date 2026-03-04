# Beaconcha.in API Notes (Dashboard Monitoring Foundation)

## Auth

Use header:

`Authorization: Bearer <API_KEY>`

## Dashboard selector pattern (V2)

Most validator analytics endpoints accept:

```json
{
  "chain": "mainnet",
  "validator": { "dashboard_id": 123 }
}
```

Optional:

```json
"range": { "evaluation_window": "24h" }
```

## Endpoints used by this foundation

Primary:
- `POST /api/v2/ethereum/validators/performance-aggregate`

This endpoint directly returns dashboard-level BeaconScore (`data.beaconscore.total`) and duty-miss stats, which makes it ideal for low-anxiety daily checks.

Optional secondary (for deep dives):
- `POST /api/v2/ethereum/validators/performance-list` (per-validator/per-epoch details)

## Why this foundation works

- Keeps API surface area small.
- Supports dashboard-level checks (not per-validator micromanagement).
- Enables one daily “am I good?” status for anxiety reduction.

## Next iteration ideas

- Add dedicated endpoint once BeaconScore field/path is confirmed in your account response.
- Add cron wrapper for daily scheduled checks + issue-only notifications.
- Add group-level checks via `group_id` when needed.
