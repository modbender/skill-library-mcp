---
name: fivetran
description: "Fivetran — manage connectors, destinations, sync status, and groups via REST API"
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+ (stdlib only — no dependencies)
metadata: {"openclaw": {"emoji": "🔗", "requires": {"env": ["FIVETRAN_API_KEY", "FIVETRAN_API_SECRET"]}, "primaryEnv": "FIVETRAN_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# 🔗 Fivetran

Fivetran — manage connectors, destinations, sync status, and groups via REST API

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `FIVETRAN_API_KEY` | ✅ | API key |
| `FIVETRAN_API_SECRET` | ✅ | API secret |

## Quick Start

```bash
# List connectors
python3 {{baseDir}}/scripts/fivetran.py connectors group_id <value>

# Get connector
python3 {{baseDir}}/scripts/fivetran.py connector-get id <value>

# Create connector
python3 {{baseDir}}/scripts/fivetran.py connector-create --service <value> --group_id <value> --config <value>

# Update connector
python3 {{baseDir}}/scripts/fivetran.py connector-update id <value> --paused <value>

# Delete connector
python3 {{baseDir}}/scripts/fivetran.py connector-delete id <value>

# Trigger sync
python3 {{baseDir}}/scripts/fivetran.py connector-sync id <value>

# Get schema
python3 {{baseDir}}/scripts/fivetran.py connector-schema id <value>

# List destinations
python3 {{baseDir}}/scripts/fivetran.py destinations
```

## All Commands

| Command | Description |
|---------|-------------|
| `connectors` | List connectors |
| `connector-get` | Get connector |
| `connector-create` | Create connector |
| `connector-update` | Update connector |
| `connector-delete` | Delete connector |
| `connector-sync` | Trigger sync |
| `connector-schema` | Get schema |
| `destinations` | List destinations |
| `destination-get` | Get destination |
| `groups` | List groups |
| `group-get` | Get group |
| `group-create` | Create group |
| `users` | List users |
| `metadata-connectors` | List connector types |
| `webhooks` | List webhooks |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/fivetran.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/fivetran.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
