# PostHog API — Endpoint Reference

## Table of Contents

- [Domains & Authentication](#domains--authentication)
- [Public Endpoints (Project API Key)](#public-endpoints-project-api-key)
- [Private Endpoints (Personal API Key)](#private-endpoints-personal-api-key)
- [Query API (HogQL)](#query-api-hogql)
- [Rate Limits](#rate-limits)
- [Pagination](#pagination)

---

## Domains & Authentication

| Cloud | Public endpoints | Private endpoints |
|-------|-----------------|-------------------|
| US | `https://us.i.posthog.com` | `https://us.posthog.com` |
| EU | `https://eu.i.posthog.com` | `https://eu.posthog.com` |
| Self-hosted | Your domain | Your domain |

### Public endpoints (no auth needed)
Use project API key in request body as `api_key`.

### Private endpoints
Use personal API key via `Authorization: Bearer <key>` header.

---

## Public Endpoints (Project API Key)

These are POST-only, no rate limits, no sensitive data returned.

### Capture — `/i/v0/e/`

Single event capture:
```json
{
  "api_key": "<project_api_key>",
  "event": "event_name",
  "distinct_id": "user_123",
  "properties": {"plan": "pro"},
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Special event types (same endpoint, different `event` field):
- `$identify` — Set person properties via `$set` / `$set_once`
- `$create_alias` — Merge distinct IDs (property: `alias`)
- `$groupidentify` — Create/update group (properties: `$group_type`, `$group_key`, `$group_set`)
- `$pageview` — Page view (properties: `$current_url`, `$session_id`)
- `$screen` — Mobile screen view (property: `$screen_name`)
- `survey sent` / `survey shown` / `survey dismissed` — Survey events (property: `$survey_id`)

Anonymous events: Set `"$process_person_profile": false` in properties.

### Batch — `/batch/`

Multiple events in one request (body < 20MB):
```json
{
  "api_key": "<project_api_key>",
  "historical_migration": false,
  "batch": [
    {"event": "evt1", "properties": {"distinct_id": "u1"}, "timestamp": "..."},
    {"event": "evt2", "properties": {"distinct_id": "u1"}}
  ]
}
```

Set `historical_migration: true` for data migrations.

### Feature Flags — `/flags?v=2`

Evaluate flags for a user:
```json
{
  "api_key": "<project_api_key>",
  "distinct_id": "user_123",
  "groups": {"company": "acme_inc"}
}
```

Add `&config=true` for PostHog config alongside flags.

Response includes `flags` object with `enabled`, `variant`, `reason`, `metadata` per flag.

---

## Private Endpoints (Personal API Key)

Base path: `/api/projects/:project_id/` (or `/api/environments/:project_id/` for some)

### Persons

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/api/environments/:project_id/persons/` | person:read | List persons (query: `distinct_id`, `email`, `search`, `properties`, `limit`, `offset`) |
| GET | `/api/environments/:project_id/persons/:id/` | person:read | Get person |
| PATCH | `/api/environments/:project_id/persons/:id/` | person:write | Update person properties |
| POST | `/api/environments/:project_id/persons/:id/delete_property/` | person:write | Delete property |
| POST | `/api/environments/:project_id/persons/:id/split/` | person:write | Split person |
| POST | `/api/environments/:project_id/persons/bulk_delete/` | person:write | Bulk delete persons |
| POST | `/api/environments/:project_id/persons/batch_by_distinct_ids/` | person:read | Batch lookup by distinct IDs |
| GET | `/api/environments/:project_id/persons/cohorts/` | person:read | List person cohorts |

### Feature Flags

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/api/projects/:project_id/feature_flags/` | feature_flag:read | List flags (query: `active`, `type`, `search`, `tags`) |
| POST | `/api/projects/:project_id/feature_flags/` | feature_flag:write | Create flag (body: `key`, `name`, `filters`, `active`) |
| GET | `/api/projects/:project_id/feature_flags/:id/` | feature_flag:read | Get flag |
| PATCH | `/api/projects/:project_id/feature_flags/:id/` | feature_flag:write | Update flag |
| DELETE | `/api/projects/:project_id/feature_flags/:id/` | feature_flag:write | Delete flag |

### Insights

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/api/projects/:project_id/insights/` | insight:read | List insights |
| POST | `/api/projects/:project_id/insights/` | insight:write | Create insight (body: `name`, `query`, `dashboards`) |
| GET | `/api/projects/:project_id/insights/:id/` | insight:read | Get insight |
| PATCH | `/api/projects/:project_id/insights/:id/` | insight:write | Update insight |
| DELETE | `/api/projects/:project_id/insights/:id/` | insight:write | Delete insight |

### Dashboards

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/api/projects/:project_id/dashboards/` | dashboard:read | List dashboards |
| POST | `/api/projects/:project_id/dashboards/` | dashboard:write | Create dashboard |
| GET | `/api/projects/:project_id/dashboards/:id/` | dashboard:read | Get dashboard |
| PATCH | `/api/projects/:project_id/dashboards/:id/` | dashboard:write | Update dashboard |
| DELETE | `/api/projects/:project_id/dashboards/:id/` | dashboard:write | Delete dashboard |

### Annotations

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/api/projects/:project_id/annotations/` | annotation:read | List annotations |
| POST | `/api/projects/:project_id/annotations/` | annotation:write | Create annotation (body: `content`, `date_marker`, `scope`) |
| GET | `/api/projects/:project_id/annotations/:id/` | annotation:read | Get annotation |
| PATCH | `/api/projects/:project_id/annotations/:id/` | annotation:write | Update annotation |

### Cohorts

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/api/projects/:project_id/cohorts/` | cohort:read | List cohorts |
| POST | `/api/projects/:project_id/cohorts/` | cohort:write | Create cohort |
| GET | `/api/projects/:project_id/cohorts/:id/` | cohort:read | Get cohort |
| PATCH | `/api/projects/:project_id/cohorts/:id/` | cohort:write | Update cohort |

### Experiments

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/api/projects/:project_id/experiments/` | experiment:read | List experiments |
| POST | `/api/projects/:project_id/experiments/` | experiment:write | Create experiment |
| GET | `/api/projects/:project_id/experiments/:id/` | experiment:read | Get experiment |
| PATCH | `/api/projects/:project_id/experiments/:id/` | experiment:write | Update experiment |
| DELETE | `/api/projects/:project_id/experiments/:id/` | experiment:write | Delete experiment |

### Surveys

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/api/projects/:project_id/surveys/` | survey:read | List surveys |
| POST | `/api/projects/:project_id/surveys/` | survey:write | Create survey |
| GET | `/api/projects/:project_id/surveys/:id/` | survey:read | Get survey |
| PATCH | `/api/projects/:project_id/surveys/:id/` | survey:write | Update survey |
| DELETE | `/api/projects/:project_id/surveys/:id/` | survey:write | Delete survey |

### Actions

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/api/projects/:project_id/actions/` | action:read | List actions |
| POST | `/api/projects/:project_id/actions/` | action:write | Create action |
| GET | `/api/projects/:project_id/actions/:id/` | action:read | Get action |
| PATCH | `/api/projects/:project_id/actions/:id/` | action:write | Update action |
| DELETE | `/api/projects/:project_id/actions/:id/` | action:write | Delete action |

### Session Recordings

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/api/projects/:project_id/session_recordings/` | session_recording:read | List recordings |
| GET | `/api/projects/:project_id/session_recordings/:id/` | session_recording:read | Get recording |
| DELETE | `/api/projects/:project_id/session_recordings/:id/` | session_recording:write | Delete recording |

### Users

| Method | Path | Scope | Description |
|--------|------|-------|-------------|
| GET | `/api/users/` | user:read | List users |
| GET | `/api/users/:uuid/` | user:read | Get user |
| GET | `/api/users/@me/` | — | Get current user info |

### Event/Property Definitions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/projects/:project_id/event_definitions/` | List event definitions |
| GET | `/api/projects/:project_id/property_definitions/` | List property definitions |

---

## Query API (HogQL)

**Endpoint**: `POST /api/projects/:project_id/query/`

The most powerful way to query PostHog data. Uses HogQL (SQL-like).

```json
{
  "query": {
    "kind": "HogQLQuery",
    "query": "SELECT event, count() FROM events WHERE timestamp >= now() - INTERVAL 7 DAY GROUP BY event ORDER BY count() DESC LIMIT 100"
  },
  "name": "top_events_last_7_days"
}
```

### Available tables
- `events` — All captured events
- `persons` — All persons
- `sessions` — Session data
- `groups` — Group analytics data
- Data warehouse tables and materialized views

### Query kinds
- `HogQLQuery` — Raw SQL queries (most common)
- `EventsQuery` — Structured event queries
- `PersonsQuery` — Structured person queries

### Best practices
1. Always include time ranges (`WHERE timestamp >= now() - INTERVAL 7 DAY`)
2. Use `LIMIT` (default 100, max 50k)
3. Use timestamp-based pagination, not OFFSET
4. Name queries for debugging via `query_log`
5. Use materialized views for repeated heavy queries
6. Don't scan same table multiple times — use materialized views

### Async queries
For long-running queries, add `"async": true`. Response includes `query_status` with `id` to poll.

---

## Rate Limits

Private endpoints only (personal API key). Public endpoints are not rate limited.

| Endpoint type | Limit |
|---------------|-------|
| Analytics (insights, persons, recordings) | 240/min, 1200/hr |
| Query endpoint | 2400/hr |
| Feature flag local evaluation | 600/min |
| All other CRUD | 480/min, 4800/hr |

Limits apply per organization (all users combined).

---

## Pagination

List endpoints return:
```json
{
  "count": 400,
  "next": "https://us.posthog.com/api/projects/.../endpoint/?offset=200&limit=100",
  "previous": "...",
  "results": [...]
}
```

Follow the `next` URL for subsequent pages. Default limit: 100.

For HogQL queries: use timestamp-based pagination (not OFFSET).

---

## OpenAPI Spec

Available when logged in:
- Download: `https://app.posthog.com/api/schema/`
- Swagger UI: `https://app.posthog.com/api/schema/swagger-ui/`
- Redoc: `https://app.posthog.com/api/schema/redoc/`
