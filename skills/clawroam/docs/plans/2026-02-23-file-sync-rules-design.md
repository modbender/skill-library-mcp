# Per-Profile File Sync Rules — Design

**Date:** 2026-02-23
**Status:** Approved

## Overview

Allow users to select which files are synced per machine (profile). Default is "share all" — users opt out individual files. The selection is stored server-side and respected by the client before building the push archive.

## Data Model

New D1 table added to `schema.sql`:

```sql
CREATE TABLE IF NOT EXISTS sync_rules (
  id           TEXT PRIMARY KEY,
  vault_id     TEXT NOT NULL REFERENCES vaults(id),
  profile_name TEXT NOT NULL,
  path         TEXT NOT NULL,
  created_at   TEXT DEFAULT (datetime('now')),
  UNIQUE(vault_id, profile_name, path)
);
CREATE INDEX IF NOT EXISTS idx_sync_rules_profile ON sync_rules(vault_id, profile_name);
```

Only **excluded** paths are stored. Absence of a row means the file is shared. This keeps the table empty for the common case (share everything).

## API

Two new endpoints in `cloud-api-worker/src/index.ts`:

### `GET /v1/vaults/:id/profiles/:profile/sync-rules`
- Auth: JWT (dashboard) or Ed25519 (client)
- Response: `{ excluded: ["path/a", "path/b"] }`
- Returns empty array if no rules exist

### `PUT /v1/vaults/:id/profiles/:profile/sync-rules`
- Auth: JWT (dashboard) or Ed25519 (client)
- Body: `{ excluded: ["path/a", "path/b"] }`
- Atomically replaces the full exclusion list (delete all + insert new)
- Response: `{ status: "ok", excluded_count: N }`

## Dashboard UI (`web/dashboard.html`)

- Each file row gets a checkbox on the left
- On profile column load, fetch `GET sync-rules` and build a `Set` of excluded paths
- Checked = shared (default); unchecked = excluded
- Excluded file rows: dimmed to 40% opacity, strikethrough filename, 🚫 icon
- Profile header shows `N excluded` badge when any exclusions exist
- Toggling a checkbox updates local state immediately, then debounces 500ms before calling `PUT sync-rules` with the full updated list
- Toast on save: "Sync rules saved" / error on failure

## Bash Client (`providers/cloud.sh`)

Before building the push archive in the `push` function:

1. Call `GET /v1/vaults/:id/profiles/:profile/sync-rules` with Ed25519 auth
2. Parse the `excluded` array
3. Build `--exclude=<path>` flags for each entry
4. Pass them to `tar` when creating the archive

Failure behaviour: if the API call fails (network error, timeout), log a warning and push everything — sync is never blocked by a rules fetch failure.

## Sequence

```
User unchecks "knowledge/private-notes.md" in dashboard
  → PUT /sync-rules { excluded: ["knowledge/private-notes.md"] }
  → D1: INSERT INTO sync_rules (vault_id, profile, path)

clawroam.sh sync push (on machine)
  → GET /sync-rules → { excluded: ["knowledge/private-notes.md"] }
  → tar czf archive.tar.gz --exclude=knowledge/private-notes.md -C ~/.clawroam .
  → PUT /profiles/Jasper/sync → uploads filtered archive

Other machines pull → never receive private-notes.md
```

## Files Changed

| File | Change |
|---|---|
| `cloud-api-worker/schema.sql` | Add `sync_rules` table + index |
| `cloud-api-worker/src/index.ts` | Add GET + PUT `/sync-rules` endpoints |
| `web/dashboard.html` | Checkbox UI, exclusion state, debounced save |
| `providers/cloud.sh` | Fetch rules before push, apply `--exclude` flags |
