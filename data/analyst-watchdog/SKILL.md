---
name: analyst-watchdog
version: 1.0.0
description: Automated monitoring agent that watches an API scoreboard, detects milestones, writes findings to markdown, and alerts via file-based triggers. Use when you need an autonomous agent that monitors a system and produces structured analysis without human intervention.
metadata:
  {"openclaw": {"emoji": "📊", "requires": {"bins": ["python3"], "env": []}, "primaryEnv": null, "network": {"outbound": false, "reason": "Reads from a local API endpoint (localhost). All output is written to local files."}}}
---

# Analyst Watchdog

An autonomous monitoring agent pattern: watch a system, detect changes, write findings, alert when thresholds are crossed. Runs on a schedule (LaunchAgent or cron) without human intervention.

## Pattern

```
API Endpoint → Poll → Detect Changes → Write FINDINGS.md
                                      → Write OUTBOX.md (for orchestrator)
                                      → Write ALERT_TELEGRAM.md (urgent)
```

## What It Monitors

Configurable, but the reference implementation tracks:
- Model evaluation scores hitting milestones (n=50, 100, 150, 200)
- Promotion events (model proven equivalent to cloud baseline)
- Score anomalies (sudden drops or improvements)
- System health degradation

## Alert Tiers

| File | Urgency | Who Reads It |
|---|---|---|
| `FINDINGS.md` | Low | Background knowledge |
| `OUTBOX.md` | Medium | Orchestrator on next heartbeat |
| `ALERT_TELEGRAM.md` | High | Sent immediately, then deleted |

## Files

- `scripts/analyst_agent.py` — Reference watchdog implementation
