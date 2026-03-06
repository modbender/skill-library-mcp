---
name: coda
description: |
  Coda API integration with managed OAuth. Manage docs, pages, tables, rows, and formulas.
  Use this skill when users want to read, create, update, or delete Coda docs, pages, tables, or rows.
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

# Coda

Access the Coda API with managed OAuth authentication. Manage docs, pages, tables, rows, formulas, and controls with full CRUD operations.

## Quick Start

```bash
# List your docs
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/coda/apis/v1/docs')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/coda/apis/v1/{resource}
```

Replace `{resource}` with the actual Coda API endpoint path. The gateway proxies requests to `coda.io/apis/v1` and automatically injects your OAuth token.

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

Manage your Coda OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=coda&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'coda'}).encode()
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
    "connection_id": "f46d34b1-3735-478a-a0d7-54115a16cd46",
    "status": "ACTIVE",
    "creation_time": "2026-02-12T01:38:10.500238Z",
    "last_updated_time": "2026-02-12T01:38:33.545353Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "coda",
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

If you have multiple Coda connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/coda/apis/v1/docs')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', 'f46d34b1-3735-478a-a0d7-54115a16cd46')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Account

#### Get Current User

```bash
GET /coda/apis/v1/whoami
```

Returns information about the authenticated user.

### Docs

#### List Docs

```bash
GET /coda/apis/v1/docs
```

Query parameters:
- `isOwner` - Show only owned docs (true/false)
- `query` - Search query
- `sourceDoc` - Filter by source doc ID
- `isStarred` - Show only starred docs
- `inGallery` - Show only gallery docs
- `workspaceId` - Filter by workspace
- `folderId` - Filter by folder
- `limit` - Page size (default: 25, max: 200)
- `pageToken` - Pagination token

#### Create Doc

```bash
POST /coda/apis/v1/docs
Content-Type: application/json

{
  "title": "My New Doc",
  "sourceDoc": "optional-source-doc-id",
  "timezone": "America/Los_Angeles",
  "folderId": "optional-folder-id"
}
```

#### Get Doc

```bash
GET /coda/apis/v1/docs/{docId}
```

#### Delete Doc

```bash
DELETE /coda/apis/v1/docs/{docId}
```

### Pages

#### List Pages

```bash
GET /coda/apis/v1/docs/{docId}/pages
```

Query parameters:
- `limit` - Page size
- `pageToken` - Pagination token

#### Create Page

```bash
POST /coda/apis/v1/docs/{docId}/pages
Content-Type: application/json

{
  "name": "New Page",
  "subtitle": "Optional subtitle",
  "parentPageId": "optional-parent-page-id"
}
```

#### Get Page

```bash
GET /coda/apis/v1/docs/{docId}/pages/{pageIdOrName}
```

#### Update Page

```bash
PUT /coda/apis/v1/docs/{docId}/pages/{pageIdOrName}
Content-Type: application/json

{
  "name": "Updated Page Name",
  "subtitle": "Updated subtitle"
}
```

#### Delete Page

```bash
DELETE /coda/apis/v1/docs/{docId}/pages/{pageIdOrName}
```

### Tables

#### List Tables

```bash
GET /coda/apis/v1/docs/{docId}/tables
```

Query parameters:
- `limit` - Page size
- `pageToken` - Pagination token
- `sortBy` - Sort by field
- `tableTypes` - Filter by table type

#### Get Table

```bash
GET /coda/apis/v1/docs/{docId}/tables/{tableIdOrName}
```

### Columns

#### List Columns

```bash
GET /coda/apis/v1/docs/{docId}/tables/{tableIdOrName}/columns
```

Query parameters:
- `limit` - Page size
- `pageToken` - Pagination token

#### Get Column

```bash
GET /coda/apis/v1/docs/{docId}/tables/{tableIdOrName}/columns/{columnIdOrName}
```

### Rows

#### List Rows

```bash
GET /coda/apis/v1/docs/{docId}/tables/{tableIdOrName}/rows
```

Query parameters:
- `query` - Filter rows by search query
- `useColumnNames` - Use column names instead of IDs in response (true/false)
- `valueFormat` - Value format (simple, simpleWithArrays, rich)
- `sortBy` - Sort by column
- `limit` - Page size
- `pageToken` - Pagination token

#### Get Row

```bash
GET /coda/apis/v1/docs/{docId}/tables/{tableIdOrName}/rows/{rowIdOrName}
```

Query parameters:
- `useColumnNames` - Use column names instead of IDs
- `valueFormat` - Value format

#### Insert/Upsert Rows

```bash
POST /coda/apis/v1/docs/{docId}/tables/{tableIdOrName}/rows
Content-Type: application/json

{
  "rows": [
    {
      "cells": [
        {"column": "Column Name", "value": "Cell Value"},
        {"column": "Another Column", "value": 123}
      ]
    }
  ],
  "keyColumns": ["Column Name"]
}
```

- Use `keyColumns` for upsert behavior (update if exists, insert if not)
- Row inserts/upserts are processed asynchronously (returns requestId)

#### Update Row

```bash
PUT /coda/apis/v1/docs/{docId}/tables/{tableIdOrName}/rows/{rowIdOrName}
Content-Type: application/json

{
  "row": {
    "cells": [
      {"column": "Column Name", "value": "Updated Value"}
    ]
  }
}
```

#### Delete Row

```bash
DELETE /coda/apis/v1/docs/{docId}/tables/{tableIdOrName}/rows/{rowIdOrName}
```

### Formulas

#### List Formulas

```bash
GET /coda/apis/v1/docs/{docId}/formulas
```

#### Get Formula

```bash
GET /coda/apis/v1/docs/{docId}/formulas/{formulaIdOrName}
```

