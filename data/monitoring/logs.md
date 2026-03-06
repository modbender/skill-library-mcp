# Centralized Logging

## Why Centralize Logs

| Problem | Solution |
|---------|----------|
| SSH to each server to find logs | One query, all servers |
| Logs rotated before investigation | Configurable retention |
| Can't correlate across services | Request IDs, unified search |
| No audit trail | Immutable log storage |

## Stack Options

### Loki + Grafana (Lightweight)

**Best for:** Teams already using Grafana, smaller volumes, simplicity.

```yaml
# docker-compose.yml
services:
  loki:
    image: grafana/loki:2.9.0
    ports:
      - "3100:3100"
    volumes:
      - ./loki-config.yaml:/etc/loki/local-config.yaml
      - loki_data:/loki

  promtail:
    image: grafana/promtail:2.9.0
    volumes:
      - /var/log:/var/log:ro
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      - ./promtail-config.yaml:/etc/promtail/config.yml
```

**Pros:** Light on resources, label-based like Prometheus, integrates with Grafana.
**Cons:** Doesn't index log content (queries on text are slower).

### ELK Stack (Powerful)

**Best for:** Complex queries, full-text search, large volumes.

**Cons:** Resource heavy (4GB+ RAM for Elasticsearch), more operational complexity.

### Managed Options

| Service | Best For | Pricing |
|---------|----------|---------|
| **Grafana Cloud** | Loki users, Grafana ecosystem | Free → $50+/mo |
| **CloudWatch** | AWS-native | $0.50/GB ingested |
| **Papertrail** | Quick setup, small teams | Free → $7+/mo |
| **Better Stack** | Modern UI, fast | Free → $24+/mo |

## Structured Logging

**Bad:**
```
User 123 logged in from 192.168.1.1
```

**Good:**
```json
{"event": "user_login", "user_id": 123, "ip": "192.168.1.1", "timestamp": "2024-01-15T10:30:00Z"}
```

### Implementation

```javascript
// Use a structured logger
import pino from 'pino';

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => ({ level: label }),
  },
});

// Good
logger.info({ userId: 123, action: 'login', ip: req.ip }, 'User logged in');

// Bad
logger.info(`User ${userId} logged in from ${req.ip}`);
```

### Request IDs

Add a unique ID to every request, log it everywhere:

```javascript
// Middleware
app.use((req, res, next) => {
  req.id = req.headers['x-request-id'] || crypto.randomUUID();
  res.setHeader('x-request-id', req.id);
  next();
});

// In logs
logger.info({ requestId: req.id, userId }, 'Processing payment');
```

Now you can trace a request across all services.

## Log Levels

| Level | When to Use | Example |
|-------|-------------|---------|
| **error** | Something failed, needs attention | Database connection lost |
| **warn** | Unexpected but handled | Retry succeeded after failure |
| **info** | Normal operations | User signed up, order placed |
| **debug** | Troubleshooting detail | Request payload, cache hit/miss |

**In production:** `info` and above.
**When debugging:** Temporarily enable `debug`.

## Retention Strategy

| Log Type | Retention | Why |
|----------|-----------|-----|
| Error logs | 90 days | Debugging, postmortems |
| Access logs | 30 days | Security, analytics |
| Debug logs | 7 days | Troubleshooting only |
| Audit logs | 1+ years | Compliance |

## Useful Queries

### Loki (LogQL)
```logql
# Errors in last hour
{job="app"} |= "error" | json | level="error"

# Slow requests (>1s)
{job="app"} | json | duration > 1000

# Errors by service
sum by (service) (count_over_time({job="app"} |= "error" [1h]))
```

### Elasticsearch
```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "level": "error" }},
        { "range": { "@timestamp": { "gte": "now-1h" }}}
      ]
    }
  }
}
```

## Alerting on Logs

```yaml
# Loki ruler config
groups:
  - name: log-alerts
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate({job="app"} |= "error" [5m])) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate in logs"
```
