---
name: healthie
description: "Healthie — manage patients, appointments, goals, and documents via GraphQL API"
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+ (stdlib only — no dependencies)
metadata: {"openclaw": {"emoji": "🏥", "requires": {"env": ["HEALTHIE_API_KEY"]}, "primaryEnv": "HEALTHIE_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# 🏥 Healthie

Healthie — manage patients, appointments, goals, and documents via GraphQL API

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `HEALTHIE_API_KEY` | ✅ | API key from Healthie developer settings |

## Quick Start

```bash
# List patients
python3 {{baseDir}}/scripts/healthie.py patients --offset <value> --keywords <value>

# Get patient
python3 {{baseDir}}/scripts/healthie.py patient-get id <value>

# Create patient
python3 {{baseDir}}/scripts/healthie.py patient-create --first_name <value> --last_name <value> --email <value>

# List appointments
python3 {{baseDir}}/scripts/healthie.py appointments --provider_id <value>

# Get appointment
python3 {{baseDir}}/scripts/healthie.py appointment-get id <value>

# Create appointment
python3 {{baseDir}}/scripts/healthie.py appointment-create --patient_id <value> --provider_id <value> --datetime <value>

# Delete appointment
python3 {{baseDir}}/scripts/healthie.py appointment-delete id <value>

# List appointment types
python3 {{baseDir}}/scripts/healthie.py appointment-types
```

## All Commands

| Command | Description |
|---------|-------------|
| `patients` | List patients |
| `patient-get` | Get patient |
| `patient-create` | Create patient |
| `appointments` | List appointments |
| `appointment-get` | Get appointment |
| `appointment-create` | Create appointment |
| `appointment-delete` | Delete appointment |
| `appointment-types` | List appointment types |
| `providers` | List providers |
| `goals` | List goals |
| `goal-create` | Create goal |
| `documents` | List documents |
| `forms` | List forms |
| `tags` | List tags |

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
python3 {{baseDir}}/scripts/healthie.py <command> --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{{baseDir}}/scripts/healthie.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
