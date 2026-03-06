# Monitoring & Observability

## Logging Best Practices

```typescript
import pino from 'pino'

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => ({ level: label }),
  },
})

// Structured logging
logger.info({ userId: '123', action: 'login' }, 'User logged in')
logger.error({ err, userId: '123' }, 'Login failed')
```

## Metrics vs Traces vs Logs

| Type | Purpose | Example |
|------|---------|---------|
| Metrics | Aggregated numbers | Request count, latency p95 |
| Traces | Request flow | Full request path |
| Logs | Events | Error details |

## Alert Design

```yaml
# Alert rules
- alert: HighErrorRate
  expr: sum(rate(http_requests_total{status=~"5.."}[5m])) > 0.05
  for: 5m
  labels:
    severity: critical
  annotations:
    description: Error rate > 5%
```

## Checklist

- [ ] Use structured logging (JSON)
- [ ] Add request IDs for tracing
- [ ] Create key metrics (latency, error rate, throughput)
- [ ] Set up health checks
- [ ] Configure alerting thresholds
- [ ] Build dashboards
