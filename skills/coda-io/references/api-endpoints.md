# Coda API v1 — Endpoint Reference

Base URL: `https://coda.io/apis/v1`

Auth header: `Authorization: Bearer <token>`

## Table of Contents

- [Account](#account)
- [Folders](#folders)
- [Docs](#docs)
- [Pages](#pages)
- [Tables and Views](#tables-and-views)
- [Columns](#columns)
- [Rows](#rows)
- [Formulas](#formulas)
- [Controls](#controls)
- [Permissions](#permissions)
- [Publishing](#publishing)
- [Automations](#automations)
- [Analytics](#analytics)
- [Miscellaneous](#miscellaneous)

---

## Account

| Method | Path | Description |
|--------|------|-------------|
| GET | `/whoami` | Get info about the API token owner |

## Folders

| Method | Path | Description |
|--------|------|-------------|
| GET | `/folders` | List folders (query: `workspaceId`, `isStarred`, `limit`, `pageToken`) |
| POST | `/folders` | Create folder (body: `name`, `workspaceId`, `description`) |
| GET | `/folders/{folderId}` | Get folder |
| PATCH | `/folders/{folderId}` | Update folder (body: `name`, `description`) |
| DELETE | `/folders/{folderId}` | Delete folder (must be empty) |

## Docs

| Method | Path | Description |
|--------|------|-------------|
| GET | `/docs` | List docs (query: `isOwner`, `isPublished`, `query`, `sourceDoc`, `isStarred`, `inGallery`, `workspaceId`, `folderId`, `limit`, `pageToken`) |
| POST | `/docs` | Create doc (body: `title`, `sourceDoc`, `timezone`, `folderId`, `initialPage`) |
| GET | `/docs/{docId}` | Get doc metadata |
| PATCH | `/docs/{docId}` | Update doc (body: `title`, `iconName`) |
| DELETE | `/docs/{docId}` | Delete doc |

## Pages

| Method | Path | Description |
|--------|------|-------------|
| GET | `/docs/{docId}/pages` | List pages (query: `limit`, `pageToken`) |
| POST | `/docs/{docId}/pages` | Create page (body: `name`, `subtitle`, `iconName`, `parentPageId`, `pageContent`) |
| GET | `/docs/{docId}/pages/{pageIdOrName}` | Get page |
| PATCH | `/docs/{docId}/pages/{pageIdOrName}` | Update page (body: `name`, `subtitle`, `iconName`, `imageUrl`, `contentUpdate`) |
| DELETE | `/docs/{docId}/pages/{pageIdOrName}` | Delete page |
| PUT | `/docs/{docId}/pages/{pageIdOrName}/export` | Begin page content export (body: `outputFormat`: html/markdown) |
| GET | `/docs/{docId}/pages/{pageIdOrName}/export/{requestId}` | Get page content export status |

## Tables and Views

| Method | Path | Description |
|--------|------|-------------|
| GET | `/docs/{docId}/tables` | List tables (query: `limit`, `pageToken`, `sortBy`, `tableTypes`) |
| GET | `/docs/{docId}/tables/{tableIdOrName}` | Get table |

## Columns

| Method | Path | Description |
|--------|------|-------------|
| GET | `/docs/{docId}/tables/{tableIdOrName}/columns` | List columns (query: `limit`, `pageToken`, `visibleOnly`) |
| GET | `/docs/{docId}/tables/{tableIdOrName}/columns/{columnIdOrName}` | Get column |

## Rows

Most-used endpoints. Insert/upsert only work on base tables (not views).

| Method | Path | Description |
|--------|------|-------------|
| GET | `/docs/{docId}/tables/{tableIdOrName}/rows` | List rows (query: `query`, `sortBy`, `useColumnNames`, `valueFormat`, `visibleOnly`, `limit`, `pageToken`) |
| POST | `/docs/{docId}/tables/{tableIdOrName}/rows` | Insert/upsert rows (body: `rows`, `keyColumns`, `disableParsing`) |
| DELETE | `/docs/{docId}/tables/{tableIdOrName}/rows` | Delete multiple rows (body: `rowIds`) |
| GET | `/docs/{docId}/tables/{tableIdOrName}/rows/{rowIdOrName}` | Get row (query: `useColumnNames`, `valueFormat`) |
| PUT | `/docs/{docId}/tables/{tableIdOrName}/rows/{rowIdOrName}` | Update row (body: `row.cells`) |
| DELETE | `/docs/{docId}/tables/{tableIdOrName}/rows/{rowIdOrName}` | Delete row |
| POST | `/docs/{docId}/tables/{tableIdOrName}/rows/{rowIdOrName}/buttons/{columnIdOrName}` | Push button |

### Row body format (insert/upsert)

```json
{
  "rows": [
    {
      "cells": [
        {"column": "c-abc123", "value": "Hello"},
        {"column": "c-def456", "value": 42}
      ]
    }
  ],
  "keyColumns": ["c-abc123"]
}
```

- With `keyColumns`: upsert (update if match, insert if not)
- Without `keyColumns`: always insert

### valueFormat options

- `simple` (default): Plain values
- `simpleWithArrays`: Arrays for list columns
- `rich`: Full structured objects

### useColumnNames

Set `useColumnNames=true` to use column names instead of IDs in row cell keys.

## Formulas

| Method | Path | Description |
|--------|------|-------------|
| GET | `/docs/{docId}/formulas` | List formulas (query: `limit`, `pageToken`) |
| GET | `/docs/{docId}/formulas/{formulaIdOrName}` | Get formula (includes current `value`) |

## Controls

| Method | Path | Description |
|--------|------|-------------|
| GET | `/docs/{docId}/controls` | List controls (query: `limit`, `pageToken`) |
| GET | `/docs/{docId}/controls/{controlIdOrName}` | Get control (includes current `value`) |

## Permissions

| Method | Path | Description |
|--------|------|-------------|
| GET | `/docs/{docId}/acl/metadata` | Get sharing metadata |
| GET | `/docs/{docId}/acl/permissions` | List permissions |
| POST | `/docs/{docId}/acl/permissions` | Add permission (body: `access`, `principal`, `suppressEmail`) |
| DELETE | `/docs/{docId}/acl/permissions/{permissionId}` | Delete permission |
| GET | `/docs/{docId}/acl/principals/search` | Search principals (query: `query`) |
| GET | `/docs/{docId}/acl/settings` | Get ACL settings |
| PATCH | `/docs/{docId}/acl/settings` | Update ACL settings |

### Permission body

```json
{
  "access": "write",
  "principal": {"type": "email", "email": "user@example.com"},
  "suppressEmail": false
}
```

Access levels: `readonly`, `write`, `comment`, `none`

## Publishing

| Method | Path | Description |
|--------|------|-------------|
| GET | `/categories` | List doc categories |
| PUT | `/docs/{docId}/publish` | Publish doc (body: `slug`, `discoverable`, `description`, `mode`, `categories`) |
| DELETE | `/docs/{docId}/publish` | Unpublish doc |

## Automations

| Method | Path | Description |
|--------|------|-------------|
| GET | `/docs/{docId}/hooks/automation/{ruleId}` | Get automation info |
| POST | `/docs/{docId}/hooks/automation/{ruleId}` | Trigger automation (body: optional payload) |

## Analytics

| Method | Path | Description |
|--------|------|-------------|
| GET | `/analytics/docs` | List doc analytics (query: `docIds`, `workspaceId`, `isPublished`, `sinceDate`, `untilDate`, `scale`, `limit`, `pageToken`) |
| GET | `/analytics/docs/{docId}/pages` | List page analytics |
| GET | `/analytics/packs` | List Pack analytics |
| GET | `/analytics/packs/{packId}/formulas` | List Pack formula analytics |
| GET | `/analytics/updated` | Get analytics last-updated day |

## Miscellaneous

| Method | Path | Description |
|--------|------|-------------|
| GET | `/mutationStatus/{requestId}` | Get mutation status (for async write operations) |
| GET | `/docs/{docId}/tables/{tableIdOrName}/rows/resolve` | Resolve browser link to row ID |
| POST | `/docs/{docId}/hooks/automation/{ruleId}` | Trigger automation |

---

## Pagination

All list endpoints support `limit` and `pageToken`. Response includes `nextPageToken` if more results exist.

## Rate Limits

- Reading: 100 req / 6 sec
- Writing (POST/PUT/PATCH): 10 req / 6 sec
- Writing doc content: 5 req / 10 sec
- Listing docs: 4 req / 6 sec
- Analytics: 100 req / 6 sec

On HTTP 429: back off and retry.

## Eventual Consistency

Write operations return HTTP 202 with a `requestId`. Poll `/mutationStatus/{requestId}` to confirm.

For fresh reads: add header `X-Coda-Doc-Version: latest` (returns 400 if stale).

## OpenAPI Spec

- YAML: https://coda.io/apis/v1/openapi.yaml
- JSON: https://coda.io/apis/v1/openapi.json
