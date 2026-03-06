---
name: fabric-api
description: Create, search, and manage Fabric resources via the Fabric HTTP API (notepads/notes, folders, bookmarks, files, tags).
homepage: https://fabric.so
metadata: {"openclaw":{"emoji":"🧵","homepage":"https://fabric.so","requires":{"env":["FABRIC_API_KEY"],"anyBins":["node","python3","python","curl"]},"primaryEnv":"FABRIC_API_KEY"},"clawdbot":{"emoji":"🧵","homepage":"https://fabric.so","requires":{"env":["FABRIC_API_KEY"],"anyBins":["node","python3","python","curl"]},"primaryEnv":"FABRIC_API_KEY"}}
---

# Fabric API (HTTP via Node/Python)

Use this skill when you need to **read or write content in a user's Fabric workspace** using the Fabric HTTP API (`https://api.fabric.so`).

This version avoids bash-only wrapper scripts. It ships **cross-platform** helpers:

- Node: `{baseDir}/scripts/fabric.mjs` (recommended)
- Python: `{baseDir}/scripts/fabric.py`

## Critical gotchas (read first)

- **There is no** `POST /v2/notes` endpoint in the bundled OpenAPI spec. To create a “note”, use **`POST /v2/notepads`**.
- Most create endpoints require **`parentId`**:
  - A folder UUID **or** one of: `@alias::inbox`, `@alias::bin`
- Notepad creation requires:
  - `parentId`
  - and **either** `text` (markdown string) **or** `ydoc` (advanced/structured)
- `tags` must be **an array of objects**, each item **either**:
  - `{ "name": "tag name" }` **or** `{ "id": "<uuid>" }`
  - Never strings, never nested arrays.
- **Field name gotcha:** the API schema uses `name` (not `title`). If the user says “title”, map it to `name` in requests.

When the user doesn’t specify a destination folder, default to:

- `parentId: "@alias::inbox"`

## Setup (OpenClaw / Clawdbot)

This skill expects the Fabric API key in:

- `FABRIC_API_KEY`

OpenClaw config example (`~/.openclaw/openclaw.json`):

```json5
{
  skills: {
    entries: {
      "fabric-api": {
        enabled: true,
        apiKey: "YOUR_FABRIC_API_KEY"
      }
    }
  }
}
```

Notes:

- `apiKey` is a convenience for skills that declare `primaryEnv`; it injects `FABRIC_API_KEY` for the duration of an agent run.
- Don’t paste the API key into prompts, client-side code, or logs.

## HTTP basics

- Base URL: `https://api.fabric.so` (override with `FABRIC_BASE` if needed)
- Auth header: `X-Api-Key: $FABRIC_API_KEY`
- JSON header (for JSON bodies): `Content-Type: application/json`

## Convenience scripts (cross-platform)

### Node helper (recommended)

```bash
node {baseDir}/scripts/fabric.mjs GET /v2/user/me

node {baseDir}/scripts/fabric.mjs POST /v2/notepads --json '{"name":"Test note","text":"Hello","parentId":"@alias::inbox"}'
```

### Python helper

```bash
python3 {baseDir}/scripts/fabric.py GET /v2/user/me

python3 {baseDir}/scripts/fabric.py POST /v2/notepads --json '{"name":"Test note","text":"Hello","parentId":"@alias::inbox"}'
```

Notes:

- Both helpers print the response body on success.
- On HTTP errors (4xx/5xx), they print `HTTP <code> <reason>` to stderr **and still print the response body**, then exit non‑zero (similar to `curl --fail-with-body`).
- If you pass an absolute URL (`https://...`), the helpers **do not** attach `X-Api-Key` unless you explicitly pass `--with-key`.

## Core workflows

### 1) Create a notepad (note)

Endpoint: `POST /v2/notepads`

Rules:

- Map user “title” → `name`
- Use `text` for markdown content
- Always include `parentId`
- If you’re debugging 400s, start minimal (required fields only), then add `name`, then `tags`.

Minimal create:

```bash
node {baseDir}/scripts/fabric.mjs POST /v2/notepads --json '{"parentId":"@alias::inbox","text":"Hello"}'
```

Create with a name:

```bash
node {baseDir}/scripts/fabric.mjs POST /v2/notepads --json '{"name":"Calendar Test Note","text":"Created via OpenClaw","parentId":"@alias::inbox"}'
```

Create with tags (correct shape):

```bash
node {baseDir}/scripts/fabric.mjs POST /v2/notepads --json '{"name":"Ideas","text":"# Ideas\\n\\n- First\\n- Second\\n","parentId":"@alias::inbox","tags":[{"name":"ideas"},{"name":"draft"}]}'
```

If you keep seeing tag validation errors, temporarily omit `tags` and create the notepad first.

### 2) Create a folder

Endpoint: `POST /v2/folders`

```bash
node {baseDir}/scripts/fabric.mjs POST /v2/folders --json '{"name":"My new folder","parentId":"@alias::inbox","description":null}'
```

### 3) Create a bookmark

Endpoint: `POST /v2/bookmarks`

```bash
node {baseDir}/scripts/fabric.mjs POST /v2/bookmarks --json '{"url":"https://example.com","parentId":"@alias::inbox","name":"Example","tags":[{"name":"reading"}]}'
```

### 4) Browse resources (list children of a folder)

Endpoint: `POST /v2/resources/filter`

Important:

- This endpoint’s `parentId` expects a **UUID** (not an alias).
- If you only have an alias, resolve it by listing resource roots and picking the inbox/bin folder ID.

```bash
node {baseDir}/scripts/fabric.mjs POST /v2/resources/filter --json '{"parentId":"PARENT_UUID_HERE","limit":50,"order":{"property":"modifiedAt","direction":"DESC"}}'
```

### 5) Search

Endpoint: `POST /v2/search`

Use search when the user gives a fuzzy description (“the note about…”).

```bash
node {baseDir}/scripts/fabric.mjs POST /v2/search --json '{"queries":[{"mode":"text","text":"meeting notes","filters":{"kinds":["notepad"]}}],"pagination":{"page":1,"pageSize":20},"sort":{"field":"modifiedAt","order":"desc"}}'
```

## Error handling + retries (practical guidance)

- **400 Bad Request**: schema validation. Re-check required fields, and that `tags` is `[{name}|{id}]` not nested.
- **401/403**: auth/subscription/permission. Stop and report the error details; don’t brute-force.
- **404**: wrong endpoint, wrong ID, or no access.
- **429**: rate limiting. Back off (sleep + jitter) and retry **reads**. Avoid blind retries on **create** (you may create duplicates).
- **5xx**: transient; retry with backoff.

## Reference files

- OpenAPI spec (source of truth): `{baseDir}/fabric-api.yaml`
- Extra schema notes: `{baseDir}/references/REFERENCE.md`
- Debug playbook: `{baseDir}/references/TROUBLESHOOTING.md`
