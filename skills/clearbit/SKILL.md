---
name: clearbit
description: "Clearbit — person enrichment, company enrichment, prospecting, and reveal (identify website visitors)."
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+ (stdlib only — no dependencies)
metadata: {"openclaw": {"emoji": "🔮", "requires": {"env": ["CLEARBIT_API_KEY"]}, "primaryEnv": "CLEARBIT_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# 🔮 Clearbit

Clearbit — person enrichment, company enrichment, prospecting, and reveal (identify website visitors).

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `CLEARBIT_API_KEY` | ✅ | Clearbit API key (or HubSpot Clearbit key) |


## Quick Start

```bash
# Enrich person by email
python3 {{baseDir}}/scripts/clearbit.py enrich-person --email <value>

# Enrich company by domain
python3 {{baseDir}}/scripts/clearbit.py enrich-company --domain <value>

# Combined person + company lookup
python3 {{baseDir}}/scripts/clearbit.py combined-lookup --email <value>

# Prospect/search for leads
python3 {{baseDir}}/scripts/clearbit.py prospect --query "JSON filter object"

# Reveal company by IP address
python3 {{baseDir}}/scripts/clearbit.py reveal --ip <value>

# Find company domain by name
python3 {{baseDir}}/scripts/clearbit.py name-to-domain --name <value>
```

## Output Format

All commands output JSON by default.

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/clearbit.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
