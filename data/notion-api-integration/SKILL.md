---
name: Notion API Integration
slug: notion-api-integration
version: 1.0.2
homepage: https://clawic.com/skills/notion-api-integration
description: Complete Notion API for databases, pages, blocks, users, search, comments, and property types with pagination and error handling.
changelog: Fixed memory template to use standard status values and natural language context.
metadata: {"clawdbot":{"emoji":"N","requires":{"env":["NOTION_API_KEY"],"config":["~/notion-api-integration/"]},"primaryEnv":"NOTION_API_KEY","os":["linux","darwin","win32"]}}
---

# Notion API Integration

Complete Notion API reference. See auxiliary files for detailed operations.

## Quick Start

```bash
curl 'https://api.notion.com/v1/users/me' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28"
```

## Setup

On first use, read `setup.md`. Preferences stored in `~/notion-api-integration/memory.md`.

## When to Use

Any Notion operation: databases, pages, blocks, users, search, comments, properties.

## Architecture

```
~/notion-api-integration/
├── memory.md      # Workspace context
└── databases.md   # Tracked database IDs
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup and memory | `setup.md`, `memory-template.md` |
| Databases: query, create, update | `databases.md` |
| Pages: CRUD, properties | `pages.md` |
| Blocks: content, children | `blocks.md` |
| Property types reference | `properties.md` |
| Filters and sorts | `filters.md` |
| Search and users | `search.md` |
| Pagination patterns | `pagination.md` |
| Error handling | `errors.md` |

## Core Rules

1. **API version header required** - Always include `Notion-Version: 2022-06-28` (or newer)
2. **Bearer token auth** - `Authorization: Bearer $NOTION_API_KEY`
3. **Page IDs without dashes** - Remove dashes from URLs: `abc123def456` not `abc-123-def-456`
4. **Property names are case-sensitive** - Match exactly as defined in database
5. **Pagination mandatory** - Use `start_cursor` for results over 100 items
6. **Rate limits** - 3 requests/second average, burst allowed
7. **Integration access** - Pages must be shared with integration to access

## Authentication

**Required environment variable:**
- `NOTION_API_KEY` - Internal integration token (starts with `ntn_` or `secret_`)

```bash
# All requests require these headers
curl 'https://api.notion.com/v1/...' \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json"
```

## Common Traps

- Missing `Notion-Version` header - 400 error
- Page ID with dashes - 404 not found
- Property name mismatch - Silent failure or error
- Skipping pagination - Miss data beyond first 100
- No integration access - 404 even if page exists

## External Endpoints

| Endpoint | Purpose |
|----------|---------|
| `https://api.notion.com/v1/*` | All Notion API operations |

No other endpoints are accessed.

## Security & Privacy

**Environment variable used:**
- `NOTION_API_KEY` - for API authentication

**Sent to Notion:** Database queries, page content, block updates via api.notion.com
**Stays local:** API key (in environment variable only), ~/notion-api-integration/ preferences
**Never:** Store API keys in files, access pages not shared with integration

## Scope

This skill ONLY:
- Makes requests to api.notion.com endpoints
- Stores preferences in `~/notion-api-integration/`
- Provides curl and code examples

This skill NEVER:
- Accesses files outside `~/notion-api-integration/`
- Makes requests to other endpoints
- Stores API keys in files

## Trust

By using this skill, data is sent to Notion (notion.com).
Only install if you trust Notion with your workspace data.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `api` — REST API patterns
- `pkm` — Personal knowledge management
- `productivity` — Task and productivity workflows

## Feedback

- If useful: `clawhub star notion-api-integration`
- Stay updated: `clawhub sync`
