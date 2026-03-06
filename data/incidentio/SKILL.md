---
name: incidentio
description: Manage incidents via the incident.io REST API. Create, view, update, escalate, and resolve incidents. Check severities, statuses, and post incident updates. Requires INCIDENTIO_API_KEY environment variable.
metadata:
  openclaw:
    emoji: "🚨"
    requires:
      bins: [curl, jq]
      env: [INCIDENTIO_API_KEY]
    primaryEnv: INCIDENTIO_API_KEY
    homepage: https://api-docs.incident.io/
---

# Incident.io

Manage incidents, severities, statuses, and post updates via the incident.io REST API.

## Setup

1. Create an API key at **Settings > API keys** in the incident.io dashboard
2. Ensure the key has scopes for managing incidents and viewing organization data
3. Set the environment variable:
   ```bash
   export INCIDENTIO_API_KEY="your-api-key"
   ```

## API Basics

Base URL: `https://api.incident.io`

**Important:** The API has a v1/v2 split:
- **v2** — Incidents, incident updates
- **v1** — Severities, incident statuses, incident types

All requests use this auth pattern:

```bash
curl -s "https://api.incident.io/v2/..." \
  -H "Authorization: Bearer $INCIDENTIO_API_KEY" \
  -H "Content-Type: application/json"
```

Rate limit: 1200 requests/minute per API key.

Pagination: Use `page_size` (max 250) and the `after` cursor from `pagination_meta.after` in responses.

## List Severities

Severities are organization-specific. Always fetch them before creating an incident to get valid IDs.

```bash
curl -s "https://api.incident.io/v1/severities" \
  -H "Authorization: Bearer $INCIDENTIO_API_KEY" | jq '.severities[] | {id, name, rank}'
```

## List Incident Statuses

```bash
curl -s "https://api.incident.io/v1/incident_statuses" \
  -H "Authorization: Bearer $INCIDENTIO_API_KEY" | jq '.incident_statuses[] | {id, name, category}'
```

Status categories: `triage`, `live`, `learning`, `closed`, `declined`, `merged`, `canceled`.

## List Incident Types

```bash
curl -s "https://api.incident.io/v1/incident_types" \
  -H "Authorization: Bearer $INCIDENTIO_API_KEY" | jq '.incident_types[] | {id, name, is_default}'
```

## Create an Incident

Required fields: `idempotency_key`, `visibility`. A `severity_id` is needed to open an active incident.

```bash
curl -s -X POST "https://api.incident.io/v2/incidents" \
  -H "Authorization: Bearer $INCIDENTIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "idempotency_key": "unique-key-123",
    "name": "Database connection pool exhaustion",
    "summary": "Primary DB connection pool at 100% causing request failures",
    "severity_id": "SEVERITY_ID",
    "visibility": "public",
    "mode": "standard"
  }' | jq '.incident | {id, reference, name, permalink}'
```

Optional fields:
- `incident_type_id` — set a specific incident type
- `incident_status_id` — override the default starting status
- `mode` — `standard` (default), `retrospective` (no Slack announcement), or `test` (no alerts)
- `visibility` — `public` or `private`
- `custom_field_entries` — array of `{custom_field_id, values: [{value_link}]}`
- `incident_role_assignments` — array of `{incident_role_id, user: {id}}`
- `incident_timestamp_values` — array of `{incident_timestamp_id, value}`

Always generate a unique `idempotency_key` per incident (e.g. a UUID or descriptive slug).

## Get an Incident

```bash
curl -s "https://api.incident.io/v2/incidents/INCIDENT_ID" \
  -H "Authorization: Bearer $INCIDENTIO_API_KEY" \
  | jq '.incident | {id, reference, name, summary, status: .incident_status.name, severity: .severity.name, created_at, permalink}'
```

## List Incidents

```bash
curl -s "https://api.incident.io/v2/incidents?page_size=25" \
  -H "Authorization: Bearer $INCIDENTIO_API_KEY" \
  | jq '.incidents[] | {id, reference, name, status: .incident_status.name, severity: .severity.name}'
```

