---
name: google-tasks
description: Manage Google Tasks via gog CLI or Google Tasks API.
metadata:
  {
    "openclaw":
      {
        "emoji": "📋",
        "requires": { "anyBins": ["gog", "curl"] },
      },
  }
---

# google-tasks

Manage Google Tasks for creating, listing, completing, and organizing tasks.
Supports two backends: `gog` CLI (recommended) or direct API via `curl`.

## Option A: Using gog CLI (Recommended)

If you have `gog` installed and configured (`gog auth add`), use the `gog tasks` subcommands.

### Setup

```bash
# If gog is already configured for Gmail/Calendar, add Tasks scope:
gog auth add you@gmail.com --services tasks
export GOG_ACCOUNT=you@gmail.com
```

### List task lists

```bash
gog tasks list --json
```

### List tasks

```bash
gog tasks get <tasklistId> --json
```

Show only incomplete tasks:

```bash
gog tasks get <tasklistId> --json --show-completed=false
```

### Create a task

```bash
gog tasks create <tasklistId> --title "Buy groceries"
```

With due date and notes:

```bash
gog tasks create <tasklistId> --title "Review PR" --notes "Check auth changes" --due "2026-02-15T00:00:00Z"
```

### Complete a task

```bash
gog tasks done <tasklistId> <taskId>
```

### Uncomplete a task

```bash
gog tasks undo <tasklistId> <taskId>
```

### Update a task

```bash
gog tasks update <tasklistId> <taskId> --title "Updated title"
```

### Delete a task

```bash
gog tasks delete <tasklistId> <taskId>
```

### Clear completed tasks

```bash
gog tasks clear <tasklistId>
```

## Option B: Using curl + Google Tasks API

For environments without `gog`, use the REST API directly.

### Setup (one-time)

1. Create a project in [Google Cloud Console](https://console.cloud.google.com)
2. Enable the **Google Tasks API**
3. Create **OAuth 2.0 Client ID** (Desktop application)
4. Download `client_secret.json`, note the `client_id` and `client_secret`

### Authenticate

Open in browser:

```
https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8080&response_type=code&scope=https://www.googleapis.com/auth/tasks&access_type=offline
```

After authorization, exchange the code for tokens:

```bash
curl -s -X POST https://oauth2.googleapis.com/token \
  -d "client_id=$GTASKS_CLIENT_ID" \
  -d "client_secret=$GTASKS_CLIENT_SECRET" \
  -d "code=AUTHORIZATION_CODE" \
  -d "redirect_uri=http://localhost:8080" \
  -d "grant_type=authorization_code" | jq .
```

Save the `refresh_token`. Refresh access tokens as needed:

```bash
ACCESS_TOKEN=$(curl -s -X POST https://oauth2.googleapis.com/token \
  -d "client_id=$GTASKS_CLIENT_ID" \
  -d "client_secret=$GTASKS_CLIENT_SECRET" \
  -d "refresh_token=$GTASKS_REFRESH_TOKEN" \
  -d "grant_type=refresh_token" | jq -r '.access_token')
```

### List task lists

```bash
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  "https://tasks.googleapis.com/tasks/v1/users/@me/lists" \
  | jq '.items[] | {id, title}'
```

### List tasks

```bash
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  "https://tasks.googleapis.com/tasks/v1/lists/$LIST_ID/tasks" \
  | jq '.items[] | {id, title, status, due, notes}'
```

Show only incomplete tasks:

```bash
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  "https://tasks.googleapis.com/tasks/v1/lists/$LIST_ID/tasks?showCompleted=false" \
  | jq '.items[] | {id, title, due}'
```

### Create a task

```bash
curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "notes": "Milk, eggs, bread", "due": "2026-02-15T00:00:00.000Z"}' \
  "https://tasks.googleapis.com/tasks/v1/lists/$LIST_ID/tasks" \
  | jq '{id, title, status}'
```

### Complete a task

```bash
curl -s -X PATCH \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}' \
  "https://tasks.googleapis.com/tasks/v1/lists/$LIST_ID/tasks/$TASK_ID" \
  | jq '{id, title, status}'
```

### Update a task

```bash
curl -s -X PATCH \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated title", "notes": "Updated notes"}' \
  "https://tasks.googleapis.com/tasks/v1/lists/$LIST_ID/tasks/$TASK_ID" \
  | jq '{id, title}'
```

### Delete a task

```bash
curl -s -X DELETE \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  "https://tasks.googleapis.com/tasks/v1/lists/$LIST_ID/tasks/$TASK_ID"
# Returns 204 No Content on success
```

### Clear completed tasks

```bash
curl -s -X POST \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  "https://tasks.googleapis.com/tasks/v1/lists/$LIST_ID/clear"
```

## Task Properties

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Task title (required for create) |
| `notes` | string | Additional details |
| `status` | string | `needsAction` or `completed` |
| `due` | string | RFC 3339 timestamp (e.g., `2026-02-15T00:00:00.000Z`) |
| `completed` | string | Completion date (auto-set when status = completed) |
| `parent` | string | Parent task ID (for subtasks) |
| `position` | string | Position among siblings |

## Notes

- Google Tasks uses only two statuses: `needsAction` and `completed`.
- The default task list ID can be retrieved by listing all task lists — it's usually named "My Tasks" or the first entry.
- `gog` CLI is recommended when available — it handles OAuth automatically and supports `--json` output.
- The curl approach works on any platform with `curl` and `jq`.
- Google Tasks API has a generous free quota (50,000 queries/day).
- Subtasks are supported via the `parent` field when creating tasks.
