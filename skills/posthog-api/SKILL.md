---
name: posthog
description: |
  PostHog API integration with managed authentication. Product analytics, feature flags, session recordings, experiments, and more.
  Use this skill when users want to query analytics events, manage feature flags, analyze user behavior, view session recordings, or run A/B experiments.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🦔
    homepage: "https://maton.ai"
    requires:
      env:
        - MATON_API_KEY
---

# PostHog

Access the PostHog API with managed authentication. Query product analytics events with HogQL, manage feature flags, analyze user behavior, view session recordings, and run A/B experiments.

## Quick Start

```bash
# List projects
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/posthog/api/projects/')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/posthog/{native-api-path}
```

Replace `{native-api-path}` with the actual PostHog API endpoint path. The gateway proxies requests to `{subdomain}.posthog.com` and automatically injects your credentials.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your PostHog OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=posthog&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'posthog'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "ce2b0840-4e39-4b58-b607-7290fa7a3595",
    "status": "ACTIVE",
    "creation_time": "2026-02-23T09:37:57.686121Z",
    "last_updated_time": "2026-02-23T09:39:11.851118Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "posthog",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple PostHog connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/posthog/api/projects/')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', 'ce2b0840-4e39-4b58-b607-7290fa7a3595')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Organizations

#### Get Current Organization

```bash
GET /posthog/api/organizations/@current/
```

### Projects

#### List Projects

```bash
GET /posthog/api/projects/
```

**Response:**
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 136209,
      "uuid": "019583c6-377c-0000-e55c-8696cbc33595",
      "organization": "019583c6-3635-0000-5798-c18f20963b3b",
      "api_token": "phc_XXX",
      "name": "Default project",
      "timezone": "UTC"
    }
  ]
}
```

#### Get Current Project

```bash
GET /posthog/api/projects/@current/
```

### Users

#### Get Current User

```bash
GET /posthog/api/users/@me/
```

### Query (HogQL)

The query endpoint is the recommended way to retrieve events and run analytics queries.

#### Run HogQL Query

```bash
POST /posthog/api/projects/{project_id}/query/
Content-Type: application/json

{
  "query": {
    "kind": "HogQLQuery",
    "query": "SELECT event, count() FROM events GROUP BY event ORDER BY count() DESC LIMIT 10"
  }
}
```

**Response:**
```json
{
  "columns": ["event", "count()"],
  "results": [
    ["$pageview", 140504],
    ["$autocapture", 108691],
    ["$identify", 5455]
  ],
  "types": [
    ["event", "String"],
    ["count()", "UInt64"]
  ]
}
```

### Persons

#### List Persons

```bash
GET /posthog/api/projects/{project_id}/persons/?limit=10
```

**Response:**
```json
{
  "results": [
    {
      "id": "5d79eecb-93e6-5c8b-90f9-8510ba4040b8",
      "uuid": "5d79eecb-93e6-5c8b-90f9-8510ba4040b8",
      "name": "user@example.com",
      "is_identified": true,
      "distinct_ids": ["user-uuid", "anon-uuid"],
      "properties": {
        "email": "user@example.com",
        "name": "John Doe"
      }
    }
  ],
  "next": "https://us.posthog.com/api/projects/{project_id}/persons/?limit=10&offset=10"
}
```

#### Get Person

```bash
GET /posthog/api/projects/{project_id}/persons/{person_uuid}/
```

### Dashboards

#### List Dashboards

```bash
GET /posthog/api/projects/{project_id}/dashboards/
```

#### Get Dashboard

```bash
GET /posthog/api/projects/{project_id}/dashboards/{dashboard_id}/
```

#### Create Dashboard

```bash
POST /posthog/api/projects/{project_id}/dashboards/
Content-Type: application/json

{
  "name": "My Dashboard",
  "description": "Analytics overview"
}
```

#### Update Dashboard

```bash
PATCH /posthog/api/projects/{project_id}/dashboards/{dashboard_id}/
Content-Type: application/json

{
  "name": "Updated Dashboard Name"
}
```

### Insights

#### List Insights

```bash
GET /posthog/api/projects/{project_id}/insights/?limit=10
```

#### Get Insight

```bash
GET /posthog/api/projects/{project_id}/insights/{insight_id}/
```

#### Create Insight

```bash
POST /posthog/api/projects/{project_id}/insights/
Content-Type: application/json

{
  "name": "Daily Active Users",
  "query": {
    "kind": "InsightVizNode",
    "source": {
      "kind": "TrendsQuery",
      "series": [{"kind": "EventsNode", "event": "$pageview", "math": "dau"}],
      "interval": "day",
      "dateRange": {"date_from": "-30d"}
    }
  }
}
```

### Feature Flags

#### List Feature Flags

```bash
GET /posthog/api/projects/{project_id}/feature_flags/
```

#### Get Feature Flag

```bash
GET /posthog/api/projects/{project_id}/feature_flags/{flag_id}/
```

#### Create Feature Flag

```bash
POST /posthog/api/projects/{project_id}/feature_flags/
Content-Type: application/json

{
  "key": "my-feature-flag",
  "name": "My Feature Flag",
  "active": true,
  "filters": {
    "groups": [{"rollout_percentage": 100}]
  }
}
```

#### Update Feature Flag

```bash
PATCH /posthog/api/projects/{project_id}/feature_flags/{flag_id}/
Content-Type: application/json

