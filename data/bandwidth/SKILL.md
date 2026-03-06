---
name: bandwidth
description: "Bandwidth — messaging, voice calls, phone numbers, and 911 services."
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+ (stdlib only — no dependencies)
metadata: {"openclaw": {"emoji": "📡", "requires": {"env": ["BANDWIDTH_API_TOKEN", "BANDWIDTH_ACCOUNT_ID"]}, "primaryEnv": "BANDWIDTH_API_TOKEN", "homepage": "https://www.agxntsix.ai"}}
---

# 📡 Bandwidth

Bandwidth — messaging, voice calls, phone numbers, and 911 services.

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `BANDWIDTH_API_TOKEN` | ✅ | Bandwidth API token |
| `BANDWIDTH_ACCOUNT_ID` | ✅ | Account ID |


## Quick Start

```bash
# Send SMS/MMS
python3 {{baseDir}}/scripts/bandwidth.py send-message --from <value> --to <value> --text <value> --application-id <value>

# List messages
python3 {{baseDir}}/scripts/bandwidth.py list-messages --from <value> --to <value>

# Create outbound call
python3 {{baseDir}}/scripts/bandwidth.py create-call --from <value> --to <value> --answer-url <value> --application-id <value>

# Get call details
python3 {{baseDir}}/scripts/bandwidth.py get-call <id>

# List phone numbers
python3 {{baseDir}}/scripts/bandwidth.py list-numbers

# Search available numbers
python3 {{baseDir}}/scripts/bandwidth.py search-numbers --area-code <value> --quantity "10"

# Order phone number
python3 {{baseDir}}/scripts/bandwidth.py order-number --numbers "comma-separated"

# List applications
python3 {{baseDir}}/scripts/bandwidth.py list-applications
```

## Output Format

All commands output JSON by default.

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/bandwidth.py` | Main CLI — all commands in one tool |

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
