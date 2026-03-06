---
name: fireflies-ai
description: "Fireflies.ai meeting intelligence — search meetings, get transcripts, action items, summaries, attendee info, and contacts via GraphQL API. No data storage; queries Fireflies servers directly. Use for meeting search, transcript lookup, action item extraction, meeting summaries, attendee lookup, and AI meeting notes."
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+ (stdlib only — no dependencies)
metadata: {"openclaw": {"emoji": "🔥", "requires": {"env": ["FIREFLIES_API_KEY"]}, "primaryEnv": "FIREFLIES_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# 🔥 Fireflies AI

Query your Fireflies.ai meeting data directly — transcripts, summaries, action items, contacts, and analytics. Zero storage: all data stays on Fireflies servers.

## Features

- **Search meetings** by keyword, date range, host, or participant
- **Get full transcripts** with speaker-attributed sentences
- **Extract action items** and meeting summaries
- **Meeting analytics** — sentiment, speaker stats, talk time
- **Contact lookup** — see who you've met with
- **User info** — account details and team members

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `FIREFLIES_API_KEY` | ✅ | API key from [app.fireflies.ai/integrations](https://app.fireflies.ai/integrations/custom/fireflies) |

## Quick Start

```bash
# List recent meetings
python3 {baseDir}/scripts/fireflies.py meetings --limit 10

# Search meetings by keyword (searches titles and spoken words)
python3 {baseDir}/scripts/fireflies.py search "quarterly review"

# Search within specific date range
python3 {baseDir}/scripts/fireflies.py meetings --from 2026-01-01 --to 2026-02-01

# Filter by participant email
python3 {baseDir}/scripts/fireflies.py meetings --participant "john@example.com"

# Filter by host email
python3 {baseDir}/scripts/fireflies.py meetings --host "jane@example.com"

# Get full transcript for a meeting
python3 {baseDir}/scripts/fireflies.py transcript <meeting_id>

# Get summary only
python3 {baseDir}/scripts/fireflies.py summary <meeting_id>

# Get action items only
python3 {baseDir}/scripts/fireflies.py actions <meeting_id>

# Get meeting analytics (sentiment, speaker stats)
python3 {baseDir}/scripts/fireflies.py analytics <meeting_id>

# Get attendee info for a meeting
python3 {baseDir}/scripts/fireflies.py attendees <meeting_id>

# List all contacts
python3 {baseDir}/scripts/fireflies.py contacts

# Get current user info
python3 {baseDir}/scripts/fireflies.py user

# Get team members
python3 {baseDir}/scripts/fireflies.py users
```

## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
# JSON (default, for programmatic use)
python3 {baseDir}/scripts/fireflies.py meetings --limit 5

# Human-readable
python3 {baseDir}/scripts/fireflies.py meetings --limit 5 --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/fireflies.py` | Main CLI — all queries in one tool |

## Data Policy

This skill **never stores meeting data locally**. Every query goes directly to the Fireflies GraphQL API (`https://api.fireflies.ai/graphql`) and results are returned to stdout. Your meeting data stays on Fireflies servers.

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
