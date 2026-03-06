---
name: afrexai-observability-engine
model: standard
description: Complete observability & reliability engineering system. Use when designing monitoring, implementing structured logging, setting up distributed tracing, building alerting systems, creating SLO/SLI frameworks, running incident response, conducting post-mortems, or auditing system reliability. Covers all three pillars (logs/metrics/traces), alert design, dashboard architecture, on-call operations, chaos engineering, and cost optimization.
version: 1.0.0
tags: observability, monitoring, logging, tracing, alerting, SRE, incident-response, SLO, metrics, devops, reliability, on-call, post-mortem, dashboards
---

# Observability & Reliability Engineering

Complete system for building observable, reliable services — from structured logging to incident response to SLO-driven development.

---

## Quick Health Check (/16)

Score your current observability posture:

| Signal | Healthy (2) | Weak (1) | Missing (0) |
|--------|-------------|----------|-------------|
| Structured logging | JSON logs with trace_id correlation | Logs exist but unstructured | Console.log / print statements |
| Metrics collection | RED/USE metrics with dashboards | Some metrics, no dashboards | No metrics |
| Distributed tracing | Full request path with sampling | Partial traces, key services only | No tracing |
| Alerting | SLO-based alerts with runbooks | Threshold alerts, some runbooks | No alerts or all-noise |
| Incident response | Defined process with roles + post-mortems | Ad-hoc response, some docs | "Whoever notices fixes it" |
| SLOs defined | SLOs with error budgets tracked weekly | Informal availability targets | No reliability targets |
| On-call rotation | Structured rotation with escalation | Informal "call someone" | No on-call |
| Cost management | Observability budget tracked monthly | Some awareness of costs | No idea what you spend |

**12-16:** Production-grade. Focus on optimization.
**8-11:** Foundation exists. Fill the gaps systematically.
**4-7:** Significant risk. Prioritize alerting + incident response.
**0-3:** Flying blind. Start with Phase 1 immediately.

---

## Phase 1: Structured Logging

### Log Architecture

```
Application → Structured JSON → Log Router → Storage → Query Engine
                                    ↓
                              Alert Pipeline
```

### Required Fields (Every Log Line)

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| `timestamp` | ISO-8601 UTC | When | `2026-02-22T18:30:00.123Z` |
| `level` | enum | Severity | `info`, `warn`, `error`, `fatal` |
| `service` | string | Which service | `payment-api` |
| `version` | string | Which deploy | `v2.3.1` |
| `environment` | string | Which env | `production` |
| `message` | string | What happened | `Payment processed successfully` |
| `trace_id` | string | Request correlation | `abc123def456` |
| `span_id` | string | Operation within trace | `span_789` |
| `duration_ms` | number | How long | `142` |

### Contextual Fields (Add Per Domain)

```yaml
# HTTP request context
http:
  method: POST
  path: /api/v1/orders
  status: 201
  client_ip: 203.0.113.42  # Anonymize in logs if needed
  user_agent: "Mozilla/5.0..."
  request_id: "req_abc123"

# Business context
business:
  user_id: "usr_456"
  tenant_id: "tenant_789"
  order_id: "ord_012"
  action: "checkout"
  amount_cents: 4999
  currency: "USD"

# Error context
error:
  type: "PaymentDeclinedError"
  message: "Card declined: insufficient funds"
  code: "CARD_DECLINED"
  stack: "..." # Only in non-production or DEBUG level
  retry_count: 2
  retryable: true
```

### Log Level Decision Tree

```
Is the process about to crash?
  → FATAL (exit after logging)

Did an operation fail that needs human attention?
  → ERROR (page someone or create ticket)

Did something unexpected happen but we recovered?
  → WARN (review in daily triage)

Is this a normal business event worth recording?
  → INFO (audit trail, business metrics)

Is this useful for debugging but noisy in production?
  → DEBUG (off in prod, on in staging)

Is this only useful when stepping through code?
  → TRACE (never in production)
```

### Log Level Rules

1. **ERROR means action required** — if no one needs to act on it, it's WARN
2. **INFO is for business events** — not internal implementation details
3. **No logging inside tight loops** — aggregate and log summary
4. **Log at boundaries** — API entry/exit, queue consume/publish, DB calls
5. **Never log secrets** — API keys, tokens, passwords, PII (see scrubbing below)

### PII & Secret Scrubbing

```yaml
scrub_patterns:
  # Always redact
  - field_patterns: ["password", "secret", "token", "api_key", "authorization"]
    action: replace_with_redacted
  
  # Hash for correlation without exposure
  - field_patterns: ["email", "phone", "ssn", "national_id"]
    action: sha256_hash
  
  # Mask partially
  - field_patterns: ["credit_card", "card_number"]
    action: mask_last_4  # "****-****-****-1234"
  
  # IP anonymization
  - field_patterns: ["client_ip", "ip_address"]
    action: zero_last_octet  # 203.0.113.0
```

### Logger Setup (By Language)

**Node.js (Pino):**
```typescript
import pino from 'pino';
import { AsyncLocalStorage } from 'node:async_hooks';

const als = new AsyncLocalStorage<Record<string, string>>();

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => ({ level: label }),
  },
  mixin: () => als.getStore() ?? {},
  redact: ['req.headers.authorization', '*.password', '*.token'],
  timestamp: pino.stdTimeFunctions.isoTime,
});

// Middleware: inject context
app.use((req, res, next) => {
  const ctx = {
    trace_id: req.headers['x-trace-id'] || crypto.randomUUID(),
    request_id: crypto.randomUUID(),
    service: 'payment-api',
    version: process.env.APP_VERSION,
  };
  als.run(ctx, () => next());
});
```

**Python (structlog):**
```python
import structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.JSONRenderer(),
    ],
)
log = structlog.get_logger()
# Bind context per-request:
structlog.contextvars.bind_contextvars(trace_id=trace_id, user_id=user_id)
```

