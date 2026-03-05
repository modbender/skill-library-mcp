# Directory Structure

## Root Layout

```
workflows/
├── index.md
├── components/
│   ├── connections/
│   │   └── {service}.md
│   ├── nodes/
│   │   └── {operation}.md
│   └── triggers/
│       └── {source}.md
└── flows/
    └── {workflow-name}/
        ├── flow.md
        ├── config.yaml
        ├── run.sh
        ├── CHANGELOG.md
        ├── state/
        │   ├── cursor.json
        │   └── checkpoint.json
        ├── data/
        │   └── {step}.json
        └── logs/
            └── {timestamp}.jsonl
```

## index.md Format

```markdown
# Workflow Index

## Active

### daily-email-digest
**Trigger:** cron 08:00 Europe/Madrid
**Does:** Summarizes overnight emails
**Uses:** gmail, openai, pushover
**Tags:** email, notification, daily
**Category:** communication
**Version:** 1.2
**Created:** 2024-01-15

### price-monitor
**Trigger:** cron */6h UTC
**Does:** Checks competitor prices, alerts on >5% change
**Uses:** fetch, diff, slack
**Tags:** monitoring, pricing, alert
**Category:** monitoring
**Upstream:** none
**Downstream:** weekly-report
**Version:** 2.0
**Created:** 2024-01-20
```

### Categories
- `communication` — email, chat, notifications
- `monitoring` — health checks, price tracking, alerts
- `backup` — data, files, snapshots
- `integration` — sync between services
- `reporting` — digests, summaries, PDFs

### Tags
Use 3-5 tags from: trigger type (daily, hourly, event, manual), domain (email, files, api, web), action (notify, backup, sync, alert, transform).

## flow.md Format

```markdown
# {Workflow Name}

**Version:** 1.0

## Trigger
- **Type:** cron | webhook | manual
- **Schedule:** {cron expression} (if cron)
- **Timezone:** {timezone} (required for cron)
- **Webhook:** {path} (if webhook)

## Config
References `config.yaml`. List key parameters:
- `threshold`: 0.05
- `recipients`: [list]

## Nodes

### 1. {Node Name}
- **Action:** {what it does}
- **Input:** `{previous-step}.json` or trigger payload
- **Input schema:** `{ email: string, timestamp: ISO8601 }`
- **Output:** `data/01-{name}.json`
- **Output schema:** `{ items: array, count: number }`
- **On error:** retry(3) | fail | continue
- **On empty:** skip | continue | fail
- **Component:** nodes/{name}.md (if reusable)

### 2. {Node Name}
...

## Output
{What the workflow produces when complete}

## Dependencies
- **Upstream:** {workflow that must run first, if any}
- **Downstream:** {workflows that depend on this}
```

## config.yaml Format

```yaml
# Workflow parameters (non-secrets)
threshold: 0.05
max_items: 100
recipients:
  - team@example.com
notify_channel: "#alerts"

# Environment-specific overrides
environments:
  production:
    notify_channel: "#prod-alerts"
  test:
    recipients:
      - test@example.com
```

## CHANGELOG.md Format

```markdown
# Changelog

## v1.2 (2024-02-01)
- Changed: filter logic for edge case X
- Fixed: timeout on slow connections

## v1.1 (2024-01-20)
- Added: retry logic for API calls

## v1.0 (2024-01-15)
- Initial version
```

## Logging Format

Use JSON Lines (`.jsonl`) with structured entries:

```json
{"ts":"2024-01-15T08:00:01Z","run_id":"abc123","node":"fetch","status":"ok","count":15}
{"ts":"2024-01-15T08:00:05Z","run_id":"abc123","node":"filter","status":"ok","count":3}
{"ts":"2024-01-15T08:00:10Z","run_id":"abc123","node":"summarize","status":"error","error":"timeout"}
```

Fields:
- `ts`: ISO8601 timestamp
- `run_id`: Unique per execution (first 8 chars of UUID)
- `node`: Current step name
- `status`: ok | error | skip
- `error`: Error message (if status=error)
- Additional fields per node (count, duration_ms, etc.)

## Naming Conventions

- **Workflow folders:** `kebab-case` (daily-email-digest)
- **Component files:** `lowercase` (gmail.md, pushover.md)
- **Scripts:** `run.sh` (or `.py`, `.js`)
- **Data files:** `{NN}-{node-name}.json` (01-fetch.json, 02-filter.json)
- **Log files:** `{YYYY-MM-DD-HH-MM-SS}.jsonl`
- **Secrets:** `{workflow}_{service}_{purpose}` (daily-digest_gmail_oauth)
