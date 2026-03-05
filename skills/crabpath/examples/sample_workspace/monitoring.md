# Monitoring

## Alerts
- Error rate > 1% → page on-call
- Latency p99 > 2s → warning in #ops
- Memory usage > 80% → investigate

## Dashboards
- Production health: grafana.internal/prod
- Error tracking: sentry.internal
- Logs: kibana.internal

## On-Call Rotation
- Week 1: Alice
- Week 2: Bob
- Week 3: Carol