**Go (zerolog):**
```go
log := zerolog.New(os.Stdout).With().
    Timestamp().
    Str("service", "payment-api").
    Str("version", version).
    Logger()
// Per-request:
reqLog := log.With().Str("trace_id", traceID).Logger()
```

### Log Storage Decision

| Volume | Solution | Retention | Cost |
|--------|----------|-----------|------|
| <10 GB/day | Loki + Grafana | 30 days hot, 90 days cold | Low |
| 10-100 GB/day | Elasticsearch / OpenSearch | 14 days hot, 90 days S3 | Medium |
| 100+ GB/day | ClickHouse or Datadog | 7 days hot, 30 days archive | High |
| Budget-constrained | Loki + S3 backend | 90 days all cold | Very low |

### 10 Logging Anti-Patterns

| # | Anti-Pattern | Fix |
|---|-------------|-----|
| 1 | `log.error(err)` with no context | Always include: what operation, what input, what state |
| 2 | Logging request/response bodies | Log only in DEBUG; redact sensitive fields |
| 3 | String concatenation in log messages | Use structured fields: `log.info("processed", { order_id, amount })` |
| 4 | Catch-and-log-and-rethrow | Log at the boundary where you handle it, not every layer |
| 5 | Different log formats per service | Standardize schema across all services |
| 6 | No log rotation / retention policy | Set max size + TTL; archive to cold storage |
| 7 | Logging inside hot paths | Aggregate: log summary every N items or every interval |
| 8 | Missing correlation IDs | Propagate trace_id from first entry point through all services |
| 9 | Boolean log levels (`verbose: true`) | Use standard levels with configurable minimum |
| 10 | Logging PII in plain text | Implement scrubbing at the logger level |

---

## Phase 2: Metrics Collection

### The RED Method (Request-Driven Services)

For every service endpoint, track:

| Metric | What | Prometheus Example |
|--------|------|--------------------|
| **R**ate | Requests per second | `http_requests_total{method, path, status}` |
| **E**rrors | Failed requests per second | `http_requests_total{status=~"5.."}` / total |
| **D**uration | Latency distribution | `http_request_duration_seconds{method, path}` (histogram) |

### The USE Method (Infrastructure Resources)

For every resource (CPU, memory, disk, network):

| Metric | What | Example |
|--------|------|---------|
| **U**tilization | % resource busy | CPU usage 78% |
| **S**aturation | Queue depth / backpressure | 12 requests queued |
| **E**rrors | Resource errors | 3 disk I/O errors |

### Golden Signals (Google SRE)

| Signal | Meaning | Source |
|--------|---------|--------|
| Latency | Time to serve requests | RED Duration |
| Traffic | Demand on the system | RED Rate |
| Errors | Rate of failed requests | RED Errors |
| Saturation | How "full" the service is | USE Saturation |

### Metric Types & When to Use Each

| Type | Use Case | Example |
|------|----------|---------|
| **Counter** | Things that only go up | Total requests, errors, bytes sent |
| **Gauge** | Current value that goes up/down | Active connections, queue depth, temperature |
| **Histogram** | Distribution of values | Request latency, response size |
| **Summary** | Pre-calculated percentiles | Client-side latency (when you need exact percentiles) |

**Rule:** Use histograms over summaries in most cases — they're aggregatable across instances.

### Naming Conventions

```
# Pattern: <namespace>_<subsystem>_<name>_<unit>
http_server_request_duration_seconds
http_server_requests_total
db_pool_connections_active
queue_messages_pending
cache_hit_ratio

# Rules:
# 1. Use snake_case
# 2. Include unit suffix (_seconds, _bytes, _total)
# 3. _total suffix for counters
# 4. Don't include label names in metric name
# 5. Use base units (seconds not milliseconds, bytes not kilobytes)
```

### Label Design Rules

| Rule | Why | Example |
|------|-----|---------|
| Keep cardinality <100 per label | High cardinality kills performance | `status="200"` not `status="200 OK"` |
| No user IDs as labels | Unbounded cardinality | Use log correlation instead |
| No request paths with IDs | `/api/users/123` creates millions of series | Normalize: `/api/users/:id` |
| Max 5-7 labels per metric | Each combo = a time series | `{method, path, status, service}` |

### Instrumentation Checklist

```yaml
application_metrics:
  # HTTP layer
  - http_request_duration_seconds: histogram {method, path, status}
  - http_request_size_bytes: histogram {method, path}
  - http_response_size_bytes: histogram {method, path}
  - http_requests_in_flight: gauge
  
  # Business logic
  - orders_processed_total: counter {status, payment_method}
  - order_value_dollars: histogram {payment_method}
  - user_signups_total: counter {source}
  
  # Dependencies
  - db_query_duration_seconds: histogram {query_type, table}
  - db_connections_active: gauge {pool}
  - db_connections_idle: gauge {pool}
  - cache_requests_total: counter {result: hit|miss}
  - external_api_duration_seconds: histogram {service, endpoint}
  - external_api_errors_total: counter {service, error_type}
  
  # Queue / async
  - queue_messages_published_total: counter {queue}
  - queue_messages_consumed_total: counter {queue, status}
  - queue_processing_duration_seconds: histogram {queue}
  - queue_depth: gauge {queue}
  - queue_consumer_lag: gauge {queue, consumer_group}

infrastructure_metrics:
  # Node exporter / cAdvisor provides these automatically
  - cpu_usage_percent: gauge {instance}
  - memory_usage_bytes: gauge {instance}
  - disk_usage_bytes: gauge {instance, mount}
  - disk_io_seconds: counter {instance, device}
  - network_bytes: counter {instance, direction}
  - container_cpu_usage: gauge {pod, container}
  - container_memory_usage: gauge {pod, container}
```

