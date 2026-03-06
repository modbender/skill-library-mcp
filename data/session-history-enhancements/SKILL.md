---
name: session-history
description: "Session history system for OpenClaw — persistent, browsable, resumable chat sessions with SQLite index, archive/restore, migration, paginated UI, and chat dropdown integration. Use when: (1) adding session archival/indexing to OpenClaw, (2) implementing session browsing/search in the dashboard, (3) adding session resume/rename/delete, (4) archiving active sessions from the dashboard, (5) adding pagination to session lists, or (6) integrating recent sessions into the chat dropdown."
---

# Session History

Transforms OpenClaw's single-slot session model into a multi-session history system with SQLite indexing, archive/restore, and full dashboard UI.

## Architecture

```
~/.openclaw/agents/{agentId}/sessions/
├── sessions.json           # routing table (unchanged)
├── history.db              # SQLite index (auto-created)
├── {activeSessionId}.jsonl # active transcript
└── archive/
    └── {sessionId}.jsonl   # archived transcripts
```

**Lifecycle:**
- On `/new` or session reset → old transcript moves to `archive/`, metadata indexed in SQLite
- On archive (from UI) → session deactivated, transcript archived, indexed, removed from store
- On resume → transcript moves back from `archive/`, SQLite status flips to active
- Migration auto-runs on first access: indexes all orphaned `.jsonl` files

## File Map

### Backend (new files)

| File | Reference | Purpose |
|------|-----------|---------|
| `src/config/sessions/history-db.ts` | [references/backend-history-db.ts.txt](references/backend-history-db.ts.txt) | SQLite CRUD operations |
| `src/config/sessions/history-migration.ts` | [references/backend-history-migration.ts.txt](references/backend-history-migration.ts.txt) | One-time migration + `initHistoryDbWithMigration` |
| `src/gateway/session-archive.ts` | [references/backend-session-archive.ts.txt](references/backend-session-archive.ts.txt) | Archive/restore logic |

### Backend (modified files)

| File | Reference | Purpose |
|------|-----------|---------|
| `src/gateway/protocol/schema/sessions.ts` | [references/backend-protocol-schemas.ts.txt](references/backend-protocol-schemas.ts.txt) | TypeBox schemas for new RPCs |
| `src/gateway/server-methods/sessions.ts` | [references/backend-rpc-handlers.ts.txt](references/backend-rpc-handlers.ts.txt) | 5 RPC handler implementations |

### Frontend (modified files)

| File | Reference | Purpose |
|------|-----------|---------|
| `ui/src/ui/controllers/sessions.ts` | [references/frontend-controllers-sessions.ts.txt](references/frontend-controllers-sessions.ts.txt) | Full controller with archived session CRUD + pagination |
| `ui/src/ui/views/sessions.ts` | [references/frontend-views-sessions.ts.txt](references/frontend-views-sessions.ts.txt) | Full view with Session History section, Archive button, pagination |
| `ui/src/ui/app-view-state.ts` | [references/frontend-state-changes.txt](references/frontend-state-changes.txt) | State + app.ts + app-render.ts + app-chat.ts + app-settings.ts + app-render.helpers.ts wiring |

## Installation

See [references/INSTALL.md](references/INSTALL.md) for step-by-step instructions.

## RPC Endpoints

| Method | Params | Purpose |
|--------|--------|---------|
| `sessions.archive` | `key` | **Archive active session** — deactivates, moves transcript, indexes in SQLite, removes from store |
| `sessions.archived` | `agentId?, limit?, offset?, search?, status?` | List archived sessions with pagination and search |
| `sessions.resume` | `sessionId, agentId?` | Restore archived session to active |
| `sessions.rename` | `sessionId, displayName, agentId?` | Update session display name |
| `sessions.deleteArchived` | `sessionId, agentId?, deleteTranscript?` | Delete archived session + optional transcript |

## UI Features

### Sessions Page
- **Active Sessions grid** — with Archive button (hidden for Main Session), History, Delete
- **Session History section** — archived sessions with search, Resume/Rename/Delete buttons
- **Pagination** — both sections have 10/20/25 page-size dropdown + Prev/Next

### Chat Dropdown
- Filters out cron/subagent/openai sessions (only user-facing sessions shown)
- "Recent Sessions" `<optgroup>` with 10 most recent archived sessions
- "📋 View All Sessions" link navigates to Sessions tab
- Selecting an archived session auto-resumes it

## Key Design Decisions

- **SQLite over JSON**: Supports search, pagination, and indexing without loading everything into memory
- **Server-side pagination for archives**: Pass `limit`/`offset` to `sessions.archived` RPC
- **Client-side pagination for live sessions**: Slice the already-loaded array
- **sessionId-based dropdown values**: Archived sessions all share the same `sessionKey` (`agent:main:main`), so the dropdown uses `__archived__:{sessionId}` as the option value
- **`sessions.archive` reuses `sessions.delete` param schema**: Both need just `{ key }`

## Common Pitfalls

1. **RPC handler signature**: Must use `({ params, respond })` destructuring, not `(request, respond)`
2. **assertValidParams**: Takes 4 args: `(params, validator, "method.name", respond)`
3. **Sessions directory**: Use `resolveSessionTranscriptsDirForAgent(agentId)` — NOT `resolveGatewaySessionStoreTarget(config)`
4. **Pagination on every load**: All `loadArchivedSessions` calls must pass `limit` and `offset`
5. **Page reset**: Changing page size or search query must reset page to 1
6. **Archived session dropdown filtering**: Filter by sessionId, not sessionKey (all archived sessions share the same sessionKey)
