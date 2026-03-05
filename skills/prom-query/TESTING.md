# Testing — prom-query

## Quick Validation

### Syntax Check

All scripts must pass bash syntax validation:

```bash
bash -n scripts/prom-query.sh && echo "✅ Syntax OK"
```

### Help Output

```bash
bash scripts/prom-query.sh --help
```

### Version

```bash
bash scripts/prom-query.sh --version
```

## Testing with Public Demo Instance

The [PromLabs demo server](https://demo.promlabs.com) is a public Prometheus instance with sample data. Use it for testing without any local setup:

```bash
export PROMETHEUS_URL=https://demo.promlabs.com
```

### Test Each Command

```bash
# 1. Instant query — check which targets are up
bash scripts/prom-query.sh query 'up'

# 2. Range query — CPU idle time over the last hour
bash scripts/prom-query.sh range 'rate(node_cpu_seconds_total{mode="idle"}[5m])' --start=-1h --step=1m

# 3. Alerts — list all alerts (may be empty on demo server)
bash scripts/prom-query.sh alerts

# 4. Targets — check scrape target health
bash scripts/prom-query.sh targets

# 5. Explore — find metrics related to HTTP
bash scripts/prom-query.sh explore 'http'

# 6. Rules — list all rules (may be empty on demo server)
bash scripts/prom-query.sh rules
```

### Expected Behavior

| Command | Expected |
|---------|----------|
| `query 'up'` | Returns JSON with `resultType: "vector"`, list of targets with value `1` (up) or `0` (down) |
| `range '...' --start=-1h` | Returns JSON with `series` array, each containing `summary` with min/max/avg and `values` array |
| `alerts` | Returns JSON with `alerts` array (may be empty), `byState` and `bySeverity` summaries |
| `targets` | Returns JSON with `active` array showing health of each target, `summary` with counts |
| `explore 'http'` | Returns JSON with matching metric names and their types/descriptions |
| `rules` | Returns JSON with `groups` array and rule details |

## Testing with Local Prometheus

### Option 1: Docker

```bash
# Start Prometheus with default config
docker run -d --name prometheus -p 9090:9090 prom/prometheus:latest

# Set URL
export PROMETHEUS_URL=http://localhost:9090

# Run tests
bash scripts/prom-query.sh query 'up'
bash scripts/prom-query.sh targets
bash scripts/prom-query.sh explore 'prometheus'
```

### Option 2: Docker Compose with Sample Metrics

Create `docker-compose.yml`:

```yaml
version: '3'
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
```

Add to `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

This gives you real node metrics (CPU, memory, disk, network) to query.

## Error Handling Tests

```bash
# Missing PROMETHEUS_URL
unset PROMETHEUS_URL
bash scripts/prom-query.sh query 'up' 2>&1 | grep -q "PROMETHEUS_URL is not set" && echo "✅ Missing URL handled"

# Invalid URL scheme
PROMETHEUS_URL=ftp://bad bash scripts/prom-query.sh query 'up' 2>&1 | grep -q "must start with http" && echo "✅ Bad scheme handled"

# Invalid PromQL
export PROMETHEUS_URL=https://demo.promlabs.com
bash scripts/prom-query.sh query 'invalid{{{' 2>&1 | grep -qi "error" && echo "✅ Bad PromQL handled"

# Unreachable server
PROMETHEUS_URL=http://192.0.2.1:9090 bash scripts/prom-query.sh query 'up' 2>&1 | grep -qi "cannot reach" && echo "✅ Unreachable handled"

# Missing command
bash scripts/prom-query.sh 2>&1 | grep -q "USAGE" && echo "✅ No-args shows help"

# Unknown command
bash scripts/prom-query.sh foobar 2>&1 | grep -q "Unknown command" && echo "✅ Unknown command handled"
```

## Downsampling Test

```bash
# Request a very long range with tiny step — should auto-downsample
export PROMETHEUS_URL=https://demo.promlabs.com
bash scripts/prom-query.sh range 'up' --start=-7d --step=1s | jq '.timeRange.downsampled'
# Expected: true
```

## Full Test Suite Script

```bash
#!/usr/bin/env bash
set -euo pipefail

SCRIPT="scripts/prom-query.sh"
PASS=0
FAIL=0

check() {
  local name="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    echo "✅ ${name}"
    ((PASS++))
  else
    echo "❌ ${name}"
    ((FAIL++))
  fi
}

# Syntax
check "bash -n" bash -n "$SCRIPT"

# Help
check "help output" bash "$SCRIPT" --help

# Version
check "version output" bash "$SCRIPT" --version

# Live tests (requires PROMETHEUS_URL)
if [[ -n "${PROMETHEUS_URL:-}" ]]; then
  check "query up" bash "$SCRIPT" query 'up'
  check "range query" bash "$SCRIPT" range 'up' --start=-15m --step=1m
  check "alerts" bash "$SCRIPT" alerts
  check "targets" bash "$SCRIPT" targets
  check "explore" bash "$SCRIPT" explore 'up'
  check "rules" bash "$SCRIPT" rules
fi

echo ""
echo "Results: ${PASS} passed, ${FAIL} failed"
[[ $FAIL -eq 0 ]] && exit 0 || exit 1
```

Powered by Anvil AI 📊