### Stack Recommendations

| Component | Options | Recommendation |
|-----------|---------|----------------|
| Collection | Prometheus, OTEL Collector, Datadog Agent | Prometheus (free) or OTEL Collector (vendor-neutral) |
| Storage | Prometheus, Thanos, Mimir, VictoriaMetrics | VictoriaMetrics (best cost/perf) or Mimir (Grafana ecosystem) |
| Visualization | Grafana, Datadog, New Relic | Grafana (free, extensible) |
| Alerting | Alertmanager, Grafana Alerting, PagerDuty | Alertmanager + PagerDuty routing |

---

## Phase 3: Distributed Tracing

### Trace Architecture

```
Client Request
  → API Gateway (root span)
    → Auth Service (child span)
    → Order Service (child span)
      → Database Query (child span)
      → Payment Service (child span)
        → Stripe API (child span)
    → Notification Service (child span)
      → Email Provider (child span)
```

### OpenTelemetry Setup

**Auto-instrumentation (Node.js):**
```typescript
// tracing.ts — import BEFORE anything else
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT || 'http://localhost:4318/v1/traces',
  }),
  instrumentations: [getNodeAutoInstrumentations({
    '@opentelemetry/instrumentation-http': { ignoreIncomingPaths: ['/health', '/ready'] },
    '@opentelemetry/instrumentation-express': { enabled: true },
  })],
  serviceName: process.env.OTEL_SERVICE_NAME || 'payment-api',
});
sdk.start();
```

**Custom spans for business logic:**
```typescript
import { trace, SpanStatusCode } from '@opentelemetry/api';

const tracer = trace.getTracer('payment-service');

async function processPayment(order: Order) {
  return tracer.startActiveSpan('process-payment', async (span) => {
    span.setAttributes({
      'order.id': order.id,
      'order.amount_cents': order.amountCents,
      'payment.method': order.paymentMethod,
    });
    try {
      const result = await chargeCard(order);
      span.setAttributes({ 'payment.status': result.status });
      return result;
    } catch (err) {
      span.setStatus({ code: SpanStatusCode.ERROR, message: err.message });
      span.recordException(err);
      throw err;
    } finally {
      span.end();
    }
  });
}
```

### Sampling Strategies

| Strategy | When | Config |
|----------|------|--------|
| **Always On** | Dev/staging, low traffic (<100 rps) | `ratio: 1.0` |
| **Probabilistic** | Moderate traffic (100-1000 rps) | `ratio: 0.1` (10%) |
| **Rate-limited** | High traffic (>1000 rps) | `max_traces_per_second: 100` |
| **Tail-based** | Want all errors + slow requests | Collector-side: keep if error OR duration > p99 |
| **Parent-based** | Respect upstream decisions | If parent sampled, child sampled |

**Recommendation:** Start with parent-based + probabilistic (10%). Add tail-based at the collector to capture all errors.

### Context Propagation

| Header | Standard | Format |
|--------|----------|--------|
| `traceparent` | W3C Trace Context | `00-{trace_id}-{span_id}-{flags}` |
| `tracestate` | W3C Trace Context | Vendor-specific key-value pairs |
| `b3` | Zipkin B3 | `{trace_id}-{span_id}-{sampled}` |

**Rule:** Use W3C Trace Context (`traceparent`) as primary. Support B3 for legacy Zipkin systems.

### Trace Storage

| Volume | Solution | Retention |
|--------|----------|-----------|
| <50 GB/day | Jaeger + Elasticsearch | 7 days |
| 50-500 GB/day | Tempo + S3 | 14 days |
| 500+ GB/day | Tempo + S3 with aggressive sampling | 7 days |
| Budget-constrained | Jaeger + Badger (local disk) | 3 days |

---

## Phase 4: SLOs, SLIs & Error Budgets

### SLI Selection by Service Type

| Service Type | Primary SLI | Secondary SLI | Measurement |
|--------------|-------------|---------------|-------------|
| API / Web | Availability + Latency | Error rate | Server-side + synthetic |
| Data pipeline | Freshness + Correctness | Throughput | Pipeline timestamps + checksums |
| Storage | Durability + Availability | Latency | Checksums + uptime monitoring |
| Streaming | Throughput + Latency | Message loss rate | Consumer lag + e2e latency |
| Batch jobs | Success rate + Freshness | Duration | Job scheduler metrics |

### SLO Definition Template

```yaml
slo:
  name: "Payment API Availability"
  service: payment-api
  owner: payments-team
  
  sli:
    type: availability
    definition: "Proportion of non-5xx responses"
    measurement: |
      sum(rate(http_requests_total{service="payment-api",status!~"5.."}[5m]))
      /
      sum(rate(http_requests_total{service="payment-api"}[5m]))
    
  target: 99.95%  # 21.9 min downtime/month
  window: rolling_30d
  
  error_budget:
    total_minutes: 21.9  # per 30 days
    burn_rate_alerts:
      - severity: critical
        burn_rate: 14.4x  # Budget consumed in 2 hours
        short_window: 5m
        long_window: 1h
      - severity: warning
        burn_rate: 6x    # Budget consumed in 5 days
        short_window: 30m
        long_window: 6h
      - severity: ticket
        burn_rate: 1x    # Budget consumed in 30 days
        short_window: 6h
        long_window: 3d
  
  consequences:
    budget_remaining_above_50pct: "Normal development velocity"
    budget_remaining_20_to_50pct: "Prioritize reliability work"
    budget_remaining_below_20pct: "Feature freeze; reliability only"
    budget_exhausted: "All hands on reliability until budget recovers"
```

### Common SLO Targets

