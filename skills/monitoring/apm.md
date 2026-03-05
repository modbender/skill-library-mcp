# Application Performance Monitoring (APM)

## What APM Shows You

| Metric | Why It Matters |
|--------|----------------|
| **Latency (p50, p95, p99)** | The average lies; p99 shows worst cases |
| **Error rate by endpoint** | Which API routes are failing |
| **Distributed traces** | Follow a request across services |
| **Slow queries** | Database calls killing performance |
| **Stack traces** | Full context when errors happen |

## Tool Comparison

| Tool | Type | Best For | Pricing |
|------|------|----------|---------|
| **Sentry** | SaaS/Self-host | Errors + basic performance | Free → $26/mo |
| **Datadog APM** | SaaS | Full observability | $31/host/mo |
| **New Relic** | SaaS | Traditional APM | Free → $49/mo |
| **Jaeger** | Self-hosted | Tracing only | Free (infra cost) |
| **Grafana Tempo** | Self-hosted | Tracing with Grafana | Free (infra cost) |

**Recommendation for most teams:** Start with Sentry. Best DX, free tier works, covers errors and performance.

## Sentry Quick Start

### Next.js
```bash
npx @sentry/wizard@latest -i nextjs
```

### Node.js
```bash
npm install @sentry/node @sentry/profiling-node
```

```javascript
import * as Sentry from "@sentry/node";
import { nodeProfilingIntegration } from "@sentry/profiling-node";

Sentry.init({
  dsn: "https://xxx@sentry.io/xxx",
  integrations: [nodeProfilingIntegration()],
  tracesSampleRate: 0.1, // 10% of transactions
  profilesSampleRate: 0.1,
});
```

### What You Get
- Automatic error capture with stack traces
- Performance monitoring (web vitals, API latency)
- Release tracking
- User context
- Breadcrumbs (what happened before the error)

## OpenTelemetry (Vendor-Neutral)

Instrument once, export anywhere.

```typescript
// instrumentation.ts
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({
    url: process.env.OTEL_EXPORTER_OTLP_ENDPOINT,
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();
```

**Auto-instrumented:**
- HTTP requests (incoming and outgoing)
- Database queries (pg, mysql, mongodb, redis)
- gRPC calls
- Express/Fastify/Koa middleware

## Self-Hosted vs SaaS

### Use SaaS When:
- Team < 10 engineers
- No dedicated ops/platform team
- Need to move fast
- Compliance allows external data

### Self-Host When:
- Data must stay in your infra (compliance)
- Very high volume (SaaS costs explode)
- You have platform/infra team
- You want full control

### Self-Hosted Stack
```
OpenTelemetry Collector → Jaeger (traces) + Prometheus (metrics) + Loki (logs)
                         ↓
                       Grafana (visualization)
```

## Quick Wins (Highest Value, Lowest Effort)

1. **Sentry free tier** — Catch errors with context (15 min setup)
2. **Add request IDs** — Correlate logs across services
3. **Log slow queries** — Find the 80/20 of database problems
4. **Web Vitals** — Know if your frontend is slow (Sentry/Vercel Analytics)
5. **Health endpoints** — `/health` with DB check for external monitoring

## What to Look For

### In Traces
- Spans taking >500ms
- N+1 query patterns (many small DB calls)
- External API calls that block
- Missing async where it should be async

### In Errors
- Error rate spikes after deploy
- Errors grouped by user/endpoint
- Errors that happen only in production

### In Metrics
- Latency p99 vs p50 (tail latency)
- Error rate by endpoint
- Throughput correlation with latency
