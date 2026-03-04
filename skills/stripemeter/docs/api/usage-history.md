# API — Usage History (v0.3.0)

[← Back to Welcome](../welcome.md)

GET /v1/usage/history

Query Parameters
- `tenantId` (string, required)
- `metric` (string, required)
- `customerRef` (string, optional)
- `since` (ISO 8601 or relative, optional)
- `until` (ISO 8601 or "now", optional)
- `interval` (string, optional; one of minute|hour|day; default day)

Response
```json
{
  "tenantId": "demo",
  "metric": "requests",
  "timeRange": {
    "since": "2025-01-15T00:00:00Z",
    "until": "2025-01-16T00:00:00Z",
    "interval": "hour"
  },
  "series": [
    { "ts": "2025-01-15T00:00:00Z", "value": 120 },
    { "ts": "2025-01-15T01:00:00Z", "value": 98 }
  ],
  "totals": {
    "value": 5230
  }
}
```

Examples
```bash
# Hourly time-series plus totals
curl -s "http://localhost:3000/v1/usage/history?tenantId=demo&metric=requests&since=-P1D&interval=hour" | jq
```

Notes
- Use this alongside Replay to visualize before/after counters
- `interval` controls aggregation bucket size