| Service Tier | Availability | p50 Latency | p99 Latency | Monthly Downtime |
|--------------|-------------|-------------|-------------|------------------|
| Tier 0 (payments, auth) | 99.99% | <100ms | <500ms | 4.3 min |
| Tier 1 (core API) | 99.95% | <200ms | <1s | 21.9 min |
| Tier 2 (non-critical) | 99.9% | <500ms | <2s | 43.8 min |
| Tier 3 (internal tools) | 99.5% | <1s | <5s | 3.6 hours |
| Batch / pipeline | 99% (success rate) | N/A | N/A | N/A |

### Error Budget Tracking

```yaml
# Weekly error budget review template
error_budget_review:
  week: "2026-W08"
  service: payment-api
  slo_target: 99.95%
  
  budget:
    total_minutes_this_period: 21.9
    consumed_minutes: 8.2
    remaining_minutes: 13.7
    remaining_percent: 62.6%
    
  incidents_consuming_budget:
    - date: "2026-02-18"
      duration_minutes: 5.1
      cause: "Database connection pool exhaustion"
      preventable: true
      action: "Increase pool size + add saturation alert"
    - date: "2026-02-20"
      duration_minutes: 3.1
      cause: "Upstream payment provider timeout"
      preventable: false
      action: "Add circuit breaker with fallback"
  
  velocity_decision: "Normal — 62.6% budget remaining"
  reliability_work_this_week:
    - "Add connection pool saturation alert"
    - "Implement circuit breaker for payment provider"
```

---

## Phase 5: Alert Design

### Alert Quality Principles

1. **Every alert must be actionable** — if no one needs to act, it's not an alert
2. **Every alert needs a runbook** — linked directly in the alert annotation
3. **Symptom-based over cause-based** — alert on "users can't checkout" not "CPU high"
4. **Multi-window burn rate** — not static thresholds (see SLO alerts above)
5. **Alert on absence, not just presence** — "no orders in 15 min" catches silent failures

### Alert Severity Levels

| Severity | Response Time | Channel | Who | Example |
|----------|--------------|---------|-----|---------|
| **P0 — Critical** | <5 min | Page (PagerDuty/Opsgenie) | On-call engineer | Payment system down |
| **P1 — High** | <30 min | Page during business hours, Slack 24/7 | On-call | Error rate >5% for 10 min |
| **P2 — Medium** | <4 hours | Slack channel | Team | p99 latency degraded 2x |
| **P3 — Low** | Next business day | Ticket auto-created | Team backlog | Disk usage >80% |
| **Info** | N/A | Dashboard only | No one | Deploy completed |

### Alerting Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Static CPU/memory thresholds | Noisy, not user-impacting | Use SLO-based burn rate alerts |
| Alert per instance | 50 instances = 50 alerts for same issue | Aggregate: alert on service-level error rate |
| No deduplication | Same alert fires 100 times | Group by service + alert name; set repeat interval |
| Missing runbook | Engineer gets paged, doesn't know what to do | Every alert links to a runbook |
| Threshold too sensitive | Fires on brief spikes | Use `for: 5m` to require sustained condition |
| Too many P0s | Alert fatigue → ignoring real incidents | Audit monthly; demote or remove noisy alerts |

### Alert Template (Prometheus Alertmanager)

```yaml
groups:
  - name: payment-api-slo
    rules:
      - alert: PaymentAPIHighErrorRate
        expr: |
          (
            sum(rate(http_requests_total{service="payment-api",status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total{service="payment-api"}[5m]))
          ) > 0.01
        for: 5m
        labels:
          severity: critical
          service: payment-api
          team: payments
        annotations:
          summary: "Payment API error rate {{ $value | humanizePercentage }} (>1%)"
          description: "5xx error rate has exceeded 1% for 5 minutes"
          runbook: "https://wiki.internal/runbooks/payment-api-errors"
          dashboard: "https://grafana.internal/d/payment-api"
          
      - alert: PaymentAPINoTraffic
        expr: |
          sum(rate(http_requests_total{service="payment-api"}[15m])) == 0
        for: 5m
        labels:
          severity: critical
          service: payment-api
        annotations:
          summary: "Payment API receiving zero traffic for 5 minutes"
          runbook: "https://wiki.internal/runbooks/payment-api-no-traffic"

      - alert: PaymentAPILatencyHigh
        expr: |
          histogram_quantile(0.99, 
            sum(rate(http_request_duration_seconds_bucket{service="payment-api"}[5m])) by (le)
          ) > 2
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Payment API p99 latency {{ $value }}s (>2s for 10min)"
          runbook: "https://wiki.internal/runbooks/payment-api-latency"
```

### Runbook Template

```markdown
# Runbook: PaymentAPIHighErrorRate

## What This Alert Means
The payment API is returning >1% 5xx errors over a 5-minute window.
Users are likely failing to complete checkouts.

## Impact
- Users cannot process payments
- Revenue loss: ~$X per minute (based on average traffic)
- SLO: Payment API availability (target: 99.95%)

## Immediate Actions
1. Check the error dashboard: [link]
2. Check recent deploys: `kubectl rollout history deployment/payment-api`
3. Check upstream dependencies:
   - Database: [dashboard link]
   - Stripe API: [status page]
   - Redis cache: [dashboard link]
4. Check application logs:
   ```
   kubectl logs -l app=payment-api --since=10m | jq 'select(.level=="error")'
   ```

## Common Causes & Fixes
| Cause | Diagnosis | Fix |
|-------|-----------|-----|
| Bad deploy | Errors started at deploy time | `kubectl rollout undo deployment/payment-api` |
| DB connection exhaustion | `db_connections_active` at max | Restart pods (rolling) + increase pool size |
| Stripe outage | Stripe status page red | Enable fallback payment processor |
| Memory leak | Memory climbing, OOMKilled events | Rolling restart + investigate |

## Escalation
- If unresolved after 15 min: page payment team lead
- If revenue impact >$10K: page VP Engineering
- If Stripe outage: communicate to support team for customer messaging

## Resolution
- Confirm error rate <0.1% for 10 min
- Post in #incidents: root cause + duration + impact
- Schedule post-mortem if downtime >5 min
```

