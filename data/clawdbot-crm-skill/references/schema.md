# CRM Schema Reference

## Person Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | ✓ | Full name |
| type | string | ✓ | Always "person" |
| tags | list | | Categorization tags |
| company | string | | Current employer (slug or name) |
| role | string | | Job title |
| email | string | | Email address |
| phone | string | | Phone number |
| telegram | string | | Telegram handle (with @) |
| twitter | string | | Twitter/X handle (with @) |
| linkedin | string | | LinkedIn profile URL |
| website | string | | Personal website |
| location | string | | City/Country |
| introduced_by | string | | Slug of person who introduced |
| met_at | string | | Slug of event where met |
| first_contact | date | | First interaction date (YYYY-MM-DD) |
| last_contact | date | | Most recent interaction (YYYY-MM-DD) |
| follow_up | date | | Next follow-up date (YYYY-MM-DD) |
| status | enum | | active, dormant, archived |

## Company Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | ✓ | Company name |
| type | string | ✓ | Always "company" |
| tags | list | | Categorization tags |
| industry | string | | Industry/sector |
| website | string | | Company website |
| location | string | | HQ location |
| size | string | | Employee count range |
| status | enum | | active, dormant, archived |

## Event Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | ✓ | Event name |
| type | string | ✓ | Always "event" |
| tags | list | | Categorization tags |
| date | date | ✓ | Event start date (YYYY-MM-DD) |
| end_date | date | | Event end date |
| location | string | | Event location |
| website | string | | Event website |

## Common Tags

### People
- `investor`, `vc`, `angel`
- `founder`, `ceo`, `cto`
- `client`, `prospect`, `lead`
- `friend`, `colleague`, `mentor`
- `partner`, `advisor`
- `developer`, `designer`, `marketing`

### Industries
- `crypto`, `web3`, `defi`
- `ai`, `ml`, `saas`
- `fintech`, `healthtech`
- `enterprise`, `startup`

### Locations
- Use city names: `singapore`, `san-francisco`, `london`
- Or regions: `asia`, `europe`, `us`

## Status Definitions

| Status | Meaning |
|--------|---------|
| active | Regular contact, engaged relationship |
| dormant | No contact in 90+ days, needs re-engagement |
| archived | Relationship ended, historical record only |

## Date Formats

All dates use ISO format: `YYYY-MM-DD`

Examples:
- `2026-01-27`
- `2025-12-31`

## File Naming

Files are named with slugified names:
- "Alice Chen" → `alice-chen.md`
- "Token2049 Singapore" → `token2049-singapore.md`
- "Acme Corp Inc." → `acme-corp-inc.md`

Slugification rules:
1. Lowercase
2. Replace non-alphanumeric with hyphens
3. Remove leading/trailing hyphens
4. Collapse multiple hyphens
