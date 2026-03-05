---
name: jules
description: Create and manage Google Jules AI coding sessions via the Jules REST API. Start tasks, monitor progress, approve plans, send messages, list sources/repos, and retrieve session activities/artifacts.
metadata: {"openclaw":{"requires":{"env":["JULES_API_KEY"],"bins":["curl"]},"primaryEnv":"JULES_API_KEY","emoji":"🤖","homepage":"https://jules.google/docs/api/reference/"}}
---

# Jules API Skill

Interact with the [Google Jules](https://jules.google) AI coding agent via its REST API. Jules can autonomously execute coding tasks on your GitHub repositories — writing code, fixing bugs, adding tests, and creating pull requests.

**Base URL:** `https://jules.googleapis.com/v1alpha`
**Auth:** Pass your API key via the `x-goog-api-key` header. Get one at [jules.google.com/settings](https://jules.google.com/settings).

---

## List Sources (Connected Repositories)

Discover which GitHub repos are connected to your Jules account:

```bash
curl -s -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sources?pageSize=30"
```

With pagination:

```bash
curl -s -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sources?pageSize=10&pageToken=PAGE_TOKEN"
```

Filter specific sources:

```bash
curl -s -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sources?filter=name%3Dsources%2Fgithub-owner-repo"
```

## Get a Source

Get details and branches for a specific repo:

```bash
curl -s -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sources/SOURCE_ID"
```

Example: `sources/github-myorg-myrepo` — replace with your actual source ID from List Sources.

---

## Create a Session (Start a Coding Task)

Create a new Jules session to execute a coding task on a repo:

```bash
curl -s -X POST \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "TASK_DESCRIPTION",
    "title": "OPTIONAL_TITLE",
    "sourceContext": {
      "source": "sources/github-OWNER-REPO",
      "githubRepoContext": {
        "startingBranch": "main"
      }
    },
    "requirePlanApproval": true
  }' \
  "https://jules.googleapis.com/v1alpha/sessions"
```

### Parameters

| Parameter | Required | Description |
|---|---|---|
| `prompt` | Yes | The task description for Jules to execute |
| `title` | No | Optional title (auto-generated if omitted) |
| `sourceContext.source` | Yes | Source resource name (e.g. `sources/github-owner-repo`) |
| `sourceContext.githubRepoContext.startingBranch` | Yes | Branch to start from (e.g. `main`, `develop`) |
| `requirePlanApproval` | No | If `true`, plans need explicit approval before execution |
| `automationMode` | No | Set to `AUTO_CREATE_PR` to auto-create PRs when done |

### Auto-approve + Auto-PR example

```bash
curl -s -X POST \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Add comprehensive unit tests for the auth module",
    "sourceContext": {
      "source": "sources/github-myorg-myrepo",
      "githubRepoContext": { "startingBranch": "main" }
    },
    "automationMode": "AUTO_CREATE_PR"
  }' \
  "https://jules.googleapis.com/v1alpha/sessions"
```

---

## List Sessions

List all your Jules sessions:

```bash
curl -s -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions?pageSize=10"
```

Paginate with `pageToken`:

```bash
curl -s -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions?pageSize=10&pageToken=NEXT_PAGE_TOKEN"
```

## Get a Session

Retrieve a single session by ID (includes outputs like PRs if completed):

```bash
curl -s -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID"
```

### Session States

| State | Meaning |
|---|---|
| `QUEUED` | Waiting to be processed |
| `PLANNING` | Jules is analyzing and creating a plan |
| `AWAITING_PLAN_APPROVAL` | Plan ready, waiting for user approval |
| `AWAITING_USER_FEEDBACK` | Jules needs additional input |
| `IN_PROGRESS` | Jules is actively working |
| `PAUSED` | Session is paused |
| `COMPLETED` | Task completed successfully |
| `FAILED` | Task failed to complete |

---

## Approve a Plan

When a session is in `AWAITING_PLAN_APPROVAL` state, approve the plan:

```bash
curl -s -X POST \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{}' \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID:approvePlan"
```

## Send a Message

Send feedback, answer questions, or give additional instructions to an active session:

```bash
curl -s -X POST \
  -H "x-goog-api-key: $JULES_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "YOUR_MESSAGE_HERE"
  }' \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID:sendMessage"
```

Use this when session state is `AWAITING_USER_FEEDBACK` or to provide additional guidance during `IN_PROGRESS`.

---

## List Activities (Monitor Progress)

Get all events/progress for a session:

```bash
curl -s -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID/activities?pageSize=50"
```

Get activities after a specific timestamp (for polling):

```bash
curl -s -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID/activities?createTime=2026-01-17T00:03:53Z"
```

### Activity Types

Activities will contain exactly one of these event fields:

| Event | Description |
|---|---|
| `planGenerated` | Jules created a plan (contains `plan.steps[]`) |
| `planApproved` | A plan was approved |
| `userMessaged` | User sent a message |
| `agentMessaged` | Jules sent a message |
| `progressUpdated` | Status update during execution |
| `sessionCompleted` | Session finished successfully |
| `sessionFailed` | Session encountered an error (contains `reason`) |

### Artifacts

Activities may include artifacts:

- **ChangeSet**: Code changes with `gitPatch` (unified diff, base commit, suggested commit message)
- **BashOutput**: Command output with `command`, `output`, `exitCode`
- **Media**: Binary output with `mimeType` and base64 `data`

## Get a Single Activity

```bash
curl -s -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID/activities/ACTIVITY_ID"
```

---

## Delete a Session

```bash
curl -s -X DELETE \
  -H "x-goog-api-key: $JULES_API_KEY" \
  "https://jules.googleapis.com/v1alpha/sessions/SESSION_ID"
```

---

## Typical Workflow

1. **List sources** to find the repo resource name
2. **Create a session** with a prompt describing the task
3. **Poll the session** (Get Session) to track state changes
4. **List activities** to monitor progress and read Jules' messages
5. If `requirePlanApproval` was set, **approve the plan** when state is `AWAITING_PLAN_APPROVAL`
6. If state is `AWAITING_USER_FEEDBACK`, **send a message** with your response
7. When `COMPLETED`, **get the session** to find the output PR URL

## Error Handling

| Code | Meaning |
|---|---|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 401 | Unauthorized (invalid/missing API key) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not found |
| 429 | Rate limited |
| 500 | Server error |

Error responses return:

```json
{
  "error": {
    "code": 400,
    "message": "Invalid session ID format",
    "status": "INVALID_ARGUMENT"
  }
}
```

## Notes

- Get your API key from [jules.google.com/settings](https://jules.google.com/settings)
- Store it as the `JULES_API_KEY` environment variable
- Sources (repos) are connected via the Jules web UI at [jules.google](https://jules.google) — the API is read-only for sources
- Session resource names follow the pattern `sessions/{sessionId}`
- Activity resource names follow `sessions/{sessionId}/activities/{activityId}`
- All list endpoints support `pageSize` (1-100) and `pageToken` for pagination