---

## Phase 6: Dashboard Architecture

### Dashboard Hierarchy

```
L1: Executive / Business Dashboard (non-technical stakeholders)
  ↓
L2: Service Overview Dashboard (on-call, quick triage)
  ↓
L3: Service Deep-Dive Dashboard (debugging specific service)
  ↓
L4: Infrastructure Dashboard (resource-level details)
```

### L1: Business Dashboard

```yaml
panels:
  - title: "Revenue per Minute"
    type: stat
    query: "sum(rate(orders_total{status='completed'}[5m])) * avg(order_value_dollars)"
  - title: "Active Users (5min)"
    type: stat
    query: "count(count by (user_id) (http_requests_total{...}[5m]))"
  - title: "Checkout Success Rate"
    type: gauge
    query: "sum(rate(checkout_total{status='success'}[1h])) / sum(rate(checkout_total[1h]))"
    thresholds: [95, 98, 99.5]
  - title: "Error Budget Remaining"
    type: gauge
    query: "1 - (error_budget_consumed / error_budget_total)"
```

### L2: Service Overview Dashboard

Every service gets one of these with identical layout:

```yaml
row_1_traffic:
  - "Request Rate (rps)" — timeseries, by status code
  - "Error Rate (%)" — timeseries, threshold line at SLO
  - "Active Requests" — gauge

row_2_latency:
  - "Latency Distribution" — heatmap
  - "p50 / p95 / p99" — timeseries, threshold lines
  - "Latency by Endpoint" — table, sorted by p99

row_3_dependencies:
  - "Downstream Latency" — timeseries per dependency
  - "Downstream Error Rate" — timeseries per dependency
  - "Database Query Duration" — timeseries by query type

row_4_resources:
  - "CPU Usage" — timeseries per pod
  - "Memory Usage" — timeseries per pod
  - "Pod Restarts" — stat

row_5_business:
  - "Business Metric 1" — service-specific
  - "Business Metric 2" — service-specific
```

### Dashboard Rules

1. **Time range default: last 1 hour** — most debugging happens in recent time
2. **Variable selectors at top**: environment, service, instance
3. **Consistent color coding**: green=good, yellow=degraded, red=bad across all dashboards
4. **Link alerts to dashboards** — every alert annotation includes dashboard URL
5. **No more than 15 panels per dashboard** — split into L3 if needed
6. **Include "as of" timestamp** — so screenshots in incidents are unambiguous
7. **Dashboard as code** — store Grafana JSON in git, provision via API

---

## Phase 7: Incident Response

### Incident Severity Classification

| Severity | Criteria | Response | Communication |
|----------|----------|----------|---------------|
| **SEV-1** | Service down, data loss risk, security breach | All hands, war room | Status page update every 15 min |
| **SEV-2** | Degraded service, SLO at risk, partial outage | On-call + backup | Status page update every 30 min |
| **SEV-3** | Minor degradation, workaround exists | On-call during hours | Internal Slack update |
| **SEV-4** | Cosmetic, low impact | Next sprint | None |

### Incident Roles

| Role | Responsibility | Who |
|------|---------------|-----|
| **Incident Commander (IC)** | Owns the incident. Coordinates. Makes decisions. | On-call lead |
| **Technical Lead** | Diagnoses and fixes. Communicates technical status to IC. | Senior engineer |
| **Communications Lead** | Updates status page, Slack, stakeholders. | Product/support |
| **Scribe** | Documents timeline, actions, decisions in real-time. | Anyone available |

### Incident Response Workflow

```
1. DETECT
   - Alert fires → on-call paged
   - Customer report → support escalates
   - Internal discovery → engineer reports
   
2. TRIAGE (first 5 minutes)
   - Confirm the issue is real (not false alert)
   - Classify severity (SEV-1 through SEV-4)
   - Open incident channel: #inc-YYYY-MM-DD-short-description
   - Assign roles (IC, Tech Lead, Comms)
   
3. MITIGATE (next 5-30 minutes)
   - Goal: STOP THE BLEEDING, not find root cause
   - Options (try in order):
     a. Rollback last deploy
     b. Scale up / restart pods
     c. Toggle feature flag off
     d. Redirect traffic / enable fallback
     e. Manual data fix
   - Document every action with timestamp
   
4. STABILIZE
   - Confirm mitigation is working (metrics back to normal)
   - Monitor for 15-30 min for recurrence
   - Update status page: "Monitoring fix"
   
5. RESOLVE
   - Confirm all metrics healthy for 30+ min
   - Update status page: "Resolved"
   - Schedule post-mortem (within 48 hours for SEV-1/2)
   - Send internal summary to stakeholders
```

### Incident Channel Template

```
📋 Incident: Payment API 5xx Errors
🔴 Severity: SEV-2
🕐 Started: 2026-02-22 14:23 UTC
👤 IC: @alice
🔧 Tech Lead: @bob
📢 Comms: @charlie

Status: MITIGATING
Impact: ~5% of checkout requests failing
Customer-facing: Yes

Timeline:
14:23 — Alert fired: PaymentAPIHighErrorRate
14:25 — IC assigned: @alice, confirmed real via dashboard
14:28 — Tech Lead: error logs show connection pool exhaustion post-deploy
14:31 — Rolled back deployment v2.3.1 → v2.3.0
14:35 — Error rate dropping, monitoring
14:50 — Error rate <0.1%, marking resolved
```

---

## Phase 8: Post-Mortem Framework

### Blameless Post-Mortem Template

