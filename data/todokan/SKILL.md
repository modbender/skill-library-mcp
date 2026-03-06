---
name: todokan
version: 1.3.2
description: "Manage tasks, boards, thoughts, and reviews in Todokan via MCP"
homepage: https://todokan.com
metadata: {"category":"productivity","tags":["tasks","kanban","mcp","planning","review"],"requires":{"env":["TODOKAN_API_KEY","TODOKAN_MCP_URL"],"mcp":true},"openclaw":{"homepage":"https://todokan.com","requires":{"env":["TODOKAN_API_KEY","TODOKAN_MCP_URL"]}}}
---

# Todokan — Kanban Task Management

Todokan is a kanban-style task manager. You can manage the user's tasks, boards, and projects through MCP tools.

## Prerequisites

- A Todokan MCP server must be available (see README for setup)
- Required env vars: `TODOKAN_API_KEY`, `TODOKAN_MCP_URL` (declared in skill metadata)

---

## Trigger — When to Activate This Skill

Activate the Todokan skill when the user has one of the following intents:

| Intent | Example |
|--------|---------|
| Create / edit / delete a task | "Create a task: review PR" |
| Show boards or tasks | "Show me my tasks", "What's on the dev board?" |
| Change status | "Mark task X as done" |
| Save research results | "Save this as a task / document in Todokan" |
| Briefing / summary from tasks | "Give me a briefing of my open tasks" |
| Attach a document to a task | "Write a note on task X" |
| Search topics across boards | "What did I note about the investor meeting?" |
| Retrieve changes since last check | "What's new since this morning?" |

**Do not** activate when the user is just talking about tasks in general without referencing Todokan.

---

## Tool Ordering

Follow this order to achieve consistent results:

### Reading (always orient first)

```
1. list_habitats            → Which workspaces exist?
2. list_boards              → Which boards exist? (note the IDs)
3. list_tasks               → Tasks on a board (with filters)
4. search_across_habitats   → Full-text search across boards/habitats
5. get_events_since         → Retrieve changes since a timestamp
6. list_board_labels        → Available labels + usage counts
7. list_task_documents      → Documents attached to a task
8. read_document            → Content of a document
```

### Writing (only after orientation + confirmation)

```
9.  create_task / create_board / create_habitat
10. update_task / update_task_by_title
11. create_document / add_document_to_task
12. delete_task              → Only after explicit confirmation
```

### AI-Assisted (optional)

```
13. propose_task_variants    → Generate 2-3 variants
14. confirm_task_fields      → Review fields before creation
```

**Golden rule:** Never write blindly. Always call `list_boards` first to discover IDs — never guess UUIDs.

---

## Mandatory Checks

Before executing write actions, clarify the following:

### Before `create_task`
- [ ] **Board**: Which board? (If unclear → show `list_boards`, let the user choose)
- [ ] **Title**: Short, precise, imperative (max 80 characters)
- [ ] **Priority**: low / normal / high — default to `normal` if unclear
- [ ] **Due date**: Only set if mentioned by the user

### Before `update_task`
- [ ] **Correct task?** State the title + board for confirmation
- [ ] **Which fields?** Only change the fields the user requested

### Before `delete_task`
- [ ] **Always ask for explicit confirmation** — "Should I permanently delete task '[Title]' on board '[Board]'? This cannot be undone."

### Before `create_document`
- [ ] **Clarify format**: markdown, text, or html
- [ ] **Link**: Attach to which task (or standalone)?

---

## Guardrails

### No Hallucination
- Use **only real data** from MCP tool responses. Never fabricate task IDs, board names, or content.
- If a tool call fails or returns empty data: inform the user, do not improvise.
- When in doubt, show the actual results and ask.

### No Sensitive Data
- Do not store passwords, API keys, tokens, or personal data in task titles or descriptions.
- If the user mentions sensitive information, warn them: "This may contain sensitive data — should I really store it in Todokan?"

### Source Attribution
- When storing content from external research (web, files, other tools) in Todokan, note the source in the task description or document:
  ```
  Source: [URL or filename]
  Created by: Agent on [date]
  ```

### Scope Awareness
- **Worker endpoint** (`/mcp-worker`): Read-only + comments (`add_comment`). No task/board CUD, no document creation.
- **Planner endpoint** (`/mcp`): Full access. Still ask before destructive actions.
- On scope errors: explain to the user that the current endpoint does not have the required permissions.

### Idempotency
- On network errors: do not blindly retry the same action. First check whether the action was already performed (`list_tasks`).

---

## Output Format

### Briefing (summary of existing tasks)

```markdown
## Briefing: [Board Name] — [Date]

**Open (todo):** X tasks
**In progress (doing):** Y tasks
**Completed (done):** Z tasks

### Urgent (high priority)
- [ ] [Task Title] — due [Date]
- [ ] [Task Title] — due [Date]

### In Progress
- [~] [Task Title] — since [Date]

### Next Steps
[1-2 sentences recommendation based on the data]
```

### Draft (preview before task creation)

