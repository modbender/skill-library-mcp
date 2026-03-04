---
name: Matomo Analytics
slug: matomo
version: 1.0.1
homepage: https://clawic.com/skills/matomo
description: Query, analyze, and manage Matomo Analytics with API integration, custom reports, and goal tracking.
metadata: {"clawdbot":{"emoji":"📊","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines. The skill stores configuration in `~/matomo/`.

## When to Use

User needs to query Matomo analytics, generate reports, track goals, or manage their self-hosted analytics. Agent handles API queries, data analysis, visitor insights, and conversion tracking.

## Architecture

Memory lives in `~/matomo/`. See `memory-template.md` for structure.

```
~/matomo/
├── memory.md         # Sites, credentials ref, preferences
├── reports/          # Saved report templates
└── queries/          # Reusable API query templates
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| API reference | `api.md` |
| Report templates | `reports.md` |

## Core Rules

### 1. Never Expose Credentials
- Token is stored in system keychain or env var, never in memory files
- Refer to credentials by reference name only
- If user pastes token in chat, warn and suggest secure storage

### 2. Use Reporting API for Reads
```bash
# Base pattern
curl -s "https://{matomo_url}/index.php?module=API&method={method}&idSite={site_id}&period={period}&date={date}&format=json&token_auth={token}"
```
Common methods:
- `VisitsSummary.get` — visitors, visits, pageviews
- `Actions.getPageUrls` — top pages
- `Referrers.getWebsites` — traffic sources
- `Goals.get` — conversion data

### 3. Understand Date Ranges
| Period | Date Format | Example |
|--------|-------------|---------|
| `day` | `YYYY-MM-DD` | `2025-01-15` |
| `week` | `YYYY-MM-DD` | Week containing that date |
| `month` | `YYYY-MM` | `2025-01` |
| `year` | `YYYY` | `2025` |
| `range` | `YYYY-MM-DD,YYYY-MM-DD` | `2025-01-01,2025-01-31` |

Special dates: `today`, `yesterday`, `last7`, `last30`, `lastMonth`, `lastYear`

### 4. Handle Multi-Site Setups
- Always confirm which site before querying
- Store site list in memory.md with idSite mappings
- Default to most-used site if configured

### 5. Format Data for Humans
- Round percentages to 1 decimal
- Use K/M suffixes for large numbers
- Compare periods when context helps (vs last week/month)
- Highlight significant changes (>10% delta)

### 6. Respect Rate Limits
- Batch related queries into single date range when possible
- Cache recent results in memory for follow-up questions
- Avoid querying same data repeatedly in conversation

### 7. Use Segments for Deeper Insights
Segments filter data by visitor attributes. Add `&segment=` to any query:

```bash
# Mobile visitors only
&segment=deviceType==smartphone

# From specific country
&segment=countryCode==US

# Returning visitors who converted
&segment=visitorType==returning;goalConversionsSome>0

# Combine with AND (;) or OR (,)
&segment=browserCode==CH;operatingSystemCode==WIN
```

Common segment dimensions:
- `deviceType` — smartphone, tablet, desktop
- `browserCode` — CH (Chrome), FF (Firefox), SF (Safari)
- `countryCode` — ISO 2-letter code
- `visitorType` — new, returning
- `referrerType` — direct, search, website, campaign

## Matomo Traps

- **Wrong idSite** → querying wrong property, misleading data. Always confirm site first.
- **Forgetting token_auth** → 403 or empty response. Token required for all non-public methods.
- **date vs period mismatch** → confusing results. `period=range` requires `date=start,end` format.
- **Expecting GA terminology** → Matomo uses "visits" not "sessions", "actions" not "events". Translate mentally.
- **Ignoring segments** → missing the real insight. Segments filter data by visitor attributes.

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| `{user_matomo_url}/index.php` | API method, site ID, date range, auth token | Query analytics data |

No other data is sent externally. All requests go to user's own Matomo instance.

## Security & Privacy

**Data that leaves your machine:**
- API queries sent to user's Matomo instance only
- Auth token included in requests (user-controlled)

**Data that stays local:**
- Site configurations in ~/matomo/
- Report templates
- No data sent to third parties

**This skill does NOT:**
- Store auth tokens in plain text
- Send data to any service except user's Matomo
- Access files outside ~/matomo/

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `analytics` — general analytics patterns
- `umami` — privacy-focused analytics
- `api` — REST API integration

## Feedback

- If useful: `clawhub star matomo`
- Stay updated: `clawhub sync`