```yaml
post_mortem:
  title: "Payment API Connection Pool Exhaustion"
  date: "2026-02-22"
  severity: SEV-2
  duration: 27 minutes (14:23 — 14:50 UTC)
  authors: ["@alice", "@bob"]
  reviewers: ["@engineering-leads"]
  status: action_items_in_progress
  
  summary: |
    A deployment at 14:15 introduced a connection leak in the payment API.
    Connection pool was exhausted by 14:23, causing 5xx errors for ~5% of
    checkout requests. Rolled back at 14:31; recovered by 14:50.
  
  impact:
    user_impact: "~340 users saw checkout failures over 27 minutes"
    revenue_impact: "$2,100 estimated (based on average order value × failed checkouts)"
    slo_impact: "Consumed 5.1 min of 21.9 min monthly error budget (23%)"
    data_impact: "No data loss. 12 orders failed; users could retry successfully."
  
  timeline:
    - time: "14:15"
      event: "Deploy v2.3.1 rolled out (3/3 pods updated)"
    - time: "14:23"
      event: "PaymentAPIHighErrorRate alert fired"
    - time: "14:25"
      event: "IC assigned, confirmed via dashboard"
    - time: "14:28"
      event: "Root cause identified: new ORM query not releasing connections"
    - time: "14:31"
      event: "Rollback initiated: v2.3.1 → v2.3.0"
    - time: "14:35"
      event: "Error rate declining"
    - time: "14:50"
      event: "Resolved: error rate <0.1% sustained"
  
  root_cause: |
    The v2.3.1 deploy introduced a new database query in the order validation
    path. The query used a raw connection instead of the pool's managed client,
    so connections were acquired but never released. Under load, the pool
    exhausted within 8 minutes.
  
  contributing_factors:
    - "No integration test for connection pool behavior under load"
    - "Connection pool saturation metric existed but had no alert"
    - "Code review didn't catch raw connection usage"
  
  what_went_well:
    - "Alert fired within 8 minutes of deploy"
    - "IC assigned in 2 minutes"
    - "Root cause identified in 3 minutes (clear in logs)"
    - "Rollback executed cleanly"
  
  what_went_wrong:
    - "8-minute detection gap after deploy"
    - "No canary deployment to catch before full rollout"
    - "Connection pool saturation had no alert"
  
  action_items:
    - action: "Add connection pool saturation alert (>80% for 2 min)"
      owner: "@bob"
      priority: P1
      due: "2026-02-25"
      status: in_progress
      ticket: "ENG-1234"
    - action: "Enable canary deployments for payment-api"
      owner: "@alice"
      priority: P1
      due: "2026-03-01"
      ticket: "ENG-1235"
    - action: "Add linting rule: no raw DB connections in application code"
      owner: "@charlie"
      priority: P2
      due: "2026-03-07"
      ticket: "ENG-1236"
    - action: "Load test payment-api connection pool in staging"
      owner: "@bob"
      priority: P2
      due: "2026-03-07"
      ticket: "ENG-1237"
  
  lessons_learned:
    - "Resource saturation metrics need alerts, not just dashboards"
    - "Canary deployments are mandatory for Tier 0 services"
    - "ORM abstractions don't guarantee connection safety — review raw queries"
```

### Post-Mortem Meeting Agenda (60 minutes)

```
1. (5 min) Context setting — IC reads the summary
2. (15 min) Timeline walkthrough — what happened, when, by whom
3. (15 min) Root cause deep-dive — 5 Whys exercise
4. (5 min) What went well — celebrate good response
5. (15 min) Action items — assign owners, priorities, due dates
6. (5 min) Wrap-up — review date for action item check-in
```

### 5 Whys Exercise

```
Problem: 5xx errors in payment API

Why 1: Database connections were exhausted
Why 2: A new query acquired connections without releasing them
Why 3: The query used a raw connection instead of the pool manager
Why 4: The ORM's raw query API doesn't auto-release (by design)
Why 5: We don't have a linting rule or code review checklist item for this

Root cause: Missing guard against raw connection usage in application code
Systemic fix: Linting rule + connection pool saturation alerting
```

---

## Phase 9: On-Call Operations

### On-Call Structure

```yaml
on_call:
  rotation: weekly
  handoff_day: Monday 10:00 UTC
  
  primary:
    response_time: 5 minutes (SEV-1/2), 30 minutes (SEV-3)
    escalation_after: 15 minutes no-ack
    
  secondary:
    response_time: 15 minutes (SEV-1), 1 hour (SEV-2/3)
    escalation_after: 30 minutes no-ack
    
  manager_escalation:
    trigger: SEV-1 unresolved after 30 minutes
    
  handoff_checklist:
    - Review open incidents and active alerts
    - Check error budget status for all services
    - Read post-mortems from previous week
    - Verify PagerDuty schedule and contact info
    - Test alert routing (send test page)
```

### On-Call Health Metrics

| Metric | Healthy | Needs Attention | Unhealthy |
|--------|---------|-----------------|-----------|
| Pages per week | <5 | 5-15 | >15 |
| After-hours pages per week | <2 | 2-5 | >5 |
| False positive rate | <10% | 10-30% | >30% |
| Mean time to acknowledge | <5 min | 5-15 min | >15 min |
| Mean time to resolve | <30 min | 30-120 min | >120 min |
| Toil ratio (manual vs automated) | <30% | 30-60% | >60% |

### Weekly On-Call Review Template

```yaml
on_call_review:
  week: "2026-W08"
  engineer: "@bob"
  
  incidents:
    total: 7
    sev_1: 0
    sev_2: 1
    sev_3: 4
    false_positives: 2
    after_hours: 3
    
  time_spent:
    incident_response: "4.5 hours"
    toil_automation: "2 hours"
    runbook_updates: "1 hour"
    
  improvements_made:
    - "Silenced noisy disk alert on dev servers"
    - "Added auto-remediation for pod restart threshold"
    
  improvements_needed:
    - "Cache expiry alert fires every Tuesday at 03:00 — needs investigation"
    - "Payment retry logic needs circuit breaker (caused 3 alerts)"
    
  handoff_notes: |
    Watch payment-api p99 latency — it's been creeping up since Wednesday.
    Stripe changed their sandbox endpoints; staging may throw errors.
```

