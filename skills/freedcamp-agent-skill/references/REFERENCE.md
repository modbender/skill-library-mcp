# Reference and implementation notes

This skill is intentionally **dependency-free** (no npm dependencies) and uses:

- Node.js built-in `fetch`, `crypto`
- Freedcamp REST API v1 (`https://freedcamp.com/api/v1`)

## Freedcamp API references

Authentication / HMAC-SHA1:

- The Freedcamp API uses HMAC-SHA1 secured authentication.
- Per-request: generate `hash = HMAC-SHA1(apiKey + timestamp, apiSecret)`, then send `api_key`, `timestamp`, and `hash` as query parameters.
- After session is established, can switch to header-based auth: `X-Freedcamp-API-Token` and `X-Freedcamp-User-Id`.

Key API endpoints:

| Method | Path | Purpose |
|---|---|---|
| GET | `/sessions/current` | Get authenticated session (user, projects, groups) |
| GET | `/tasks/{task_id}` | Fetch single task with comments and files |
| GET | `/tasks` | Fetch tasks with filters and pagination |
| POST | `/tasks` | Create a new task |
| POST | `/tasks/{task_id}` | Update a task |
| GET | `/lists/{app_id}` | Fetch task lists/groups for a project |
| POST | `/comments` | Add a comment to any app item |
| GET | `/notifications` | Fetch notifications (last 60 days) |
| POST | `/notifications` | Mark notifications as read |

Comments / Rich text:

- Comments use HTML formatting.
- Known Freedcamp bug: omitting `<p>` tags in comment body can break formatting.
- Always wrap plain text in `<p>...</p>` before sending.

Pagination:

- Max `limit` is 200 per request.
- Use `offset` parameter for subsequent pages.
- Response includes `meta.has_more` boolean to indicate if more results exist.

Task filters (query parameters):

- `status[]` - Array of status codes (0-4)
- `assigned_to_id[]` - Array of user IDs (0 = unassigned, -1 = everyone)
- `due_date[from]` / `due_date[to]` - Date in YYYY-MM-DD format
- `created_date[from]` / `created_date[to]` - Date in YYYY-MM-DD format
- `list_status` - "active", "archived", or "all"
- `f_with_archived` - 1 to include archived projects, 0 to exclude
- `order[due_date]` / `order[priority]` - "asc" or "dsc"

Session management:

- Session is fetched via `GET /sessions/current`
- Contains: user ID, all projects, all groups, users, notifications count
- Session is cached locally; on 401 response the session auto-refreshes and retries

## Organization hierarchy

Freedcamp organizes work in a hierarchy:

```
Groups (top-level)
  -> Projects
    -> Apps (Tasks, Discussions, Milestones, etc.)
      -> Items (tasks, discussions, etc.)
        -> Comments, Files
```

Each group and project has a set of enabled applications. The session response contains the full hierarchy.

## App type IDs

| ID | Name | Key |
|---|---|---|
| 2 | Tasks | TODOS |
| 3 | Discussions | DISCUSSIONS |
| 4 | Milestones | MILESTONES |
| 5 | Time | TIME |
| 6 | Files | FILES |
| 7 | Invoices | INVOICES |
| 13 | Issue Tracker | BUGTRACKER |
| 14 | Wikis | WIKI |
| 16 | CRM | CRM |
| 17 | Passwords | PASSMAN |
| 19 | Calendar | CALENDAR |
| 20 | Invoices Plus | INVOICESPLUS |
| 37 | Overview | PEOPLE |
| 47 | Planner | PLANNER |
| 48 | Translations | TRANSLATIONS |

## OpenClaw references

- Skills: https://docs.openclaw.ai/tools/skills
- Skills config: https://docs.openclaw.ai/tools/skills-config
- ClawHub: https://docs.openclaw.ai/tools/clawhub
- AgentSkills format: https://agentskills.io/home

## Design decisions

- **Task-focused**: The primary use case is task management (CRUD, status, comments).
- **Session caching**: Session data is cached locally to avoid re-authenticating every request.
- **Auto-pagination**: The `--all` flag handles pagination automatically.
- **Name-based resolution**: `create-task-by-name` resolves project names to IDs using session data.
- **HTML auto-wrapping**: Plain text comments are auto-wrapped in `<p>` tags to work around the Freedcamp formatting bug.
- **Output is JSON-only**: Designed for agents and automation.

## OpenClaw CLI config helpers

- Config CLI (get/set/unset): https://docs.openclaw.ai/cli/config
