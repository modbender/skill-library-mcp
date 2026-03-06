# 🤿 log-dive

**Unified Log Search Across Loki, Elasticsearch, and CloudWatch**

> "Find me the error logs from the checkout service in the last 30 minutes"

One skill. Three backends. Natural language queries translated to LogQL, ES Query DSL, or CloudWatch filter patterns — and the LLM correlates patterns across services.

## Why

Log search during incidents is painful:
- You need to remember three different query syntaxes
- You navigate different UIs for different backends
- You manually scan hundreds of lines looking for the root cause
- Errors in service A are caused by service B, but you're only looking at A

**log-dive** fixes all of this. Ask in plain English. Get a structured analysis with root cause, timeline, and recommended actions.

## Features

- 🔍 **Natural language → query translation** — "find timeout errors in the payment service" becomes the right LogQL/ES DSL/CW filter
- 🔗 **Multi-backend support** — Query Loki, Elasticsearch, and CloudWatch through one interface
- 🧠 **AI-powered correlation** — LLM reads raw logs, finds patterns, traces root causes across services
- 📊 **Structured output** — Error summaries, timelines, and action items (not raw log dumps)
- 🔒 **Read-only & safe** — Cannot delete or modify logs. Never caches log output.
- ⚡ **Smart limits** — Default 200-line cap with pre-filtering to keep token costs sane

## OpenClaw Discord v2 Ready

Compatible with OpenClaw Discord channel behavior documented for v2026.2.14+:
- Compact first response with top error patterns and likely root cause
- Component-style quick actions when available (`Show Error Timeline`, `Show Top Error Patterns`, `Run Related Service Query`)
- Numbered-list fallback when components are unavailable

## Quick Start

### 1. Configure at least one backend

**Loki:**
```bash
export LOKI_ADDR="http://loki.internal:3100"
export LOKI_TOKEN="your-token"        # optional
export LOKI_TENANT_ID="your-tenant"   # optional
```

**Elasticsearch / OpenSearch:**
```bash
export ELASTICSEARCH_URL="https://es.internal:9200"
export ELASTICSEARCH_TOKEN="Basic dXNlcjpwYXNz"  # optional
```

**AWS CloudWatch:**
```bash
export AWS_PROFILE="production"
export AWS_REGION="us-east-1"
# Or use AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY
```

### 2. Ask your agent

```
"What errors are happening in the checkout service?"
"Search for timeout exceptions in the last hour"
"Which log backends do I have configured?"
"List all available Loki labels"
"Tail the payment-service logs"
```

## Supported Backends

| Backend | Tool Required | Query Language | Status |
|---------|--------------|----------------|--------|
| **Grafana Loki** | `logcli` or `curl` | LogQL | ✅ Full support |
| **Elasticsearch / OpenSearch** | `curl` | Query DSL (JSON) | ✅ Full support |
| **AWS CloudWatch Logs** | `aws` CLI | Filter Patterns | ✅ Full support |

## Commands

| Command | Description |
|---------|-------------|
| `search --query <q>` | Search logs across configured backends |
| `backends` | Show which backends are configured and reachable |
| `indices` / `labels` | List available indices, log groups, or labels |
| `tail --query <q>` | Follow live log output (30s default) |

## Example Output

```markdown
## Log Search Results

**Backend:** Loki | **Query:** `{app="checkout"} |= "error"`
**Time range:** Last 30 minutes | **Results:** 47 entries

### Error Summary

| Error Type | Count | First Seen | Last Seen |
|-----------|-------|------------|-----------|
| NullPointerException | 23 | 14:02:31 | 14:28:45 |
| ConnectionTimeout | 18 | 14:05:12 | 14:29:01 |

### Root Cause Analysis
Database connection pool exhausted → checkout service NPEs → payment service 503s
```

## Security

- **Read-only** — All operations are search/read only. No write, delete, or admin operations.
- **No caching** — Log output is never written to disk. Logs may contain PII/secrets.
- **URL validation** — Only `http://` and `https://` schemes accepted.
- **Safe JSON** — All JSON construction uses `jq --arg` to prevent injection.

## Dependencies

| Tool | Required For | Install |
|------|-------------|---------|
| `jq` | All backends | `apt install jq` / `brew install jq` |
| `curl` | Loki, Elasticsearch | Usually pre-installed |
| `logcli` | Loki (optional, falls back to curl) | [Install guide](https://grafana.com/docs/loki/latest/tools/logcli/) |
| `aws` | CloudWatch | [Install guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) |

## License

MIT — Anvil AI 2026

---

Built by **[Anvil AI](https://anvil-ai.io)**.

