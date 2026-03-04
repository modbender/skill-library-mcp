---
name: datadog
description: "Datadog monitoring — manage monitors, dashboards, metrics, logs, events, and incidents via REST API"
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+ (stdlib only — no dependencies)
metadata: {"openclaw": {"emoji": "🐕", "requires": {"env": ["DD_API_KEY", "DD_APP_KEY"]}, "primaryEnv": "DD_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# 🐕 Datadog

Datadog monitoring — manage monitors, dashboards, metrics, logs, events, and incidents via REST API

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `DD_API_KEY` | ✅ | API key from app.datadoghq.com |
| `DD_APP_KEY` | ✅ | Application key |

## Quick Start

```bash
# List monitors
python3 {{baseDir}}/scripts/datadog.py monitors --query <value> --tags <value>

# Get monitor
python3 {{baseDir}}/scripts/datadog.py monitor-get id <value>

# Create monitor
python3 {{baseDir}}/scripts/datadog.py monitor-create --name <value> --type <value> --query <value> --message <value>

# Update monitor
python3 {{baseDir}}/scripts/datadog.py monitor-update id <value> --name <value> --query <value>

# Delete monitor
python3 {{baseDir}}/scripts/datadog.py monitor-delete id <value>

# Mute monitor
python3 {{baseDir}}/scripts/datadog.py monitor-mute id <value>

# List dashboards
python3 {{baseDir}}/scripts/datadog.py dashboards

# Get dashboard
python3 {{baseDir}}/scripts/datadog.py dashboard-get id <value>
```

## All Commands

| Command | Description |
|---------|-------------|
| `monitors` | List monitors |
| `monitor-get` | Get monitor |
| `monitor-create` | Create monitor |
| `monitor-update` | Update monitor |
| `monitor-delete` | Delete monitor |
| `monitor-mute` | Mute monitor |
| `dashboards` | List dashboards |
| `dashboard-get` | Get dashboard |
| `dashboard-create` | Create dashboard |
| `dashboard-delete` | Delete dashboard |
| `metrics-search` | Search metrics |
| `metrics-query` | Query metrics |
| `events-list` | List events |
| `event-create` | Create event |
| `logs-search` | Search logs |
| `incidents` | List incidents |
| `incident-get` | Get incident |
| `hosts` | List hosts |
| `downtimes` | List downtimes |
| `downtime-create` | Create downtime |
| `slos` | List SLOs |
| `synthetics` | List synthetic tests |
| `users` | List users |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/datadog.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/datadog.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