Filter parameters (query string):
- `status_category[one_of]=live` — filter by category (`triage`, `live`, `learning`, `closed`, `declined`, `merged`, `canceled`)
- `status[one_of]=STATUS_ID` — filter by exact status ID (repeatable)
- `severity[one_of]=SEVERITY_ID` — filter by severity (repeatable)
- `severity[gte]=SEVERITY_ID` / `severity[lte]=SEVERITY_ID` — filter by severity rank
- `created_at[gte]=2024-01-01` / `created_at[lte]=2024-12-31` — date range
- `mode[one_of]=standard` — filter by mode
- `page_size=N` (max 250) and `after=CURSOR` for pagination

## Edit an Incident

Only provided fields are updated; omitted fields remain unchanged.

```bash
curl -s -X POST "https://api.incident.io/v2/incidents/INCIDENT_ID/actions/edit" \
  -H "Authorization: Bearer $INCIDENTIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "incident": {
      "summary": "Root cause identified: memory leak in connection pooler",
      "severity_id": "NEW_SEVERITY_ID"
    },
    "notify_incident_channel": true
  }' | jq '.incident | {id, reference, name, severity: .severity.name}'
```

Editable fields inside `incident`:
- `name`, `summary`, `severity_id`, `incident_status_id`
- `call_url`, `slack_channel_name_override`
- `custom_field_entries`, `incident_role_assignments`, `incident_timestamp_values`

Set `notify_incident_channel: true` to alert responders of the change.

## Close an Incident

Closing is done by setting `incident_status_id` to a status with category `closed`. First, find the closed status ID:

```bash
curl -s "https://api.incident.io/v1/incident_statuses" \
  -H "Authorization: Bearer $INCIDENTIO_API_KEY" \
  | jq '.incident_statuses[] | select(.category == "closed") | {id, name}'
```

Then update the incident:

```bash
curl -s -X POST "https://api.incident.io/v2/incidents/INCIDENT_ID/actions/edit" \
  -H "Authorization: Bearer $INCIDENTIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "incident": {
      "incident_status_id": "CLOSED_STATUS_ID"
    },
    "notify_incident_channel": true
  }' | jq '.incident | {id, reference, name, status: .incident_status.name}'
```

## Post an Incident Update

```bash
curl -s -X POST "https://api.incident.io/v2/incident_updates" \
  -H "Authorization: Bearer $INCIDENTIO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "INCIDENT_ID",
    "message": "Rolling restart in progress. Monitoring connection pool metrics."
  }' | jq '.incident_update | {id, message, created_at}'
```

## List Incident Updates

```bash
curl -s "https://api.incident.io/v2/incident_updates?incident_id=INCIDENT_ID&page_size=25" \
  -H "Authorization: Bearer $INCIDENTIO_API_KEY" \
  | jq '.incident_updates[] | {id, message, created_at}'
```

## Common Workflows

### Declare and manage an incident end-to-end

1. **Fetch severities** — `GET /v1/severities` to get valid severity IDs
2. **Create incident** — `POST /v2/incidents` with name, severity, visibility
3. **Post updates** — `POST /v2/incident_updates` as investigation progresses
4. **Escalate if needed** — Edit the incident to raise severity via `POST /v2/incidents/{id}/actions/edit`
5. **Resolve** — Edit the incident status to a `closed`-category status

### Triage active incidents

1. **List live incidents** — `GET /v2/incidents?status_category[one_of]=live`
2. **Get details** — `GET /v2/incidents/{id}` for each incident
3. **Check updates** — `GET /v2/incident_updates?incident_id={id}` for latest status

## Notes

- IDs are ULIDs (e.g. `01FCNDV6P870EA6S7TK1DSYDG0`)
- Severities, statuses, and types are organization-specific — always query them dynamically rather than hardcoding
- The `idempotency_key` on create prevents duplicate incidents; use a unique value per request
- `mode: "test"` creates test incidents that do not alert responders
- The edit endpoint wraps fields inside an `incident` object, unlike the create endpoint
- Rate limit: 1200 req/min per API key
- Pagination: use the `after` cursor from `pagination_meta.after` in responses