### Controls

#### List Controls

```bash
GET /coda/apis/v1/docs/{docId}/controls
```

#### Get Control

```bash
GET /coda/apis/v1/docs/{docId}/controls/{controlIdOrName}
```

### Permissions

#### Get Sharing Metadata

```bash
GET /coda/apis/v1/docs/{docId}/acl/metadata
```

#### List Permissions

```bash
GET /coda/apis/v1/docs/{docId}/acl/permissions
```

#### Add Permission

```bash
POST /coda/apis/v1/docs/{docId}/acl/permissions
Content-Type: application/json

{
  "access": "readonly",
  "principal": {
    "type": "email",
    "email": "user@example.com"
  }
}
```

Access values: `readonly`, `write`, `comment`

#### Delete Permission

```bash
DELETE /coda/apis/v1/docs/{docId}/acl/permissions/{permissionId}
```

### Categories

#### List Categories

```bash
GET /coda/apis/v1/categories
```

### Utilities

#### Resolve Browser Link

```bash
GET /coda/apis/v1/resolveBrowserLink?url={encodedUrl}
```

Converts a Coda browser URL to API resource information.

#### Get Mutation Status

```bash
GET /coda/apis/v1/mutationStatus/{requestId}
```

Check the status of an asynchronous mutation operation.

### Analytics

#### List Doc Analytics

```bash
GET /coda/apis/v1/analytics/docs
```

Query parameters:
- `isPublished` - Filter by published status
- `sinceDate` - Start date (YYYY-MM-DD)
- `untilDate` - End date (YYYY-MM-DD)
- `limit` - Page size
- `pageToken` - Pagination token

#### List Pack Analytics

```bash
GET /coda/apis/v1/analytics/packs
```

#### Get Analytics Update Time

```bash
GET /coda/apis/v1/analytics/updated
```

## Pagination

Coda uses cursor-based pagination with `pageToken`:

```bash
GET /coda/apis/v1/docs?limit=25
```

Response includes `nextPageToken` when more results exist:

```json
{
  "items": [...],
  "href": "https://coda.io/apis/v1/docs?pageToken=...",
  "nextPageToken": "eyJsaW1..."
}
```

Use the `nextPageToken` value as `pageToken` in subsequent requests.

## Asynchronous Mutations

Create, update, and delete operations return HTTP 202 with a `requestId`:

```json
{
  "id": "canvas-abc123",
  "requestId": "mutate:9f038510-be42-4d16-bccf-3468d38efd57"
}
```

Check mutation status:

```bash
GET /coda/apis/v1/mutationStatus/mutate:9f038510-be42-4d16-bccf-3468d38efd57
```

Response:
```json
{
  "completed": true
}
```

Mutations are generally processed within a few seconds.

## Code Examples

### JavaScript - List Docs

```javascript
const response = await fetch(
  'https://gateway.maton.ai/coda/apis/v1/docs?limit=10',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
console.log(data.items);
```

### Python - List Docs

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/coda/apis/v1/docs',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'limit': 10}
)
data = response.json()
for doc in data['items']:
    print(f"{doc['name']}: {doc['id']}")
```

### Python - Create Doc and Page

```python
import os
import requests

headers = {'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
base_url = 'https://gateway.maton.ai/coda/apis/v1'

# Create doc
doc_response = requests.post(
    f'{base_url}/docs',
    headers=headers,
    json={'title': 'My New Doc'}
)
doc = doc_response.json()
print(f"Created doc: {doc['id']}")

# Create page
page_response = requests.post(
    f'{base_url}/docs/{doc["id"]}/pages',
    headers=headers,
    json={'name': 'First Page', 'subtitle': 'Created via API'}
)
page = page_response.json()
print(f"Created page: {page['id']}")
```

### Python - Insert Rows

```python
import os
import requests

headers = {'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}

response = requests.post(
    'https://gateway.maton.ai/coda/apis/v1/docs/{docId}/tables/{tableId}/rows',
    headers=headers,
    json={
        'rows': [
            {
                'cells': [
                    {'column': 'Name', 'value': 'John Doe'},
                    {'column': 'Email', 'value': 'john@example.com'}
                ]
            }
        ]
    }
)
result = response.json()
print(f"Request ID: {result['requestId']}")
```

## Notes

- Doc IDs look like `s0ekj2vV-v`
- Page IDs start with `canvas-`
- Table and column names can be used instead of IDs
- Row operations require a base table (not views)
- Create/Update/Delete operations are asynchronous (return requestId)
- Newly created docs may take a moment to be accessible via API (409 error)
- Page-level analytics require Enterprise plan
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq`, environment variables may not expand correctly. Use Python examples instead.

## Rate Limits

| Operation | Limit |
|-----------|-------|
| Reading data | 100 requests per 6 seconds |
| Writing data | 10 requests per 6 seconds |
| Writing doc content | 5 requests per 10 seconds |
| Listing docs | 4 requests per 6 seconds |
| Reading analytics | 100 requests per 6 seconds |

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Coda connection or invalid request |
| 401 | Invalid or missing Maton API key |
| 404 | Resource not found |
| 409 | Doc not yet accessible (just created) |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Coda API |

### Troubleshooting: API Key Issues

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Invalid App Name

1. Ensure your URL path starts with `coda`. For example:

- Correct: `https://gateway.maton.ai/coda/apis/v1/docs`
- Incorrect: `https://gateway.maton.ai/apis/v1/docs`

## Resources

- [Coda API Documentation](https://coda.io/developers/apis/v1)
- [Coda API Postman Collection](https://www.postman.com/codaio/coda-workspace/collection/0vy7uxn/coda-api)
- [Coda API Python Library (codaio)](https://codaio.readthedocs.io/)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
