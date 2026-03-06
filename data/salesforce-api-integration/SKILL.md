---
name: Salesforce API Integration
slug: salesforce-api-integration
version: 1.0.1
homepage: https://clawic.com/skills/salesforce-api-integration
description: Complete Salesforce REST API for SOQL queries, CRUD operations, Bulk API, Composite API, authentication, and standard objects with error handling.
changelog: Fixed memory template to use standard status values and natural language context.
metadata: {"clawdbot":{"emoji":"☁️","requires":{"env":["SF_ACCESS_TOKEN","SF_INSTANCE_URL"],"config":["~/salesforce-api-integration/"]},"primaryEnv":"SF_ACCESS_TOKEN","os":["linux","darwin","win32"]}}
---

# Salesforce API Integration

Complete Salesforce REST API reference. See auxiliary files for detailed operations.

## Quick Start

```bash
curl "$SF_INSTANCE_URL/services/data/v59.0/sobjects/" \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN"
```

## Setup

On first use, read `setup.md`. Preferences stored in `~/salesforce-api-integration/memory.md`.

## When to Use

Any Salesforce operation: SOQL queries, record CRUD, bulk imports/exports, metadata, composite requests.

## Architecture

```
~/salesforce-api-integration/
├── memory.md      # Org context and object schemas
└── queries.md     # Saved SOQL queries
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup and authentication | `setup.md`, `memory-template.md` |
| SOQL queries and search | `soql.md` |
| Records: create, read, update, delete | `records.md` |
| Standard objects reference | `objects.md` |
| Bulk API 2.0 for large datasets | `bulk.md` |
| Composite and batch requests | `composite.md` |
| Metadata and schema | `metadata.md` |
| Error handling | `errors.md` |

## Core Rules

1. **Bearer token auth** - `Authorization: Bearer $SF_ACCESS_TOKEN`
2. **Instance URL required** - Each org has unique URL like `https://yourorg.my.salesforce.com`
3. **API version in path** - Use `/services/data/v59.0/` (or newer)
4. **SOQL for queries** - Salesforce Object Query Language for data retrieval
5. **Object API names** - Use API names: `Account`, `Contact__c` (custom objects end in `__c`)
6. **Pagination for large results** - Use `nextRecordsUrl` for results over 2000
7. **Rate limits** - Vary by edition, typically 100k+ calls/day

## Authentication

**Required environment variables:**
- `SF_ACCESS_TOKEN` - OAuth access token for API calls
- `SF_INSTANCE_URL` - Your Salesforce instance (e.g., `https://yourorg.my.salesforce.com`)

```bash
# All requests require these headers
curl "$SF_INSTANCE_URL/services/data/v59.0/..." \
  -H "Authorization: Bearer $SF_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

## Common Traps

- Wrong instance URL - 404 or DNS errors
- Expired access token - 401 INVALID_SESSION_ID
- Missing field permissions - Field appears null
- SOQL syntax errors - MALFORMED_QUERY
- Relationship name vs field name - Use `Account.Name` not `AccountId.Name`

## External Endpoints

| Endpoint | Purpose |
|----------|---------|
| `https://*.my.salesforce.com/services/data/*` | REST API |
| `https://*.my.salesforce.com/services/async/*` | Bulk API |
| `https://login.salesforce.com/services/oauth2/*` | OAuth (production) |
| `https://test.salesforce.com/services/oauth2/*` | OAuth (sandbox) |

## Security & Privacy

**Environment variables used:**
- `SF_ACCESS_TOKEN` - for API authentication
- `SF_INSTANCE_URL` - for API endpoint routing

**Sent to Salesforce:** Queries, record data via your instance URL
**Stays local:** Access token (in environment variable only), ~/salesforce-api-integration/ preferences
**Never:** Store tokens in files, log sensitive data, bypass field-level security

## Scope

This skill ONLY:
- Makes requests to Salesforce REST API endpoints
- Stores preferences in `~/salesforce-api-integration/`
- Provides curl and code examples

This skill NEVER:
- Accesses files outside `~/salesforce-api-integration/`
- Makes requests to non-Salesforce endpoints
- Stores access tokens in files

## Trust

By using this skill, data is sent to Salesforce (salesforce.com).
Only install if you trust Salesforce with your CRM data.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `api` — REST API patterns
- `crm` — CRM workflows
- `accounting` — Financial operations

## Feedback

- If useful: `clawhub star salesforce-api-integration`
- Stay updated: `clawhub sync`