{
  "active": false
}
```

#### Delete Feature Flag

Use soft delete by setting `deleted: true`:

```bash
PATCH /posthog/api/projects/{project_id}/feature_flags/{flag_id}/
Content-Type: application/json

{
  "deleted": true
}
```

### Cohorts

#### List Cohorts

```bash
GET /posthog/api/projects/{project_id}/cohorts/
```

#### Get Cohort

```bash
GET /posthog/api/projects/{project_id}/cohorts/{cohort_id}/
```

#### Create Cohort

```bash
POST /posthog/api/projects/{project_id}/cohorts/
Content-Type: application/json

{
  "name": "Active Users",
  "groups": [
    {
      "properties": [
        {"key": "$pageview", "type": "event", "value": "performed_event"}
      ]
    }
  ]
}
```

### Actions

#### List Actions

```bash
GET /posthog/api/projects/{project_id}/actions/
```

#### Create Action

```bash
POST /posthog/api/projects/{project_id}/actions/
Content-Type: application/json

{
  "name": "Signed Up",
  "steps": [{"event": "$identify"}]
}
```

### Session Recordings

#### List Session Recordings

```bash
GET /posthog/api/projects/{project_id}/session_recordings/?limit=10
```

**Response:**
```json
{
  "results": [
    {
      "id": "019c8795-79e3-7a05-ac56-597b102f1960",
      "distinct_id": "user-uuid",
      "recording_duration": 1807,
      "start_time": "2026-02-22T23:00:46.389000Z",
      "end_time": "2026-02-22T23:30:53.297000Z",
      "click_count": 0,
      "keypress_count": 0,
      "start_url": "https://example.com/register"
    }
  ],
  "has_next": false
}
```

#### Get Session Recording

```bash
GET /posthog/api/projects/{project_id}/session_recordings/{recording_id}/
```

### Annotations

#### List Annotations

```bash
GET /posthog/api/projects/{project_id}/annotations/
```

#### Create Annotation

```bash
POST /posthog/api/projects/{project_id}/annotations/
Content-Type: application/json

{
  "content": "New feature launched",
  "date_marker": "2026-02-23T00:00:00Z",
  "scope": "project"
}
```

### Surveys

#### List Surveys

```bash
GET /posthog/api/projects/{project_id}/surveys/
```

#### Create Survey

```bash
POST /posthog/api/projects/{project_id}/surveys/
Content-Type: application/json

{
  "name": "NPS Survey",
  "type": "popover",
  "questions": [
    {
      "type": "rating",
      "question": "How likely are you to recommend us?"
    }
  ]
}
```

### Experiments

#### List Experiments

```bash
GET /posthog/api/projects/{project_id}/experiments/
```

#### Create Experiment

```bash
POST /posthog/api/projects/{project_id}/experiments/
Content-Type: application/json

{
  "name": "Button Color Test",
  "feature_flag_key": "button-color-test"
}
```

### Event Definitions

#### List Event Definitions

```bash
GET /posthog/api/projects/{project_id}/event_definitions/?limit=10
```

### Property Definitions

#### List Property Definitions

```bash
GET /posthog/api/projects/{project_id}/property_definitions/?limit=10
```

## Pagination

PostHog uses offset-based pagination:

```bash
GET /posthog/api/projects/{project_id}/persons/?limit=10&offset=20
```

Response includes pagination info:

```json
{
  "count": 100,
  "next": "https://us.posthog.com/api/projects/{project_id}/persons/?limit=10&offset=30",
  "previous": "https://us.posthog.com/api/projects/{project_id}/persons/?limit=10&offset=10",
  "results": [...]
}
```

For session recordings, use `has_next` boolean:

```json
{
  "results": [...],
  "has_next": true
}
```

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/posthog/api/projects/',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/posthog/api/projects/',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
```

### Python - HogQL Query

```python
import os
import requests

response = requests.post(
    'https://gateway.maton.ai/posthog/api/projects/@current/query/',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={
        'query': {
            'kind': 'HogQLQuery',
            'query': 'SELECT event, count() FROM events GROUP BY event LIMIT 10'
        }
    }
)
data = response.json()
```

## Notes

- Use `@current` as a shortcut for the current project ID (e.g., `/api/projects/@current/dashboards/`)
- Project IDs are integers (e.g., `136209`)
- Person UUIDs are in standard UUID format
- The Events endpoint is deprecated; use the Query endpoint with HogQL instead
- Session recordings include activity metrics like click_count, keypress_count
- PostHog uses soft delete: use `PATCH` with `{"deleted": true}` instead of HTTP DELETE
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments. Use Python examples instead.

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing PostHog connection |
| 401 | Invalid or missing Maton API key |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from PostHog API |

### Rate Limits

- Analytics endpoints (insights, persons, recordings): 240/minute, 1200/hour
- HogQL query endpoint: 120/hour
- CRUD endpoints: 480/minute, 4800/hour

## Resources

- [PostHog API Overview](https://posthog.com/docs/api)
- [HogQL Documentation](https://posthog.com/docs/hogql)
- [Feature Flags](https://posthog.com/docs/feature-flags)
- [Session Replay](https://posthog.com/docs/session-replay)
- [Experiments](https://posthog.com/docs/experiments)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
