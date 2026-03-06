# Prometheus Metrics Examples

Query and analyze Prometheus metrics using PromQL.

## Available Tools

### 1. list-metrics-from-prometheus
List available metrics from Prometheus.

**Parameters:**
- `search` (optional, string): Filter metrics by name pattern
- `limit` (optional, string): Maximum number to return (default: 100)

### 2. query-metrics-from-prometheus
Execute instant PromQL query (current value).

**Parameters:**
- `query` (required, string): PromQL expression

### 3. query-metrics-range-from-prometheus
Execute range PromQL query (values over time).

**Parameters:**
- `query` (required, string): PromQL expression
- `time_range` (required, string): Time range (e.g., `5m`, `1h`, `24h`, `7d`)
- `step` (optional, string): Resolution step (e.g., `15s`, `1m`, `5m`)

## Example 1: List Available Metrics

```bash
# List all metrics
npx mcporter call ops-mcp-server list-metrics-from-prometheus

# Search for specific metrics
npx mcporter call ops-mcp-server list-metrics-from-prometheus search="cpu" limit="50"
```

## Example 2: Instant Queries (Current Values)

```bash
# Simple metric query
npx mcporter call ops-mcp-server query-metrics-from-prometheus query="up"

# Filtered query
npx mcporter call ops-mcp-server query-metrics-from-prometheus query='up{job="kubernetes-nodes"}'

# Aggregated query
npx mcporter call ops-mcp-server query-metrics-from-prometheus query="sum(node_memory_MemTotal_bytes)"
```

## Example 3: Range Queries (Values Over Time)

```bash
# Query over time (default step)
npx mcporter call ops-mcp-server query-metrics-range-from-prometheus \
  query="node_cpu_seconds_total" time_range="1h"

# With custom step interval
npx mcporter call ops-mcp-server query-metrics-range-from-prometheus \
  query="node_memory_MemAvailable_bytes" time_range="24h" step="5m"

# Rate calculation
npx mcporter call ops-mcp-server query-metrics-range-from-prometheus \
  query="rate(http_requests_total[5m])" time_range="30m" step="1m"
```

## PromQL Basics

### Simple Queries

```promql
# Get metric
up

# Filter by label
up{job="kubernetes-nodes"}

# Multiple label filters
http_requests_total{status="200",method="GET"}

# Regex matching
http_requests_total{path=~"/api/.*"}

# Negative matching
up{job!="node-exporter"}
```

### Rate and Increase

```promql
# Rate per second
rate(http_requests_total[5m])

# Increase over time window
increase(http_requests_total[1h])

# irate (instant rate)
irate(http_requests_total[5m])
```

### Aggregation Functions

```promql
# Sum
sum(container_memory_usage_bytes)

# Sum by label
sum(container_memory_usage_bytes) by (namespace)

# Average
avg(node_cpu_usage_percent) by (instance)

# Min/Max
max(container_memory_usage_bytes) by (pod)
min(node_disk_free_bytes) by (node)

# Count
count(up{job="kubernetes-nodes"})

# Top K
topk(5, container_memory_usage_bytes)
bottomk(3, node_disk_free_bytes)
```

### Mathematical Operations

```promql
# Arithmetic
node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes

# Percentage
(node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100

# Rate calculation
rate(http_requests_total[5m]) * 60
```

## Example 4: Resource Monitoring

```bash
# CPU usage
npx mcporter call ops-mcp-server query-metrics-from-prometheus \
  query='100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) by (instance) * 100)'

# Memory usage
npx mcporter call ops-mcp-server query-metrics-from-prometheus \
  query="container_memory_usage_bytes > 1073741824"

# Disk usage
npx mcporter call ops-mcp-server query-metrics-from-prometheus \
  query="(node_filesystem_avail_bytes / node_filesystem_size_bytes) * 100 < 20"
```

## Example 5: Application Performance

