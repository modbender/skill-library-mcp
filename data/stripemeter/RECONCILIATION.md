# Reconciliation Runbook (Operator Playbook)

Concise, copy-pasteable steps to investigate drift and repair discrepancies between StripeMeter and Stripe. Runnable against local docker-compose.

## Policy

- Drift epsilon: 0.5% relative difference per subscription item per period
- Within epsilon (≤ 0.5%): record a small adjustment to align and proceed
- Beyond epsilon (> 0.5%): backfill late/missing events, then re-run aggregation

## Core mechanics (how the system behaves)

- Watermarks: each counter tracks a last-processed timestamp; late events within the window trigger re-aggregation
- Delta push: writer sends only the delta from `pushed_total` per Stripe item (idempotent)
- Reconciliation loop: periodically compares local totals vs Stripe reported usage and flags items beyond epsilon

---

## Triage Runbook

### 0) Prerequisites (local)

```bash
# Bring up infra
docker compose -f docker-compose.yml up -d

# Start app stack (in another terminal)
pnpm -r build && pnpm dev
```

Optional monitoring stack:

```bash
docker compose -f docker-compose.prod.yml --profile monitoring up -d
# Prometheus: http://localhost:${PROMETHEUS_PORT:-9090}
# Grafana:    http://localhost:${GRAFANA_PORT:-3001}  (admin/admin by default)
```

### 1) Verify service health and scrape status

```bash
# API health
curl -fsS http://localhost:3000/health/ready | jq .

# API metrics are exposed for Prometheus
curl -fsS http://localhost:3000/metrics | head -n 20

# If monitoring profile is enabled, check Prometheus targets
open "http://localhost:9090/targets" || echo "Open http://localhost:9090/targets"
```

Expected: `/health/ready` returns `healthy` or `degraded`; `/metrics` includes `http_requests_total` and `http_request_duration_seconds_bucket`.

### 2) Inspect drift metrics and logs

Prometheus queries (paste into Prometheus/Grafana):

```
# Percentage drift by item and period
max_over_time(reconciliation_diff_pct[15m])

# Absolute drift by item and period
max_over_time(reconciliation_diff_abs[15m])

# Reconciliation run cadence and latency
increase(recon_runs_total[1h])
histogram_quantile(0.95, sum(rate(recon_duration_seconds_bucket[5m])) by (le))

# Ingest p95 latency for /v1/events/ingest
histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{route="/v1/events/ingest"}[5m])))

# HTTP 5xx rate by route
sum by (route) (rate(http_requests_total{status_code=~"5.."}[5m]))
```

Logs (newest last):

```bash
docker logs -n 200 -f stripemeter-api | sed -n '1,120p'
docker logs -n 200 -f stripemeter-workers | sed -n '1,120p'
```

### 3) Identify the affected item

Gather: `tenantId`, `customerRef`, `metric`, and billing period.

```bash
# Quick period summary (demo endpoint)
curl -s "http://localhost:3000/v1/reconciliation/summary?tenantId=demo&metric=requests" | jq .
```

### 4) Re-aggregate a window (safe retry/backoff)

Use the Replay API to recompute counters over a time window. Always run a dry-run first.

```bash
# Dry-run last 24h for one metric
curl -s -X POST http://localhost:3000/v1/replay \
  -H 'Content-Type: application/json' \
  -d '{
    "tenantId": "demo",
    "metrics": ["requests"],
    "since": "-PT24H",
    "until": "now",
    "mode": "dry-run"
  }' | jq .

# Apply if the dry-run looks correct (idempotent)
curl -s -X POST http://localhost:3000/v1/replay \
  -H 'Content-Type: application/json' \
  -d '{
    "tenantId": "demo",
    "metrics": ["requests"],
    "since": "-PT24H",
    "until": "now",
    "mode": "apply"
  }' | jq .
```

Guidance:
- Safe to retry with exponential backoff (e.g., 5s, 15s, 30s) if queues are busy; the writer is delta/idempotent
- Expected time: re-aggregation of ~10k late events ≤ 2 s on a laptop

### 5) Targeted replays

Narrow the blast radius by period or customer where needed.

```bash
# Replay a specific period
curl -s -X POST http://localhost:3000/v1/replay \
  -H 'Content-Type: application/json' \
  -d '{
    "tenantId": "demo",
    "metrics": ["requests"],
    "since": "2025-01-01T00:00:00Z",
    "until": "2025-02-01T00:00:00Z",
    "mode": "dry-run"
  }' | jq .
```

### 6) Confirm resolution

```bash
# Reconciliation summary should show drift back within epsilon
curl -s "http://localhost:3000/v1/reconciliation/summary?tenantId=demo&metric=requests" | jq .

# Optionally trigger a reconciliation cycle
curl -s -X POST http://localhost:3000/v1/reconciliation/run -H 'Content-Type: application/json' \
  -d '{"tenantId":"demo"}' | jq .
```

If still beyond epsilon: inspect raw events and watermarks, then repeat step 4 with a wider window.

---

## Common pitfalls

- Tenant or metric mismatch (e.g., wrong `tenantId` or unconfigured metric mapping)
- Timezone boundaries causing the wrong billing period window
- Events arriving after the lateness window → require adjustments instead of automatic re-aggregation
- Missing Stripe secrets or permissions block writer parity
- Placeholder drift gauges (`reconciliation_diff_*`) not yet wired in your environment

## Examples

- Late event (< 48h): falls within lateness window, re-aggregate; if residual diff ≤ 0.5%, adjust.
- Duplicate event: idempotency key should dedupe; if not, create a negative adjustment.

## References & dashboards

- Health and metrics: `GET /health/ready`, `GET /metrics`
- Replay API: `POST /v1/replay` (dry-run → apply)
- Reconciliation: `GET /v1/reconciliation/summary`, `POST /v1/reconciliation/run`
- Alerts and “what to do next”: see `ops/ALERTS.md`
