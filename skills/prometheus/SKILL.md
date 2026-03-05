---
name: prometheus
description: Query Prometheus monitoring data to check server metrics, resource usage, and system health. Use when the user asks about server status, disk space, CPU/memory usage, network stats, or any metrics collected by Prometheus. Supports HTTP Basic Auth via environment variables.
---

# Prometheus Skill

Query Prometheus monitoring data to get insights about your infrastructure.

## Environment Variables

Set in `.env` file:
- `PROMETHEUS_URL` - Prometheus server URL (e.g., `http://localhost:9090`)
- `PROMETHEUS_USER` - HTTP Basic Auth username (optional)
- `PROMETHEUS_PASSWORD` - HTTP Basic Auth password (optional)

## Usage

### Query Metrics

Use the CLI to run PromQL queries:

```bash
source .env && node scripts/cli.js query '<promql_query>'
```

### Common Examples

**Disk space usage:**
```bash
node scripts/cli.js query '100 - (node_filesystem_avail_bytes / node_filesystem_size_bytes * 100)'
```

**CPU usage:**
```bash
node scripts/cli.js query '100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)'
```

**Memory usage:**
```bash
node scripts/cli.js query '(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100'
```

**Load average:**
```bash
node scripts/cli.js query 'node_load1'
```

### List Metrics

Find available metrics matching a pattern:

```bash
node scripts/cli.js metrics 'node_memory_*'
```

### Series Discovery

Find time series by label selectors:

```bash
node scripts/cli.js series '{__name__=~"node_cpu_.*", instance=~".*:9100"}'
```

### Get Labels

List label names:

```bash
node scripts/cli.js labels
```

List values for a specific label:

```bash
node scripts/cli.js label-values instance
```

## Output Format

All commands output JSON for easy parsing. Use `jq` for pretty printing:

```bash
node scripts/cli.js query 'up' | jq .
```

## Common Queries Reference

| Metric | PromQL Query |
|--------|--------------|
| Disk free % | `node_filesystem_avail_bytes / node_filesystem_size_bytes * 100` |
| Disk used % | `100 - (node_filesystem_avail_bytes / node_filesystem_size_bytes * 100)` |
| CPU idle % | `avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100` |
| Memory used % | `(node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100` |
| Network RX | `rate(node_network_receive_bytes_total[5m])` |
| Network TX | `rate(node_network_transmit_bytes_total[5m])` |
| Uptime | `node_time_seconds - node_boot_time_seconds` |
| Service up | `up` |

## Notes

- Time range defaults to last 1 hour for instant queries
- Use range queries `[5m]` for rate calculations
- All queries return JSON with `data.result` containing the results
- Instance labels typically show `host:port` format