```bash
# Request rate
npx mcporter call ops-mcp-server query-metrics-range-from-prometheus \
  query="sum(rate(http_requests_total[5m])) by (service)" time_range="1h" step="1m"

# Error rate
npx mcporter call ops-mcp-server query-metrics-from-prometheus \
  query='sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100'

# Latency
npx mcporter call ops-mcp-server query-metrics-from-prometheus \
  query="histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))"
```

## Time Range Format

Supported time units:
- `s` - seconds
- `m` - minutes
- `h` - hours
- `d` - days

Examples:
- `5m` - 5 minutes
- `1h` - 1 hour
- `24h` - 24 hours (1 day)
- `7d` - 7 days
- `30d` - 30 days

## Step Interval Format

Same format as time range:
- `15s` - 15 seconds (default)
- `30s` - 30 seconds
- `1m` - 1 minute
- `5m` - 5 minutes
- `1h` - 1 hour

## Example 6: Alerting and Capacity Planning

```bash
# High CPU alert
npx mcporter call ops-mcp-server query-metrics-from-prometheus \
  query="100 - (avg(rate(container_cpu_usage_seconds_total[5m])) by (pod) * 100) > 90"

# Memory growth trend
npx mcporter call ops-mcp-server query-metrics-range-from-prometheus \
  query="sum(container_memory_usage_bytes) by (namespace)" time_range="7d" step="1h"
```

## Expected Output

### Instant Query Response

```json
{
  "status": "success",
  "data": {
    "resultType": "vector",
    "result": [
      {
        "metric": {
          "__name__": "up",
          "job": "kubernetes-nodes",
          "instance": "node-1"
        },
        "value": [1740672000, "1"]
      }
    ]
  }
}
```

### Range Query Response

```json
{
  "status": "success",
  "data": {
    "resultType": "matrix",
    "result": [
      {
        "metric": {
          "__name__": "node_cpu_seconds_total",
          "instance": "node-1"
        },
        "values": [
          [1740672000, "12345.67"],
          [1740672060, "12350.12"],
          [1740672120, "12354.89"]
        ]
      }
    ]
  }
}
```

## Troubleshooting

### No Data Returned

**Problem:** Query returns empty result

**Solutions:**
1. List metrics first to verify name: `list-metrics-from-prometheus`
2. Check label filters are correct
3. Verify time range includes data points
4. Try simpler query without filters

### Query Too Slow

**Problem:** Query times out or is very slow

**Solutions:**
1. Reduce time range
2. Increase step interval for range queries
3. Add more specific label filters
4. Use recording rules for complex queries

### Syntax Error

**Problem:** PromQL syntax error

**Solutions:**
1. Check label syntax: `{label="value"}`
2. Verify function names: `rate()`, `sum()`, etc.
3. Ensure time range in square brackets: `[5m]`
4. Match parentheses and brackets

## Best Practices

### 1. Use Rate for Counters

```bash
# Good - use rate for counter metrics
npx mcporter call ops-mcp-server query-metrics-from-prometheus \
  query="rate(http_requests_total[5m])"
```

### 2. Aggregate Appropriately

```bash
# Good - aggregate by relevant label
npx mcporter call ops-mcp-server query-metrics-from-prometheus \
  query="sum(container_memory_usage_bytes) by (namespace)"
```

### 3. Choose Appropriate Time Windows

```bash
# Good - 5m is typical for rate calculations
npx mcporter call ops-mcp-server query-metrics-from-prometheus \
  query="rate(http_requests_total[5m])"
```

### 4. Use Instant Queries for Current State

```bash
# Instant query for current value
npx mcporter call ops-mcp-server query-metrics-from-prometheus query="up"

# Range query for trend
npx mcporter call ops-mcp-server query-metrics-range-from-prometheus query="up" time_range="1h"
```

## Reference

- **Tools**: `list-metrics-from-prometheus`, `query-metrics-from-prometheus`, `query-metrics-range-from-prometheus`
- **Prometheus PromQL**: https://prometheus.io/docs/prometheus/latest/querying/basics/
- **Query Functions**: https://prometheus.io/docs/prometheus/latest/querying/functions/
- **Best Practices**: https://prometheus.io/docs/practices/naming/
