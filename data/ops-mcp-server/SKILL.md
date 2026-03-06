---
name: ops-mcp-server
description: |
  Query observability data and execute operational procedures via the ops-mcp-server MCP interface.
  Covers Kubernetes events, Prometheus metrics, Elasticsearch logs, Jaeger distributed traces, and SOPS runbooks.
triggers:
  - ops
  - ops-mcp-server
  - kubernetes
  - k8s
  - prometheus
  - metrics
  - elasticsearch
  - logs
  - jaeger
  - traces
  - tracing
  - observability
  - monitoring
  - incident
  - sops
  - events
  - cluster
  - pod
  - deployment
  - namespace
  - alert
  - latency
  - error rate
  - outage
---

# Ops MCP Server Skill

Access your infrastructure's observability data and execute operational procedures through a unified MCP interface.

## Capabilities at a Glance

| Module | Tools | What it answers |
|--------|-------|----------------|
| **Events** (Kubernetes) | `list-events-from-ops`, `get-events-from-ops` | What happened to a pod/deployment/node? |
| **Metrics** (Prometheus) | `list-metrics-from-prometheus`, `query-metrics-from-prometheus`, `query-metrics-range-from-prometheus` | Is CPU/memory/traffic normal? What changed over time? |
| **Logs** (Elasticsearch) | `list-log-indices-from-elasticsearch`, `search-logs-from-elasticsearch`, `query-logs-from-elasticsearch` | What errors are in the logs? What did service X log? |
| **Traces** (Jaeger) | `get-services-from-jaeger`, `get-operations-from-jaeger`, `find-traces-from-jaeger`, `get-trace-from-jaeger` | Why is this request slow? Where did it fail? |
| **SOPS** | `list-sops-from-ops`, `list-sops-parameters-from-ops`, `execute-sops-from-ops` | Run a standard operational procedure |

## Setup (first-time)

```bash
# 1. Use mcporter with npx (no installation needed)
# Or install globally: npm i -g mcporter

# 2. Register the server
cd ~/.openclaw/workspace
npx mcporter config add ops-mcp-server --url http://localhost/mcp

# 3. Authenticate (if needed)
npx mcporter auth ops-mcp-server
# On failure, add to ~/.openclaw/workspace/config/mcporter.json:
# "headers": { "Authorization": "Bearer YOUR_TOKEN" }

# 4. Verify
npx mcporter list ops-mcp-server
npx mcporter call ops-mcp-server list-events-from-ops page_size=5

# 5. Set env var
export OPS_MCP_SERVER_URL="http://localhost/mcp"
```

---

## How to Investigate: Decision Guide

When a user describes a problem, use this guide to choose starting tools and build a complete picture.

### 🔴 "Something is broken / service is down"

1. **Kubernetes Events first** — check if pods crashed, restarted, or got evicted
   ```
   get-events-from-ops  subject_pattern="ops.clusters.*.namespaces.<ns>.pods.*.events"
   ```
2. **Logs** — search for errors around the time of the incident
   ```
   query-logs-from-elasticsearch  query="FROM logs-* | WHERE @timestamp > NOW() - 30 minutes | WHERE level == 'error' | LIMIT 50"
   ```
3. **Traces** — find failed or slow requests
   ```
   find-traces-from-jaeger  serviceName=<service>  tags={"error":"true"}
   ```

### 🟡 "Performance is degraded / requests are slow"

1. **Metrics** — check resource saturation
   ```
   query-metrics-from-prometheus  query="100 - (avg(rate(node_cpu_seconds_total{mode='idle'}[5m])) * 100)"
   query-metrics-range-from-prometheus  query="node_memory_MemAvailable_bytes"  time_range="1h"  step="1m"
   ```
2. **Traces** — find slow spans
   ```
   find-traces-from-jaeger  serviceName=<service>  durationMin=1000
   ```
3. **Logs** — look for timeouts or slow query warnings

### 🔵 "I need to run a procedure / restart something"

1. **List available SOPs**
   ```
   list-sops-from-ops
   ```
2. **Get parameters**
   ```
   list-sops-parameters-from-ops  sops_id=<id>
   ```
3. **Execute**
   ```
   execute-sops-from-ops  sops_id=<id>  parameters='{...}'
   ```

### 🟢 "General health check / nothing specific"

Start with events + a key metrics query, then go deeper based on what you find.

---

## Tool Quick Reference

### Events — NATS subject pattern format

```
# Namespace resources
ops.clusters.{cluster}.namespaces.{ns}.{resourceType}.{name}.{observation}

# Node level
ops.clusters.{cluster}.nodes.{nodeName}.{observation}

# Notifications
ops.notifications.providers.{provider}.channels.{channel}.severities.{severity}
```

Wildcards: `*` = one segment, `>` = everything remaining (tail only)

Observation types: `status` | `events` | `alerts` | `findings`

Time is Unix milliseconds: `$(date +%s)000`

### Logs — ES|QL query patterns

```sql
-- Recent errors
FROM logs-* | WHERE @timestamp > NOW() - 30 minutes | WHERE level == 'error' | LIMIT 100

-- Top errors by frequency
FROM logs-* | WHERE @timestamp > NOW() - 1 hour | WHERE level == 'error'
| STATS count() BY message | SORT count DESC | LIMIT 10

-- Specific service
FROM logs-* | WHERE service == 'checkout-service' | WHERE @timestamp > NOW() - 1 hour | LIMIT 50
```

### Metrics — PromQL patterns

```
# CPU usage
100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance) * 100)

# Memory available
node_memory_MemAvailable_bytes

# HTTP error rate
rate(http_requests_total{status=~"5.."}[5m])
```

---

## Detailed Examples & Reference Files

For complete parameter lists, output formats, and advanced patterns, read the relevant file:

- **events** → `examples/events.md`
- **metrics** → `examples/metrics.md`
- **logs** → `examples/logs.md`
- **traces** → `examples/traces.md`
- **sops** → `examples/sops.md`
- **event subject format design** → `references/design.md`

Read the relevant example file before making complex tool calls you're unsure about.

---

## What This Skill is NOT For

- Direct infrastructure changes (use dedicated automation tooling)
- Real-time alerting (investigation only, not a monitoring agent)
- Writing to or modifying operational data (all access is read-only)
