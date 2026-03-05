# prom-query

**Prometheus Metrics Query & Alert Interpreter for OpenClaw**

Ask your agent *"is the API healthy?"* and it queries Prometheus directly, interprets the timeseries data, and explains what's happening — in plain English.

![Version](https://img.shields.io/badge/version-1.0.1-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Read-only](https://img.shields.io/badge/operations-read--only-brightgreen)

---

## What It Does

**prom-query** gives your AI agent direct access to your Prometheus metrics server. Instead of switching to Grafana dashboards or writing PromQL by hand, just ask:

- *"What alerts are firing right now?"*
- *"Show me the error rate for the payments service over the last hour"*
- *"Which pods are using the most CPU?"*
- *"Is the database healthy?"*
- *"What happened to latency at 3am?"*

The agent translates your question to PromQL, queries Prometheus, and interprets the results for you.

### Supported Backends

Works with any Prometheus-compatible API:

| Backend | Supported |
|---------|-----------|
| **Prometheus** | ✅ |
| **Thanos** | ✅ |
| **Grafana Mimir** | ✅ |
| **VictoriaMetrics** | ✅ |

## Install

```bash
clawhub install prom-query
```

Then set your Prometheus URL:

```bash
export PROMETHEUS_URL=https://prometheus.your-company.com
# Optional: bearer token for auth
export PROMETHEUS_TOKEN=your-token-here
```

That's it. One command, one env var.

## Example Interaction

```
You: Are there any alerts firing?

Agent: Let me check your Prometheus alerts.
       [runs: prom-query alerts --state=firing]

       🔴 2 alerts are currently firing:

       CRITICAL — HighErrorRate
         Service: payments-api
         Firing since: 14 minutes ago
         Summary: Error rate is above 5% (current: 8.3%)

       WARNING — HighMemoryUsage
         Service: cache-redis
         Firing since: 2 hours ago
         Summary: Memory usage above 80% (current: 87.2%)

       I'd recommend looking at the payments-api error rate first since it's
       critical. Want me to pull the error rate timeseries for the last hour?
```

```
You: Yes, show me the error rate trend

Agent: [runs: prom-query range 'rate(http_requests_total{service="payments-api",code=~"5.."}[5m])' --start=-1h --step=1m]

       📈 Error rate for payments-api (last hour):

       The error rate was stable at ~0.1% until 14 minutes ago when it
       spiked to 8.3%. The spike correlates exactly with the alert firing time.

       The error rate is still elevated at 7.9% — this isn't recovering on its own.

       Possible causes:
       • A recent deployment (check your CD pipeline)
       • A downstream dependency failure
       • Resource exhaustion (memory/CPU)

       Want me to check CPU and memory for payments-api pods?
```

## Commands

| Command | Description |
|---------|-------------|
| `prom-query query '<promql>'` | Instant query — current value |
| `prom-query range '<promql>' [--start= --end= --step=]` | Range query — timeseries data |
| `prom-query alerts [--state=firing\|pending]` | Active alerts grouped by severity |
| `prom-query targets [--state=active\|dropped]` | Scrape target health check |
| `prom-query explore [pattern]` | Search available metrics |
| `prom-query rules [--type=alert\|record]` | Alerting & recording rules |

## Features

- **🧠 Natural Language → PromQL:** SKILL.md teaches the agent common PromQL patterns for error rates, latency percentiles, CPU, memory, disk, and Kubernetes metrics.
- **📊 Smart Downsampling:** Range queries with thousands of data points are automatically downsampled to stay within LLM context limits.
- **🔍 Metric Explorer:** Don't know the metric name? `explore` searches all available metrics with descriptions.
- **🚨 Alert Triage:** Alerts grouped by severity with firing duration and recommended next steps.
- **🎯 Target Health:** Instantly see which scrape targets are down and why.
- **🔒 Read-Only:** Never modifies your Prometheus. Zero write operations.
- **🔐 Secure:** Tokens never appear in output. URL validation. No injection patterns.

## OpenClaw Discord v2 Ready

Compatible with OpenClaw Discord channel behavior documented for v2026.2.14+:
- Uses a compact first response for alert triage and quick operator context
- Supports component-style follow-up actions when available (`Show Last 1h Trend`, `List Firing Alerts`, `Explore Related Metrics`)
- Falls back to concise numbered next actions when components are unavailable

## Requirements

- `bash` 4.0+
- `curl`
- `jq`
- Network access to your Prometheus server

## Security

- All operations are **read-only** (read-only API queries only)
- Bearer tokens are sent via HTTP headers, never logged or printed
- URL scheme validated (http/https only)
- All JSON construction uses `jq --arg` (no string interpolation)
- See [SECURITY.md](SECURITY.md) for full details

## License

MIT — use it however you want.

---

## More from Anvil AI

This skill is part of the **Anvil AI** open-source skill suite.

| Skill | What it does |
|-------|-------------|
| **[vibe-check](https://clawhub.com/skills/vibe-check)** | AI code quality + security review scorecard. |
| **[rug-checker](https://clawhub.com/skills/rug-checker)** | Solana token rug-pull risk analysis. |
| **[dep-audit](https://clawhub.com/skills/dep-audit)** | Dependency vulnerability auditing across npm/pip/cargo/go. |
| **[prom-query](https://clawhub.com/skills/prom-query)** | This skill — Prometheus query + alert triage. |


---

Built by **[Anvil AI](https://anvil-ai.io)**.

