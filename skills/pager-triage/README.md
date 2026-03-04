# 🚨 pager-triage

**AI-powered PagerDuty incident triage for OpenClaw — because nobody should parse JSON at 3am.**

[![Version](https://img.shields.io/badge/version-0.1.1-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Author](https://img.shields.io/badge/by-Anvil%20AI-orange)]()

---

## What It Does

`pager-triage` gives your OpenClaw agent direct access to PagerDuty. List active incidents, deep-dive into timelines and alerts, check who's on call, acknowledge, resolve, and annotate — all through natural conversation. Read-only by default; write operations require explicit confirmation.

## Quick Install

```bash
clawhub install pager-triage
```

## Setup (2 minutes)

```bash
# 1. Create a PagerDuty API key
#    PagerDuty → Settings → API Access Keys → Create New API Key
#    Name: "OpenClaw Agent" → Select "Read-only" (or Full Access for ack/resolve)

# 2. Set environment variables
export PAGERDUTY_API_KEY="u+your_key_here"

# Optional — only needed for ack/resolve/note
export PAGERDUTY_EMAIL="you@company.com"

# 3. Verify
# Ask your agent: "What's firing on PagerDuty?"
```

## Example: 3am Incident Triage

```
You:    What's firing?

Agent:  Checking PagerDuty... 🔍

        Found 2 active incidents:

        🔴 #4521 — High CPU on prod-web-03
           Service: Production Web | Urgency: HIGH | Triggered 45 min ago
           Assigned to: Jane Doe (Level 1) | 3 alerts

        🟡 #4520 — Elevated error rate on auth-service
           Service: Auth Service | Urgency: LOW | Triggered 2 hours ago
           Assigned to: Bob Smith (Level 1) | 1 alert

You:    Tell me more about #4521

Agent:  Deep-diving into incident P123ABC... 🔍

        📋 Incident: High CPU on prod-web-03
        Status: TRIGGERED | Urgency: HIGH | Duration: 45 minutes

        📊 Timeline:
        03:00 — Triggered via Prometheus Alertmanager
        03:05 — Escalated to Jane Doe (Level 1)
        03:05 — Notified Jane Doe via push, SMS

        🚨 Alerts (3):
        • CPU > 95% on prod-web-03 (critical) — source: Prometheus
        • Memory > 90% on prod-web-03 (warning) — source: Prometheus
        • High load average on prod-web-03 (warning) — source: Prometheus

        📝 Notes: none yet

        The trigger source is Prometheus Alertmanager. Want me to query
        Prometheus for the CPU metrics on prod-web-03? I can also check
        Kubernetes pod health if kube-medic is installed.

You:    Ack it while I investigate

Agent:  ⚠️ ACKNOWLEDGE INCIDENT
        ID: P123ABC (#4521)
        Title: High CPU on prod-web-03
        Service: Production Web
        Urgency: HIGH

        This will stop escalation. Proceed?

You:    Yes

Agent:  ✅ Incident P123ABC acknowledged at 03:46 UTC.
        Escalation paused. Let me know when you want to resolve it.
```

## Features

| Feature | Description |
|---------|-------------|
| **List incidents** | All triggered + acknowledged incidents, sorted by urgency |
| **Incident deep-dive** | Full timeline, alerts, notes, and automated analysis |
| **On-call schedules** | Who's on call now across all escalation policies |
| **Service overview** | All services with operational status (critical/warning/active) |
| **Recent history** | Incident history with MTTR stats (24h/7d/30d windows) |
| **Acknowledge** | Stop escalation with confirmation gate |
| **Resolve** | Mark incidents as fixed with confirmation gate |
| **Add notes** | Document findings directly on the incident timeline |

## Subcommands

| Command | Type | Description |
|---------|------|-------------|
| `incidents` | 🟢 Read | List active incidents |
| `detail <id>` | 🟢 Read | Incident deep-dive |
| `oncall` | 🟢 Read | On-call schedules |
| `services` | 🟢 Read | Service health overview |
| `recent [--service ID] [--since 24h\|7d\|30d]` | 🟢 Read | Recent incident history |
| `ack <id> --confirm` | 🟡 Write | Acknowledge incident |
| `resolve <id> --confirm` | 🟡 Write | Resolve incident |
| `note <id> --content "..." --confirm` | 🟡 Write | Add incident note |

## OpenClaw Discord v2 Ready

Compatible with OpenClaw Discord channel behavior documented for v2026.2.14+:
- Compact first incident summary (active count + highest urgency)
- Component-style quick actions when available (`Deep Dive Incident`, `Acknowledge Incident`, `Add Incident Note`)
- Numbered-list fallback when components are unavailable

## Safety First

- **Read-only by default** — 5 read commands need no confirmation
- **Write operations gated** — `ack`, `resolve`, and `note` require `--confirm` flag
- **Credentials never exposed** — API keys are read from env vars only, masked in errors
- **Input sanitized** — Incident IDs validated as alphanumeric before any API call

See [SECURITY.md](./SECURITY.md) for the full threat model.

## Companion Skills

`pager-triage` is most powerful when combined with:

| Skill | What It Adds |
|-------|-------------|
| **[prom-query](https://clawhub.com/skills/prom-query)** | Query Prometheus metrics — correlate incidents with CPU, memory, latency, error rates |
| **[kube-medic](https://clawhub.com/skills/kube-medic)** | Kubernetes cluster health — check pods, restarts, OOMKills, node status |
| **[log-dive](https://clawhub.com/skills/log-dive)** | Log search — find error patterns around incident timeframes |

Together, they give your agent a complete incident response toolkit: **see the alert → read the metrics → check the pods → search the logs → ack → resolve**.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `PAGERDUTY_API_KEY` | Yes | PagerDuty REST API v2 token |
| `PAGERDUTY_EMAIL` | For writes | Your PagerDuty login email (required for ack/resolve/note) |

## Requirements

- `curl` and `jq` must be available in the agent's runtime
- PagerDuty REST API v2 access (standard on all PagerDuty plans)

## License

MIT — see [LICENSE](./LICENSE)

---

<p align="center">
  <strong>Built by <a href="https://anvil-ai.io">Anvil AI</a></strong><br>
  <em>For the engineer who gets paged at 3am</em>
</p>
