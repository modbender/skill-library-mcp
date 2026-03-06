# Testing Guide — log-dive

## Prerequisites

- `bash` 4.0+
- `jq` 1.6+
- `curl` 7.x+
- At least one backend configured (see below)

## Quick Smoke Test

```bash
# Check that backends detection works (no backends needed)
bash scripts/log-dive.sh backends

# Expected: JSON showing which backends are configured/available
```

## Backend-Specific Testing

### Loki

```bash
# Set up
export LOKI_ADDR="http://localhost:3100"

# Test backends detection
bash scripts/log-dive.sh backends
# Expected: loki shows as "configured: true"

# Test label listing
bash scripts/log-dive.sh labels --backend loki
# Expected: JSON array of label names

# Test search
bash scripts/log-dive.sh search --backend loki --query '{job="varlogs"} |= "error"' --since 1h --limit 10

# Test with logcli (if installed)
which logcli && bash scripts/log-dive.sh search --backend loki --query '{job="varlogs"}' --since 1h --limit 10
```

### Elasticsearch

```bash
# Set up
export ELASTICSEARCH_URL="http://localhost:9200"

# Test backends detection
bash scripts/log-dive.sh backends
# Expected: elasticsearch shows as "configured: true"

# Test index listing
bash scripts/log-dive.sh indices --backend elasticsearch
# Expected: list of indices with doc counts

# Test search
bash scripts/log-dive.sh search --backend elasticsearch --query '{"query":{"match_all":{}}}' --index 'test-*' --since 1h --limit 10
```

### CloudWatch

```bash
# Set up
export AWS_REGION="us-east-1"
export AWS_PROFILE="dev"  # or set AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY

# Test backends detection
bash scripts/log-dive.sh backends
# Expected: cloudwatch shows as "configured: true"

# Test log group listing
bash scripts/log-dive.sh indices --backend cloudwatch
# Expected: list of log groups

# Test search
bash scripts/log-dive.sh search --backend cloudwatch --query '"ERROR"' --log-group '/ecs/myapp' --since 1h --limit 10
```

## Unit Tests (No Live Backends)

These tests validate script behavior without requiring live backends:

```bash
# Test: no backends configured (clear all env vars)
unset LOKI_ADDR ELASTICSEARCH_URL AWS_REGION AWS_PROFILE AWS_ACCESS_KEY_ID
bash scripts/log-dive.sh backends
# Expected: all backends show configured: false

# Test: URL validation rejects non-http schemes
LOKI_ADDR="ftp://evil.com" bash scripts/log-dive.sh search --backend loki --query 'test'
# Expected: error about invalid URL scheme

# Test: missing required tools
PATH="" bash scripts/log-dive.sh backends 2>&1
# Expected: error about missing jq

# Test: invalid subcommand
bash scripts/log-dive.sh invalid-command
# Expected: usage help text

# Test: search without --query
bash scripts/log-dive.sh search --backend loki
# Expected: error about missing query
```

## Docker-Based Integration Tests

For CI or isolated testing:

```bash
# Loki
docker run -d --name loki -p 3100:3100 grafana/loki:2.9.0
export LOKI_ADDR="http://localhost:3100"
bash scripts/log-dive.sh labels --backend loki

# Elasticsearch
docker run -d --name es -p 9200:9200 -e "discovery.type=single-node" -e "xpack.security.enabled=false" elasticsearch:8.12.0
export ELASTICSEARCH_URL="http://localhost:9200"
bash scripts/log-dive.sh indices --backend elasticsearch

# LocalStack for CloudWatch
docker run -d --name localstack -p 4566:4566 localstack/localstack
export AWS_ENDPOINT_URL="http://localhost:4566"
export AWS_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="test"
export AWS_SECRET_ACCESS_KEY="test"
bash scripts/log-dive.sh indices --backend cloudwatch
```

## Validation Checklist

- [ ] `backends` command works with zero backends configured
- [ ] `backends` command detects each backend independently
- [ ] `search` rejects invalid URL schemes
- [ ] `search` respects `--limit` flag
- [ ] `search` returns valid JSON output
- [ ] `indices`/`labels` work for each backend
- [ ] Error messages are specific (not generic "something went wrong")
- [ ] Scripts exit non-zero on errors
- [ ] No log data written to disk (check with `strace` or `fs_usage`)
- [ ] `set -euo pipefail` is present in all scripts

---

*Powered by Anvil AI 🤿*
