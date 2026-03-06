# Session History — Installation Guide

## Prerequisites

- OpenClaw with the gateway dashboard UI
- Node.js with `node:sqlite` support (Node 22+)
- TypeBox (`@sinclair/typebox`) for schema validation

## Step-by-Step Installation

### Phase 1: Backend — New Files

Create these 3 new files:

1. **`src/config/sessions/history-db.ts`**
   Copy from [backend-history-db.ts.txt](backend-history-db.ts.txt)

2. **`src/config/sessions/history-migration.ts`**
   Copy from [backend-history-migration.ts.txt](backend-history-migration.ts.txt)

3. **`src/gateway/session-archive.ts`**
   Copy from [backend-session-archive.ts.txt](backend-session-archive.ts.txt)

### Phase 2: Backend — Protocol Schemas

Add the 4 new TypeBox schemas to `src/gateway/protocol/schema/sessions.ts`:
See [backend-protocol-schemas.ts.txt](backend-protocol-schemas.ts.txt)

Then register them:

1. **Export types** from `src/gateway/protocol/schema/types.ts`:
   ```ts
   export { SessionsArchivedParamsSchema, SessionsResumeParamsSchema,
     SessionsRenameParamsSchema, SessionsDeleteArchivedParamsSchema } from "./sessions.js";
   export type SessionsArchivedParams = Static<typeof SessionsArchivedParamsSchema>;
   // ... same for Resume, Rename, DeleteArchived
   ```

2. **Compile validators** in `src/gateway/protocol/index.ts`:
   ```ts
   export const validateSessionsArchivedParams = ajv.compile<SessionsArchivedParams>(SessionsArchivedParamsSchema);
   export const validateSessionsResumeParams = ajv.compile<SessionsResumeParams>(SessionsResumeParamsSchema);
   export const validateSessionsRenameParams = ajv.compile<SessionsRenameParams>(SessionsRenameParamsSchema);
   export const validateSessionsDeleteArchivedParams = ajv.compile<SessionsDeleteArchivedParams>(SessionsDeleteArchivedParamsSchema);
   ```

### Phase 3: Backend — Sessions Directory Helper

If `resolveSessionTranscriptsDirForAgent` doesn't exist in your version, create it:

```ts
// src/config/sessions/paths.ts
import os from "node:os";
import path from "node:path";

export function resolveSessionTranscriptsDirForAgent(agentId?: string): string {
  const home = process.env.OPENCLAW_HOME || path.join(os.homedir(), ".openclaw");
  const id = agentId || "main";
  return path.join(home, "agents", id, "sessions");
}
```

### Phase 4: Backend — RPC Handlers

Add the 5 RPC handlers to `src/gateway/server-methods/sessions.ts`:
See [backend-rpc-handlers.ts.txt](backend-rpc-handlers.ts.txt)

**5 handlers:**
- `sessions.archive` — Archive active session (deactivate + move to history)
- `sessions.archived` — List archived sessions with pagination
- `sessions.resume` — Resume archived session
- `sessions.rename` — Rename session
- `sessions.deleteArchived` — Delete archived session

**Critical**: Use `({ params, respond })` destructuring pattern. Add all required imports listed at the top of that file.

**Note**: `sessions.archive` reuses the existing `validateSessionsDeleteParams` validator (both need `{ key }` param). No new schema needed for it.

### Phase 5: Frontend — Controller

Replace `ui/src/ui/controllers/sessions.ts` with the full file from [frontend-controllers-sessions.ts.txt](frontend-controllers-sessions.ts.txt).

This adds:
- `loadRecentArchivedSessions()` — fetches 10 most recent for chat dropdown
- `loadArchivedSessions()` — with `limit`/`offset` pagination params
- `resumeSession()`, `renameSession()`, `deleteArchivedSession()`
- Updated `SessionsState` type with pagination fields

### Phase 6: Frontend — Sessions View

Replace `ui/src/ui/views/sessions.ts` with the full file from [frontend-views-sessions.ts.txt](frontend-views-sessions.ts.txt).

This adds:
- `renderSessionHistory()` — archived sessions grid with search
- `renderPaginationControls()` — shared 10/20/25 page-size dropdown + Prev/Next
- `renderArchivedSessionRow()` — row with Resume/Rename/Delete buttons
- **Archive button** on active sessions (hidden for Main Session)
- Updated `SessionsProps` type with `onArchive` + pagination + archived session callbacks

### Phase 7: Frontend — State & Wiring

Apply the changes described in [frontend-state-changes.txt](frontend-state-changes.txt):

1. **`app-view-state.ts`** — Add 9 new state properties to the interface
2. **`app.ts`** — Add 9 `@state()` decorated properties with defaults
3. **`app-chat.ts`** — Import and call `loadRecentArchivedSessions` in `refreshChat()`
4. **`app-settings.ts`** — Import `loadArchivedSessions`, call it when sessions tab loads
5. **`app-render.ts`** — Import archived session functions, wire all props including `onArchive`
6. **`app-render.helpers.ts`** — Add `renderRecentArchivedOptions()`, filter cron/subagent from dropdown, handle `__archived__:` and `__view_all_sessions__` special values

### Phase 8: Build & Test

```bash
npm run build
openclaw doctor --non-interactive
openclaw gateway restart
```

Verify:
1. **Sessions tab** — "Session History" section shows below active sessions
2. **Archive button** — Visible on all rows except Main Session; clicking archives + refreshes
3. **Session History** — Shows archived sessions with search, pagination, Resume/Rename/Delete
4. **Chat dropdown** — Shows only user-facing sessions (no cron/subagent), "Recent Sessions" group, "View All Sessions" link
5. **history.db** — Should exist at `~/.openclaw/agents/main/sessions/history.db`

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `respond is not a function` | Handler uses `(request, respond)` instead of `({ params, respond })` | Fix handler signature to use destructuring |
| `Cannot read 'trim' of undefined` | Using `resolveGatewaySessionStoreTarget(config)` | Replace with `resolveSessionTranscriptsDirForAgent(agentId)` |
| `assertValidParams` fails silently | Missing method name string (3rd arg) | Ensure 4 args: `(params, validator, "method.name", respond)` |
| Shows all rows despite pagination | `loadArchivedSessions` called without `limit`/`offset` | Pass pagination params on every call |
| `No archived sessions found` | Migration hasn't run | Check `history.db` exists; `initHistoryDbWithMigration` should auto-migrate |
| Recent Sessions empty in dropdown | Filtering by `sessionKey` (all share same key) | Must use `sessionId` with `__archived__:` prefix pattern |
| Cron/subagent in chat dropdown | Missing `isUserSession` filter | Add filter excluding `:cron:`, `:subagent:`, `:openai:` keys |
