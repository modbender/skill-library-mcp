# Squad Control API Reference

**Base URL:** `https://squadcontrol.ai` (set as `SC_API_URL`)  
**Auth:** `x-api-key: <SC_API_KEY>` header on all requests.

---

## API Key Scopes

**Workspace-scoped key** — bound to a single workspace. All endpoints return/operate on that workspace only.

**Account-scoped key** — spans all workspaces in your account.
- `/api/tasks/pending` returns tasks from **all workspaces**, each with an embedded `workspace` object
- `/api/tasks/list` returns tasks across all workspaces; use `?workspaceId=<id>` to scope to one
- All write endpoints (`pickup`, `complete`, `set-review`, etc.) work normally with either key type

---

## GET /api/tasks/pending

Returns tasks ready for pickup. OpenClaw polls this every 15 min.

Optional query params: `?agentId=<id>` (filter by agent), `?limit=<n>`

**Response (workspace-scoped key):**
```json
{
  "workspace": {
    "_id": "wsId",
    "name": "My Workspace",
    "repoUrl": "https://github.com/org/repo",
    "githubToken": "ghp_xxxx",
    "agentConcurrency": 2
  },
  "tasks": [{
    "_id": "taskId",
    "title": "Add dark mode toggle",
    "description": "...",
    "priority": "medium",
    "tags": ["frontend"],
    "agent": {
      "_id": "agentId",
      "name": "Cody",
      "role": "Developer",
      "model": "anthropic/claude-sonnet-4-6",
      "soulMd": "You are Cody..."
    }
  }]
}
```

**Response (account-scoped key):**
```json
{
  "tasks": [{
    "_id": "taskId",
    "title": "Add dark mode toggle",
    "description": "...",
    "priority": "medium",
    "tags": ["frontend"],
    "workspace": {
      "_id": "wsId",
      "name": "My Workspace",
      "repoUrl": "https://github.com/org/repo",
      "githubToken": "ghp_xxxx",
      "agentConcurrency": 3
    },
    "agent": {
      "_id": "agentId",
      "name": "Cody",
      "role": "Developer",
      "model": "anthropic/claude-sonnet-4-6",
      "soulMd": "You are Cody..."
    }
  }]
}
```

With an account-scoped key, tasks from different workspaces may appear in the same response. Each task's `workspace` object contains all config needed — no local workspace file required.

### The `workspace` Object

| Field | Type | Description |
|---|---|---|
| `_id` | string | Workspace ID |
| `name` | string | Human-readable workspace name |
| `repoUrl` | string | GitHub repo URL |
| `githubToken` | string | GitHub token for this workspace's repo (may be empty for public repos) |
| `agentConcurrency` | number | Max simultaneous agents for this workspace |

**Important:** When `task.workspace` is present, use it directly for all workspace config. If absent, use the top-level `workspace` from the response (workspace-scoped key, backward-compatible behavior).

---

## POST /api/tasks/pickup

Mark a task as in-progress. Call this before starting work.

Body:
```json
{ "taskId": "...", "agentId": "...", "branch": "task/<taskId>" }
```

Response includes workspace context (same as pending):
```json
{
  "success": true,
  "workspace": {
    "repoUrl": "https://github.com/org/repo",
    "githubToken": "ghp_xxxx"
  }
}
```

---

## POST /api/threads/send

Post a message to the task's thread. Use for status updates, findings, errors.

Body:
```json
{ "taskId": "...", "agentId": "...", "content": "Starting work on the feature..." }
```

Always post results here before marking a task done — this is what the human sees.

---

## POST /api/tasks/complete

Mark task done with result.

Body:
```json
{
  "taskId": "...",
  "agentId": "...",
  "result": "Summary of what was done",
  "status": "done",
  "deliverables": [{ "type": "pr", "name": "PR #42", "url": "https://github.com/..." }]
}
```

---

## POST /api/tasks/set-review

Move task to review queue (use when a reviewer agent exists).

Body:
```json
{
  "taskId": "...",
  "agentId": "...",
  "result": "Summary of changes",
  "deliverables": [{ "type": "pr", "name": "PR #42", "url": "https://github.com/..." }]
}
```

---

## POST /api/tasks/review

Submit review verdict after examining a PR.

Body:
```json
{
  "taskId": "...",
  "agentId": "...",
  "verdict": "approve",
  "comments": "Looks good. Clean implementation, types pass."
}
```

`verdict` must be `"approve"` or `"request_changes"`.

---

## POST /api/tasks/fail

Report a task failure. Always call this instead of silently stopping.

Body:
```json
{ "taskId": "...", "agentId": "...", "error": "tsc failed with 3 errors in billing.ts" }
```

---

## POST /api/tasks/create

Create a new task programmatically (useful for breaking down work into subtasks).

Body:
```json
{
  "title": "Fix login redirect bug",
  "description": "After OAuth, users land on /dashboard instead of /onboarding",
  "priority": "high",
  "tags": ["bug", "auth"],
  "assignedAgentId": "..."
}
```

---

## GET /api/agents

List all agents in the workspace.

Response:
```json
{
  "agents": [{
    "_id": "...",
    "name": "Cody",
    "role": "Developer",
    "model": "anthropic/claude-sonnet-4-6",
    "soulMd": "..."
  }]
}
```

Look for `role: "Code Reviewer"` to identify the reviewer agent.

---

## GET /api/tasks/list

List all tasks accessible to this API key.

Optional query params:
- `?status=<status>` — filter by task status (e.g. `review`, `working`, `done`)
- `?workspaceId=<id>` — filter by workspace ID (useful with account-scoped keys to scope results to one workspace)

Response: `{ "tasks": [...] }`

---

## GET /api/workspace

Get workspace details including repo URL.

---

## GET /api/health

Health check, no auth required. Returns `{ "status": "ok" }`.