---

## Phase 10: Chaos Engineering & Reliability Testing

### Chaos Principles

1. Start with a hypothesis: "If X fails, the system should Y"
2. Run in production (start small — one instance, one AZ)
3. Minimize blast radius with automatic rollback
4. Build confidence incrementally: staging → canary → production

### Chaos Experiment Template

```yaml
chaos_experiment:
  name: "Payment DB failover"
  hypothesis: "If the primary database becomes unavailable, traffic should
    failover to the replica within 30 seconds with <1% error rate spike"
  
  steady_state:
    - metric: "checkout_success_rate"
      expected: ">99.5%"
    - metric: "db_query_duration_p99"
      expected: "<200ms"
  
  injection:
    type: "network_partition"
    target: "payment-db-primary"
    duration: "5 minutes"
    blast_radius: "single AZ"
  
  abort_conditions:
    - "checkout_success_rate < 95% for > 60 seconds"
    - "revenue_per_minute drops > 50%"
    - "any SEV-1 incident declared"
  
  results:
    failover_time: "22 seconds"
    error_spike: "0.3% for 25 seconds"
    hypothesis_confirmed: true
    
  follow_up_actions:
    - "Document failover behavior in runbook"
    - "Add failover time as SLI (target: <30s)"
```

### Chaos Engineering Maturity Levels

| Level | What You Test | Tools |
|-------|--------------|-------|
| 1: Manual | Kill a pod, see what happens | `kubectl delete pod` |
| 2: Automated | Scheduled pod kills, network delays | Chaos Monkey, Litmus |
| 3: Game Days | Multi-failure scenarios with team exercise | Custom scripts + coordination |
| 4: Continuous | Automated chaos in production with auto-rollback | Gremlin, Chaos Mesh |

---

## Phase 11: Observability Cost Optimization

### Cost Drivers (Ranked)

| # | Driver | Typical % of Bill | Optimization |
|---|--------|-------------------|-------------|
| 1 | Log volume | 40-60% | Reduce verbosity, drop DEBUG, sample repetitive |
| 2 | Metric cardinality | 15-25% | Drop unused metrics, limit labels |
| 3 | Trace volume | 10-20% | Sampling, tail-based sampling |
| 4 | Retention | 10-15% | Tiered storage (hot → warm → cold) |
| 5 | Query cost | 5-10% | Optimize dashboard queries, set max scan limits |

### Cost Reduction Checklist

```yaml
cost_optimization:
  logs:
    - action: "Drop DEBUG/TRACE in production"
      savings: "30-50% of log volume"
    - action: "Sample health check logs (1:100)"
      savings: "5-15% of log volume"
    - action: "Deduplicate identical error bursts"
      savings: "10-20% during incidents"
    - action: "Move logs older than 7 days to S3/cold storage"
      savings: "60-80% of storage cost"
    - action: "Drop request/response body logging"
      savings: "20-40% of log volume"
  
  metrics:
    - action: "Audit unused metrics (no dashboard, no alert)"
      savings: "10-30% of series"
    - action: "Reduce histogram bucket count (default 11 → 8)"
      savings: "~27% of histogram series"
    - action: "Remove high-cardinality labels"
      savings: "Variable — can be massive"
    - action: "Increase scrape interval for non-critical metrics (15s → 60s)"
      savings: "75% of data points for those metrics"
  
  traces:
    - action: "Implement tail-based sampling"
      savings: "80-95% of trace volume"
    - action: "Drop internal health check traces"
      savings: "5-20% of trace volume"
    - action: "Reduce span attribute size (truncate long strings)"
      savings: "10-30% of trace storage"
  
  general:
    - action: "Review and right-size retention policies quarterly"
    - action: "Set query timeouts and result limits on dashboards"
    - action: "Use recording rules for expensive queries"
```

### Monthly Cost Review Template

```yaml
observability_cost_review:
  month: "February 2026"
  total_cost: "$X,XXX"
  
  breakdown:
    logs: { volume: "X TB", cost: "$X", pct: "X%" }
    metrics: { series: "X million", cost: "$X", pct: "X%" }
    traces: { volume: "X TB", cost: "$X", pct: "X%" }
    infrastructure: { instances: X, cost: "$X", pct: "X%" }
  
  cost_per:
    request: "$0.000X"
    service: "$X average"
    engineer: "$X per engineer"
  
  optimizations_applied: []
  optimizations_planned: []
  budget_status: "on_track | over_budget | under_budget"
```

---

## Phase 12: Advanced Patterns

### Correlation: Connecting the Three Pillars

```
Every log line includes: trace_id, span_id
Every trace span includes: service, operation
Every metric includes: service label

Correlation paths:
  Alert fires (metric) → Click → Dashboard (metric) → Filter by time window
    → Trace search (same service + time) → Find failing trace
    → Logs (filter by trace_id) → See exact error
    
  Support ticket (user report) → Find request_id in logs
    → Extract trace_id → View full trace → Identify slow span
    → Check span's service metrics → Confirm pattern
```

### Synthetic Monitoring

```yaml
synthetic_checks:
  - name: "Checkout flow"
    type: browser
    frequency: 5m
    locations: [us-east, eu-west, ap-southeast]
    steps:
      - navigate: "https://app.example.com/products"
      - click: "Add to Cart"
      - click: "Checkout"
      - assert: "Order confirmation page loads in <3s"
    alert_on: "2 consecutive failures from same location"
    
  - name: "API health"
    type: api
    frequency: 1m
    endpoints:
      - url: "https://api.example.com/health"
        expected_status: 200
        max_latency_ms: 500
      - url: "https://api.example.com/v1/products?limit=1"
        expected_status: 200
        max_latency_ms: 1000
```

