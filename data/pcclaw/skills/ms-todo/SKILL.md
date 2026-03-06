---
name: ms-todo
description: Manage Microsoft To Do tasks via Microsoft Graph API.
metadata:
  {
    "openclaw":
      {
        "emoji": "✅",
        "requires": { "bins": ["curl"], "env": ["MS_TODO_CLIENT_ID", "MS_TODO_REFRESH_TOKEN"] },
        "primaryEnv": "MS_TODO_REFRESH_TOKEN",
      },
  }
---

# ms-todo

Manage Microsoft To Do tasks using the Microsoft Graph API. Works on all platforms.

## Setup (one-time)

### 1. Register an Azure App

1. Go to [Azure Portal > App registrations](https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)
2. Click **New registration**
3. Name: `OpenClaw Todo`
4. Supported account types: **Personal Microsoft accounts only**
5. Redirect URI: leave blank
6. After creation → **Authentication** → **Advanced settings** → Set **Allow public client flows** to **Yes**
7. Go to **API permissions** → Add permission → Microsoft Graph → Delegated → `Tasks.ReadWrite` and `offline_access`
8. Copy the **Application (client) ID**

### 2. Authenticate via Device Code Flow

Request a device code:

```bash
curl -s -X POST "https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode" \
  -d "client_id=$MS_TODO_CLIENT_ID&scope=Tasks.ReadWrite offline_access"
```

The response will show a `user_code` and `verification_uri`. Open the URL in a browser, enter the code, and sign in.

Then poll for the token:

```bash
curl -s -X POST "https://login.microsoftonline.com/consumers/oauth2/v2.0/token" \
  -d "client_id=$MS_TODO_CLIENT_ID&device_code=DEVICE_CODE_HERE&grant_type=urn:ietf:params:oauth:grant-type:device_code"
```

Save the `refresh_token` from the response as `MS_TODO_REFRESH_TOKEN`.

### 3. Configure OpenClaw

Add to `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      "ms-todo": {
        env: {
          MS_TODO_CLIENT_ID: "your-azure-app-client-id",
          MS_TODO_REFRESH_TOKEN: "your-refresh-token",
        },
      },
    },
  },
}
```

## Getting an Access Token

Tokens expire after ~1 hour. Refresh before each session:

```bash
ACCESS_TOKEN=$(curl -s -X POST "https://login.microsoftonline.com/consumers/oauth2/v2.0/token" \
  -d "client_id=$MS_TODO_CLIENT_ID&refresh_token=$MS_TODO_REFRESH_TOKEN&grant_type=refresh_token&scope=Tasks.ReadWrite offline_access" \
  | jq -r '.access_token')
```

Use `$ACCESS_TOKEN` in the Authorization header for all commands below.

## Commands

### List all task lists

```bash
curl -s "https://graph.microsoft.com/v1.0/me/todo/lists" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.value[] | {id, displayName}'
```

### List tasks in a list

```bash
curl -s "https://graph.microsoft.com/v1.0/me/todo/lists/$LIST_ID/tasks" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  | jq '.value[] | {id, title, status, importance, dueDateTime}'
```

Filter incomplete tasks:

```bash
curl -s "https://graph.microsoft.com/v1.0/me/todo/lists/$LIST_ID/tasks?\$filter=status ne 'completed'" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  | jq '.value[] | {id, title, status, importance, dueDateTime}'
```

### Create a task

```bash
curl -s -X POST "https://graph.microsoft.com/v1.0/me/todo/lists/$LIST_ID/tasks" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Review PR #42",
    "importance": "high",
    "dueDateTime": {
      "dateTime": "2026-02-15T00:00:00",
      "timeZone": "Asia/Taipei"
    },
    "body": {
      "content": "Check auth module changes",
      "contentType": "text"
    }
  }' | jq '{id, title, status}'
```

Minimal create (title only):

```bash
curl -s -X POST "https://graph.microsoft.com/v1.0/me/todo/lists/$LIST_ID/tasks" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Quick task"}' | jq '{id, title}'
```

### Complete a task

```bash
curl -s -X PATCH "https://graph.microsoft.com/v1.0/me/todo/lists/$LIST_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}' | jq '{id, title, status}'
```

### Update a task

```bash
curl -s -X PATCH "https://graph.microsoft.com/v1.0/me/todo/lists/$LIST_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated title",
    "importance": "high"
  }' | jq '{id, title, importance}'
```

### Delete a task

```bash
curl -s -X DELETE "https://graph.microsoft.com/v1.0/me/todo/lists/$LIST_ID/tasks/$TASK_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
# Returns 204 No Content on success
```

## Task Properties

| Field | Type | Values |
|-------|------|--------|
| `title` | string | Required for create |
| `status` | string | `notStarted`, `inProgress`, `completed`, `waitingOnOthers`, `deferred` |
| `importance` | string | `low`, `normal`, `high` |
| `body.content` | string | Task notes/details |
| `body.contentType` | string | `text` or `html` |
| `dueDateTime.dateTime` | string | ISO 8601 (e.g., `2026-02-15T00:00:00`) |
| `dueDateTime.timeZone` | string | IANA timezone (e.g., `Asia/Taipei`, `UTC`) |
| `isReminderOn` | boolean | Enable/disable reminder |
| `reminderDateTime` | object | Same format as `dueDateTime` |

## Notes

- Microsoft Graph To Do API only supports **delegated** (user) auth — no app-only/service accounts.
- Use `offline_access` scope to get a refresh token that works indefinitely.
- The default task list (called "Tasks") always exists for every user.
- `$LIST_ID` can be found from the "List all task lists" command.
- Pipe through `jq` for readable output; omit `jq` if not installed.
- Works from WSL, macOS, Linux — anywhere `curl` is available.
