---
name: Plausible
slug: plausible
version: 1.0.1
homepage: https://clawic.com/skills/plausible
description: Query Plausible Analytics API for traffic stats, referrers, conversions, and custom events.
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":[],"env":["PLAUSIBLE_API_KEY"]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines.

## When to Use

User needs website traffic data from Plausible. Agent queries visitors, pageviews, referrers, goals, and custom events through the Plausible API.

## Architecture

Memory lives in `~/plausible/`. See `memory-template.md` for structure.

```
~/plausible/
├── memory.md     # Sites + preferences (no secrets stored)
└── queries/      # Saved query templates (optional)
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |

## Core Rules

### 1. API Key from Environment
API key comes from `PLAUSIBLE_API_KEY` environment variable. Never hardcode or ask user to paste keys in chat.

### 2. Site ID Required
Every query needs a site_id (domain). Check memory.md for configured sites before asking.

### 3. Time Periods
Default to `30d` unless user specifies. Valid periods: `day`, `7d`, `30d`, `month`, `6mo`, `12mo`, `custom` (requires date/date_range).

### 4. Metrics Available
| Metric | Description |
|--------|-------------|
| `visitors` | Unique visitors |
| `visits` | Total sessions |
| `pageviews` | Total page views |
| `views_per_visit` | Pages per session |
| `bounce_rate` | Single-page visits % |
| `visit_duration` | Avg session length (seconds) |
| `events` | Custom event count |
| `conversion_rate` | Goal conversion % (requires goal filter) |

### 5. Breakdown Dimensions
| Dimension | Description |
|-----------|-------------|
| `event:page` | Pages |
| `event:name` | Custom events |
| `visit:source` | Traffic sources |
| `visit:referrer` | Full referrer URLs |
| `visit:utm_source` | UTM source |
| `visit:utm_medium` | UTM medium |
| `visit:utm_campaign` | UTM campaign |
| `visit:device` | Desktop/Mobile/Tablet |
| `visit:browser` | Browser name |
| `visit:os` | Operating system |
| `visit:country` | Country code |
| `visit:city` | City name |

### 6. Filters Syntax
Filters use format: `dimension==value` or `dimension!=value`. Multiple filters with `;` (AND).

```
visit:source==Google
event:page==/pricing;visit:country==US
```

### 7. Rate Limits
600 requests/hour per API key. Cache results in memory when doing multiple queries.

## Common Traps

- Forgetting site_id → API returns 400
- Using wrong date format for custom range → use `YYYY-MM-DD`
- Requesting `conversion_rate` without goal filter → returns null
- Querying breakdown without metrics → defaults to visitors only

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| https://plausible.io/api/v1/stats/realtime/visitors | site_id | Realtime count |
| https://plausible.io/api/v1/stats/aggregate | site_id, metrics, period, filters | Aggregate stats |
| https://plausible.io/api/v1/stats/timeseries | site_id, metrics, period, interval | Time series |
| https://plausible.io/api/v1/stats/breakdown | site_id, property, metrics, filters | Breakdown by dimension |

Self-hosted instances use custom base URL from memory.md.

No other data is sent externally.

## Security & Privacy

**Data that leaves your machine:**
- Site ID (domain) and query parameters sent to Plausible API
- API key sent as Bearer token

**Data that stays local:**
- Query results cached in memory
- Site configurations in ~/plausible/

**This skill does NOT:**
- Store API keys in plain text (uses environment variable)
- Send user data beyond what's needed for queries
- Access files outside ~/plausible/

## Trust

By using this skill, your site analytics queries are sent to Plausible (plausible.io or your self-hosted instance).
Only install if you trust Plausible with your domain data.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `analytics` — general analytics guidance
- `umami` — alternative privacy analytics
- `mixpanel` — product analytics

## Feedback

- If useful: `clawhub star plausible`
- Stay updated: `clawhub sync`