### Feature Flag Observability

```yaml
# Correlate feature flags with metrics
feature_flag_monitoring:
  - flag: "new_checkout_flow"
    metrics_to_compare:
      - "checkout_conversion_rate" # by flag variant
      - "checkout_error_rate"
      - "checkout_latency_p99"
    alerts:
      - "If error rate for new variant > 2x control, auto-disable flag"
```

### Observability Maturity Model

| Dimension | Level 1 | Level 2 | Level 3 | Level 4 |
|-----------|---------|---------|---------|---------|
| Logging | Unstructured logs | Structured JSON, centralized | Correlated with traces | Automated log analysis |
| Metrics | Basic infra metrics | RED/USE for services | SLO-based with error budgets | Predictive (anomaly detection) |
| Tracing | No tracing | Key services instrumented | Full distributed tracing | Trace-driven testing |
| Alerting | Static thresholds | Multi-signal alerts | Burn-rate based on SLOs | Auto-remediation |
| Incident Response | Ad hoc | Defined process + roles | Post-mortems with action tracking | Chaos engineering in prod |
| Culture | "Ops team handles it" | Shared ownership (you build it, you run it) | SLO-driven development velocity | Reliability as a feature |

---

## Quality Scoring Rubric (0-100)

| Dimension | Weight | 0 | 5 | 10 |
|-----------|--------|---|---|-----|
| Logging quality | 15% | Unstructured, no correlation | Structured JSON, missing fields | Full schema, trace correlation, PII scrubbing |
| Metrics coverage | 15% | No metrics | RED or USE, not both | RED + USE + business metrics + custom |
| Tracing completeness | 10% | No tracing | Key services | Full path, sampling strategy, tail-based |
| SLO maturity | 15% | No reliability targets | Informal targets | SLOs with error budgets, burn-rate alerts, weekly review |
| Alert quality | 15% | Noisy/missing | Actionable, some runbooks | SLO-based, full runbooks, low false positive |
| Incident response | 10% | Ad hoc | Defined process | Full process, roles, post-mortems, chaos engineering |
| Dashboard design | 10% | No dashboards | Basic panels | Hierarchical L1-L4, consistent, linked to alerts |
| Cost efficiency | 10% | Unknown cost | Tracked | Optimized, reviewed monthly, within budget |

**90-100:** World-class. Teach others. **70-89:** Production-ready. Fill specific gaps. **50-69:** Functional but fragile. **<50:** Significant reliability risk.

---

## 10 Observability Commandments

1. **Structured or it didn't happen** — unstructured logs are technical debt
2. **Correlate everything** — trace_id connects logs, traces, and metrics
3. **Alert on symptoms, not causes** — users don't care about CPU, they care about latency
4. **Every alert gets a runbook** — no runbook = no alert
5. **SLOs drive velocity** — error budgets decide when to ship vs stabilize
6. **Dashboards have hierarchy** — executives don't need pod CPU graphs
7. **Blameless post-mortems always** — blame prevents learning
8. **Cost is a feature** — observability that bankrupts you isn't observability
9. **You build it, you run it** — the team that ships code owns its observability
10. **Practice failure** — chaos engineering builds confidence

---

## 12 Natural Language Commands

| Command | What It Does |
|---------|-------------|
| "Audit our observability" | Run the /16 health check, score each dimension, prioritize gaps |
| "Design logging for [service]" | Generate structured log schema with context fields for the service |
| "Set up metrics for [service]" | Create RED + USE + business metric instrumentation plan |
| "Create SLOs for [service]" | Define SLIs, targets, error budgets, and burn-rate alert rules |
| "Design alerts for [service]" | Create alert rules with severity, thresholds, and runbook templates |
| "Build dashboard for [service]" | Design L2 service overview dashboard with panel specifications |
| "Write a runbook for [alert]" | Generate structured runbook with diagnosis steps and fixes |
| "Run post-mortem for [incident]" | Generate blameless post-mortem document with timeline and action items |
| "Set up on-call for [team]" | Design rotation, escalation policy, handoff checklist |
| "Plan chaos experiment for [scenario]" | Design experiment with hypothesis, injection, abort conditions |
| "Optimize observability costs" | Audit current spend, identify top savings, create reduction plan |
| "Design tracing for [system]" | Create OpenTelemetry instrumentation plan with sampling strategy |

---

## ⚡ Level Up Your Observability

This skill gives you the methodology. For industry-specific implementation patterns:

- **SaaS companies:** [AfrexAI SaaS Context Pack ($47)](https://afrexai-cto.github.io/context-packs/) — includes SaaS-specific SLOs, multi-tenant monitoring, and usage-based billing observability
- **Fintech:** [AfrexAI Fintech Context Pack ($47)](https://afrexai-cto.github.io/context-packs/) — compliance audit logging, transaction monitoring, fraud detection signals
- **Healthcare:** [AfrexAI Healthcare Context Pack ($47)](https://afrexai-cto.github.io/context-packs/) — HIPAA audit trails, PHI access logging, uptime requirements

### 🔗 More Free Skills by AfrexAI

- `afrexai-devops-engine` — CI/CD, infrastructure, deployment strategies
- `afrexai-api-architect` — API design, security, versioning
- `afrexai-database-engineering` — Schema design, query optimization, migrations
- `afrexai-code-reviewer` — Code review methodology with SPEAR framework
- `afrexai-prompt-engineering` — System prompt design, testing, optimization

**Browse all AfrexAI skills:** [clawhub.com](https://clawhub.com) | [Full storefront](https://afrexai-cto.github.io/context-packs/)
