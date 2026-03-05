# Rails Agent Gateway Usage Reference

## Minimal health check

### Via curl

```bash
curl -H "Authorization: Bearer $AGENT_GATEWAY_TOKEN" \
  "https://myapp.com/agent-gateway/$AGENT_GATEWAY_SECRET/briefing?period=7d&resources=users&latest=1"
```

### Via helper script

```bash
RAILS_GATEWAY_URL='https://myapp.com/agent-gateway/<secret>/briefing' \
RAILS_GATEWAY_TOKEN='***' \
/home/node/.openclaw/workspace/scripts/rails-gateway-briefing --period 7d --resources users --latest 1
```

## Expected response shape

```json
{
  "app_name": "MyApp",
  "generated_at": "2026-02-20T12:00:00Z",
  "period": { "from": "2026-02-13", "to": "2026-02-20", "days": 7 },
  "data": {
    "users": {
      "count": 142,
      "latest": [{ "email": "new@example.com", "name": "New User", "created_at": "2026-02-20" }]
    },
    "orders": {
      "count": 89,
      "sum": { "total": 12450.0 },
      "avg": { "total": 139.89 },
      "latest": [{ "id": 501, "total": "250.00", "status": "paid", "created_at": "2026-02-20" }]
    }
  }
}
```

Key fields:

- `app_name`, `generated_at`, `period` — top-level metadata
- `data.<resource>.count` — record count
- `data.<resource>.sum` / `data.<resource>.avg` — aggregations (if configured)
- `data.<resource>.latest[]` — most recent records with allowlisted attributes

## Common pull profiles

### Daily summary

```bash
/home/node/.openclaw/workspace/scripts/rails-gateway-briefing --period 1d --resources users,orders --latest 5
```

### Weekly digest

```bash
/home/node/.openclaw/workspace/scripts/rails-gateway-briefing --period 7d --resources users,orders --latest 10
```

### Full history

```bash
/home/node/.openclaw/workspace/scripts/rails-gateway-briefing --period all --resources users,orders --latest 20
```

## Period values

`1d`, `7d`, `30d`, `90d`, `1y`, `all`

## Error triage map

- `Missing env vars` → set `AGENT_GATEWAY_TOKEN` and `AGENT_GATEWAY_SECRET`
- `401` → bearer token invalid/expired (`AGENT_GATEWAY_TOKEN`)
- `404` → path secret wrong or endpoint path incorrect (`AGENT_GATEWAY_SECRET`)
- `timeout/network` → host reachability/TLS/DNS issue
- malformed JSON → server response not in briefing format

## Output summary template

Use concise summaries:

- Period: `<from> → <to>`
- Users: `<count>` (latest: `<name/email/date>`)
- Orders: `<count>`, sum: `<total>`, avg: `<avg>` (latest: `<id/status/date>`)

Avoid dumping full payload unless user asks.
