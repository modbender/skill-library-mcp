---
name: sentry
description: |
  Sentry API integration with managed authentication. Monitor errors, issues, and application performance.
  Use this skill when users want to list issues, retrieve events, manage projects, teams, or releases in Sentry.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    homepage: "https://maton.ai"
    requires:
      env:
        - MATON_API_KEY
---

# Sentry

Access the Sentry API with managed authentication. Monitor errors, manage issues, projects, teams, and releases.

## Quick Start

```bash
# List issues for a project
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/sentry/api/0/projects/{organization_slug}/{project_slug}/issues/')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/sentry/{native-api-path}
```

Replace `{native-api-path}` with the actual Sentry API endpoint path. The gateway proxies requests to `{subdomain}.sentry.io` and automatically injects your credentials.

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

Manage your Sentry OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=sentry&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'sentry'}).encode()
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
    "connection_id": "21fd90f9-5935-43cd-b6c8-bde9d915ca80",
    "status": "ACTIVE",
    "creation_time": "2025-12-08T07:20:53.488460Z",
    "last_updated_time": "2026-01-31T20:03:32.593153Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "sentry",
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

If you have multiple Sentry connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/sentry/api/0/organizations/')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Organization Operations

#### List Organizations

```bash
GET /sentry/api/0/organizations/
```

#### Retrieve an Organization

```bash
GET /sentry/api/0/organizations/{organization_slug}/
```

#### Update an Organization

```bash
PUT /sentry/api/0/organizations/{organization_slug}/
Content-Type: application/json

{
  "name": "Updated Organization Name"
}
```

#### List Organization Projects

```bash
GET /sentry/api/0/organizations/{organization_slug}/projects/
```

#### List Organization Members

```bash
GET /sentry/api/0/organizations/{organization_slug}/members/
```

### Project Operations

#### Retrieve a Project

```bash
GET /sentry/api/0/projects/{organization_slug}/{project_slug}/
```

#### Update a Project

```bash
PUT /sentry/api/0/projects/{organization_slug}/{project_slug}/
Content-Type: application/json

{
  "name": "Updated Project Name",
  "slug": "updated-project-slug"
}
```

#### Delete a Project

```bash
DELETE /sentry/api/0/projects/{organization_slug}/{project_slug}/
```

#### Create a New Project

```bash
POST /sentry/api/0/teams/{organization_slug}/{team_slug}/projects/
Content-Type: application/json

{
  "name": "New Project",
  "slug": "new-project"
}
```

### Issue Operations

#### List Project Issues

```bash
GET /sentry/api/0/projects/{organization_slug}/{project_slug}/issues/
```

**Query Parameters:**
- `statsPeriod` - Stats period: `24h`, `14d`, or empty
- `shortIdLookup` - Enable short ID lookup (set to `1`)
- `query` - Sentry search query (default: `is:unresolved`)
- `cursor` - Pagination cursor

#### List Organization Issues

```bash
GET /sentry/api/0/organizations/{organization_slug}/issues/
```

#### Retrieve an Issue

```bash
GET /sentry/api/0/issues/{issue_id}/
```

#### Update an Issue

```bash
PUT /sentry/api/0/issues/{issue_id}/
Content-Type: application/json

{
  "status": "resolved"
}
```

**Status values:** `resolved`, `unresolved`, `ignored`

#### Delete an Issue

```bash
DELETE /sentry/api/0/issues/{issue_id}/
```

#### List Issue Events

```bash
GET /sentry/api/0/issues/{issue_id}/events/
```

#### List Issue Hashes

```bash
GET /sentry/api/0/issues/{issue_id}/hashes/
```

### Event Operations

#### List Project Events

```bash
GET /sentry/api/0/projects/{organization_slug}/{project_slug}/events/
```

#### Retrieve an Event

```bash
GET /sentry/api/0/projects/{organization_slug}/{project_slug}/events/{event_id}/
```

### Team Operations

#### List Organization Teams

```bash
GET /sentry/api/0/organizations/{organization_slug}/teams/
```

#### Create a Team

```bash
POST /sentry/api/0/organizations/{organization_slug}/teams/
Content-Type: application/json

{
  "name": "New Team",
  "slug": "new-team"
}
```

#### Retrieve a Team

```bash
GET /sentry/api/0/teams/{organization_slug}/{team_slug}/
```

#### Update a Team

```bash
PUT /sentry/api/0/teams/{organization_slug}/{team_slug}/
Content-Type: application/json

{
  "name": "Updated Team Name"
}
```

#### Delete a Team

```bash
DELETE /sentry/api/0/teams/{organization_slug}/{team_slug}/
```

#### List Team Projects

```bash
GET /sentry/api/0/teams/{organization_slug}/{team_slug}/projects/
```

### Release Operations

#### List Organization Releases

```bash
GET /sentry/api/0/organizations/{organization_slug}/releases/
```

#### Create a Release

```bash
POST /sentry/api/0/organizations/{organization_slug}/releases/
Content-Type: application/json

{
  "version": "1.0.0",
  "projects": ["project-slug"]
}
```

#### Retrieve a Release

```bash
GET /sentry/api/0/organizations/{organization_slug}/releases/{version}/
```

#### Update a Release

```bash
PUT /sentry/api/0/organizations/{organization_slug}/releases/{version}/
Content-Type: application/json

{
  "ref": "main",
  "commits": [
    {
      "id": "abc123",
      "message": "Fix bug"
    }
  ]
}
```

#### Delete a Release

```bash
DELETE /sentry/api/0/organizations/{organization_slug}/releases/{version}/
```

#### List Release Deploys

```bash
GET /sentry/api/0/organizations/{organization_slug}/releases/{version}/deploys/
```

#### Create a Deploy

```bash
POST /sentry/api/0/organizations/{organization_slug}/releases/{version}/deploys/
Content-Type: application/json

{
  "environment": "production"
}
```

## Pagination

Sentry uses cursor-based pagination via the `Link` header.

```bash
GET /sentry/api/0/projects/{organization_slug}/{project_slug}/issues/?cursor=0:100:0
```

Response headers include pagination links:

```
Link: <...?cursor=0:0:1>; rel="previous"; results="false"; cursor="0:0:1",
      <...?cursor=0:100:0>; rel="next"; results="true"; cursor="0:100:0"
```

- `results="true"` indicates more results exist
- `results="false"` indicates no more results in that direction

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/sentry/api/0/organizations/',
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
    'https://gateway.maton.ai/sentry/api/0/organizations/',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
```

### Python - Resolve an Issue

```python
import os
import requests

response = requests.put(
    'https://gateway.maton.ai/sentry/api/0/issues/12345/',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={'status': 'resolved'}
)
```

## Notes

- Sentry API uses version `0` prefix: `/api/0/`
- Organization and project identifiers use slugs (lowercase, hyphenated)
- Issue IDs are numeric
- Release versions can contain special characters (URL encode as needed)
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Sentry connection |
| 401 | Invalid or missing Maton API key |
| 403 | Insufficient permissions (check OAuth scopes) |
| 404 | Resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Sentry API |

## Resources

- [Sentry API Documentation](https://docs.sentry.io/api/)
- [Sentry API Authentication](https://docs.sentry.io/api/auth/)
- [Sentry Events API](https://docs.sentry.io/api/events/)
- [Sentry Projects API](https://docs.sentry.io/api/projects/)
- [Sentry Organizations API](https://docs.sentry.io/api/organizations/)
- [Sentry Teams API](https://docs.sentry.io/api/teams/)
- [Sentry Releases API](https://docs.sentry.io/api/releases/)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
