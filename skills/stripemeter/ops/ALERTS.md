## Alerting Rules (Prometheus)

This document defines baseline alerting rules for StripeMeter. Each alert includes a brief next action.

Copy the rules block into your Prometheus `rule_files` and run `promtool check rules` before applying.

```yaml
groups:
  - name: stripemeter.rules
    rules:
      # Drift absolute exceeds epsilon for 15 minutes
      - alert: ReconciliationDriftAbsHigh
        expr: max_over_time(reconciliation_diff_abs[15m]) > 0.0
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Reconciliation absolute drift above epsilon"
          description: "Absolute drift between local and Stripe exceeds epsilon for 15m. value={{ $value }}"
          runbook: "Inspect reconciliation reports; follow RECONCILIATION.md steps 1–4."

      # Drift percentage exceeds threshold for 15 minutes
      - alert: ReconciliationDriftPctHigh
        expr: max_over_time(reconciliation_diff_pct[15m]) > 0.005
        for: 15m
        labels:
          severity: critical
        annotations:
          summary: "Reconciliation percentage drift above threshold"
          description: "Percentage drift (|local - stripe| / stripe) > 0.5% for 15m. value={{ $value }}"
          runbook: "Backfill or adjust per RECONCILIATION.md for affected item(s)."

      # Queue lag above threshold (requires exporter of BullMQ/Redis lag)
      - alert: IngestionQueueLagHigh
        expr: max_over_time(queue_lag_seconds{queue=~"aggregation|writer"}[15m]) > 60
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Queue lag over 60s"
          description: "Background queue lag above 60s for 15m. value={{ $value }}"
          runbook: "Check Redis, worker replicas, backlog; scale workers or unstick jobs."

      # Ingest latency p95 above SLO
      - alert: IngestLatencyHighP95
        expr: histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket{route="/v1/events/ingest"}[5m]))) > 0.2
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Ingest p95 latency over 200ms"
          description: "POST /v1/events/ingest p95 > 200ms for 15m. value={{ $value }}"
          runbook: "Check API/DB/Redis; scale API or tune batch sizes."

      # HTTP 5xx rate above threshold
      - alert: Http5xxRateHigh
        expr: sum by (route) (rate(http_requests_total{status_code=~"5.."}[5m])) > 0.1
        for: 15m
        labels:
          severity: critical
        annotations:
          summary: "HTTP 5xx rate high"
          description: "5xx error rate > 0.1 req/s over 5m for 15m. route={{ $labels.route }} value={{ $value }}"
          runbook: "Check deploys/logs/upstreams; roll back or hotfix."
```

Notes
- Metrics used are based on built-in exporters:
  - `http_request_duration_seconds_bucket`, `http_requests_total` from API
  - `reconciliation_diff_abs`, `reconciliation_diff_pct` are placeholders; wire to reconciler metrics or Redis-exported gauges.
  - `queue_lag_seconds` is a placeholder for BullMQ/Redis consumer lag. Add an exporter or custom gauge.
- Coordinate thresholds with `RECONCILIATION.md` and production SLOs in `project-principles.md`.

### Alertmanager Example

See `ops/alertmanager/alertmanager.yml` for a minimal route/receiver.


### What to do next (Runbook)

When any reconciliation alert fires, follow the operator playbook:

- Read `RECONCILIATION.md` → Steps 1–6 (verify health, inspect drift, replay window, confirm resolution)
- Use copy-paste commands for `/metrics`, Replay API, and reconciliation summary
- Validate drift is back within epsilon (≤ 0.5%) before closing the alert