```markdown
## Task Draft

| Field       | Value                         |
|-------------|-------------------------------|
| Board       | [Board Name]                  |
| Title       | [Title, max 80 chars]         |
| Description | [Description, max 500 chars]  |
| Status      | todo                          |
| Priority    | [low / normal / high]         |
| Due         | [YYYY-MM-DD or —]             |
| Labels      | [label1, label2]              |

Should I create this task?
```

### Document Draft

```markdown
## Document Draft

**Title:** [Title]
**Format:** markdown
**Linked to:** [Task Title] on [Board Name]

---
[Document content]
---

Should I create this document?
```

---

## Data Model

```
Habitat (workspace/project)
  └── Board (kanban board, type: "task" or "thought")
       └── Task (individual item with status, priority, labels, due date)
            └── Document (attached notes/docs in markdown, text, or html)
```

- **Habitats** group boards. A user can have multiple habitats.
- **Boards** are kanban boards. Type `task` for actionable items, `thought` for ideas/notes.
- **Tasks** live on a board and move through status columns.
- **Documents** are rich text attached to tasks.

## Status Values

| Status | Meaning |
|--------|---------|
| `todo` | Not started |
| `doing` | In progress |
| `done` | Completed |

## Priority Values

| Priority | Meaning |
|----------|---------|
| `low` | Low priority |
| `normal` | Default priority |
| `high` | High/urgent priority |

## Available MCP Tools

### Reading Data
- `list_habitats` — List all workspaces
- `list_boards` — List all boards (returns id, name, version)
- `list_tasks` — List tasks with filters: `boardId`, `status`, `label`/`labels`, `limit`, `cursor`
- `search_across_habitats` — Full-text search over habitats/boards/tasks in one call
- `get_events_since` — Unified feed since timestamp (task events + comments + documents)
- `list_board_labels` — Get unique labels on a board with usage counts
- `list_task_documents` — Get documents attached to a task
- `read_document` — Read a document's content
- `list_task_comments` — List comments on a task

### Creating & Modifying (Planner endpoint only)
- `create_habitat` — Create a new workspace (`name`)
- `create_board` — Create a new board (`name`, optional `habitatId`, `boardType`)
- `create_task` — Create a task (`title`, `boardId` or `boardName`, optional `description`, `dueDate`, `priority`, `labels`)
- `update_task` — Update a task by ID (`taskId`, plus fields to change)
- `update_task_by_title` — Update a task by exact title match (`titleExact`, `boardId` or `boardName`)
- `delete_task` — Permanently delete a task (`taskId`)
- `create_document` — Create a document (optional `relatedTaskId` to attach)
- `add_document_to_task` — Attach a new document to a task
- `add_comment` — Add a comment to a task

### AI-Assisted Creation
- `propose_task_variants` — Generate 2-3 task variants (short/standard/detailed) from a rough description
- `confirm_task_fields` — Preview a variant's fields before creating it

## AI Visibility Gate

By default, the MCP server only returns tasks where `aiEnabled: true`. Tasks with `aiEnabled: false` are invisible to MCP agents — they will not appear in `list_tasks`, `search_across_habitats`, `get_events_since`, or `get_task`.

Users control this via a **"Send to AI"** button on each task card. When clicked, it sets `aiEnabled: true`, `assignee: 'ai'`, and `status: 'doing'`.

- To see only AI-assigned tasks: `list_tasks { "assignee": "ai" }`
- To see all AI-enabled tasks: `list_tasks {}` (default — only AI-enabled tasks are returned)
- To explicitly include non-AI tasks: `list_tasks { "aiEnabled": false }` (override, useful for reporting)

## OAuth & Authentication

- **OAuth 2.1 with PKCE** (RS256 JWT)
- **Token lifetime:** 30 days, no refresh token
- **Planner** (`/mcp`): Full CRUD access — all scopes
- **Worker** (`/mcp-worker`): `boards:read`, `tasks:read`, `labels:read`, `docs:read`, `comments:read`, `comments:write`
- **No rate limiting** — still be conservative with calls
- **Activity logging**: Every tool call is logged server-side

## Common Workflows

### List all tasks on a board
1. `list_boards` to find the board ID
2. `list_tasks` with `boardId` to get tasks

### Create a task
```
create_task { "title": "Review PR #42", "boardName": "Development", "priority": "high", "dueDate": "2026-03-01" }
```

### Move a task to done
```
update_task { "taskId": "<uuid>", "status": "done" }
```

### Add labels to a task
```
update_task { "taskId": "<uuid>", "labels": ["bug", "frontend"] }
```

### Find tasks by label
```
list_tasks { "boardId": "<uuid>", "labels": ["bug"] }
```

### Search across all habitats
```
search_across_habitats { "query": "investor meeting", "limit": 20 }
```

### Poll event feed (agent loop)
```
get_events_since { "since": "2026-02-24T08:00:00Z", "limit": 200 }
```

## Tips

- Always call `list_boards` first to discover available board IDs — don't guess UUIDs.
- Use `boardName` instead of `boardId` when the user refers to boards by name.
- Due dates use `YYYY-MM-DD` format.
- Task titles are max 80 characters, descriptions max 500 characters.
- Labels are free-form strings (max 10 per task).
- The `update_task` tool requires the task's UUID. Use `list_tasks` to find it, or `update_task_by_title` if you only know the title.
