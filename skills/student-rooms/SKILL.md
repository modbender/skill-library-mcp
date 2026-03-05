---
name: student-rooms
description: Search, scan, and monitor student accommodation availability across Yugo and Aparto providers. Use when the user asks about student housing, room availability, semester accommodation, booking options, or price comparisons in any supported city. Covers Yugo (11 countries, 70+ cities including UK, Ireland, Spain, Germany, France, Italy, Portugal, Austria, Australia, USA, UAE) and Aparto (14 cities across Ireland, Spain, Italy, UK, France). Supports semester filtering, continuous watch mode with alerts, booking-flow probing, and multiple notification backends (stdout, webhook, Telegram, OpenClaw). Works standalone (no OpenClaw required) but has native OpenClaw integration for notifications and agent-mode alerts.
---

# student-rooms CLI

Multi-provider student accommodation finder and monitor. Query Yugo and Aparto for room availability, filter by semester and price, and get alerts when new options appear.

## Setup

```bash
cd /Users/thoth/.openclaw/workspace/yugo-scraper
source .venv/bin/activate
```

Config file: `config.yaml` (copy from `config.sample.yaml` if missing). Key settings:

```yaml
target:
  country: "Ireland"
  city: "Dublin"
academic_year:
  start_year: 2026
  end_year: 2027
filters:
  max_weekly_price: 350.0
notifications:
  type: "openclaw"  # or stdout | webhook | telegram
  openclaw:
    mode: "message"
    channel: "telegram"
    target: "CHAT_ID"
```

## Commands

All commands support `--provider yugo|aparto|all` (default: `all`) and `--json` for structured output.

### discover — List properties

```bash
python -m student_rooms discover --provider all
python -m student_rooms discover --provider all --json
python -m student_rooms discover --city Barcelona --provider aparto --json
```

Returns property names, slugs, locations, and URLs for the target city.

### scan — One-shot availability check

```bash
# Semester 1 rooms (default filter)
python -m student_rooms scan --provider all --json

# All options (full year, semester 2, etc.)
python -m student_rooms scan --all-options --json

# Scan + send notification for top match
python -m student_rooms scan --provider all --notify
```

JSON output structure:
```json
{
  "matchCount": 5,
  "matches": [
    {
      "provider": "yugo",
      "property": "Residence Name",
      "roomType": "Gold Ensuite",
      "priceWeekly": 310.0,
      "priceLabel": "€310/week",
      "available": true,
      "bookingUrl": "https://...",
      "startDate": "2026-09-01",
      "endDate": "2027-01-31",
      "optionName": "Semester 1",
      "dedupKey": "yugo|slug|gold ensuite|2026-27|Semester 1"
    }
  ]
}
```

### watch — Continuous monitoring

```bash
python -m student_rooms watch --provider all
```

Scans at configured interval (default 1h + random jitter). Alerts only on **new** options not previously seen. Persists seen options in `reports/seen_options.json`.

### probe-booking — Deep booking-flow probe

```bash
python -m student_rooms probe-booking --provider yugo --residence "Dominick Place" --json
python -m student_rooms probe-booking --provider aparto --residence "Binary Hub" --json
```

Returns booking context, available beds, direct booking links, and portal redirect URLs. Supports `--residence`, `--room`, `--tenancy`, `--index` filters.

### notify — Test notification

```bash
python -m student_rooms notify --message "Test alert 🏠"
```

### test-match — Test semester matching logic

```bash
python -m student_rooms test-match --from-year 2026 --to-year 2027 --name "Semester 1" --start-date 2026-09-01 --end-date 2027-01-31 --json
```

## Location override

Override config target with CLI flags:

```bash
python -m student_rooms scan --city Barcelona --country Spain --provider all --json
```

## Agent usage tips

- Always use `--json` for structured output.
- Use `scan --json` to check current availability; parse `matchCount` and `matches` array.
- Use `discover --json` to list what properties exist before scanning.
- Use `watch` as a background process for ongoing monitoring.
- Combine `scan --notify` to trigger alerts in a single command.
- The `dedupKey` field in scan output uniquely identifies each option for tracking.

## OpenClaw integration

Set `notifications.type: "openclaw"` in config. Supports two modes:

- **message**: Sends alert text via `openclaw message send` to a channel/target.
- **agent**: Triggers an OpenClaw agent session with the alert as context.

Optional: `create_job_on_match: true` creates a one-shot cron job for reservation assistance.

The tool works fully standalone — OpenClaw is only needed if you want the `openclaw` notification backend.

## Notification backends

| Backend | Config key | Requires |
|---------|-----------|----------|
| `stdout` | (default) | Nothing |
| `webhook` | `notifications.webhook.url` | Any HTTP endpoint (Discord, Slack, ntfy.sh) |
| `telegram` | `notifications.telegram.bot_token` + `chat_id` | Telegram bot |
| `openclaw` | `notifications.openclaw.target` | OpenClaw CLI installed |

## Provider notes

- **Yugo**: Dynamic API discovery (countries → cities → residences → rooms → tenancy options). Supports full booking-flow probing.
- **Aparto**: Scrapes apartostudent.com for property discovery, then probes StarRez portal termIDs. IE/ES/IT share one portal; UK has a separate portal; France has no StarRez portal (discover-only).
