---
name: todoist-api-rest
description: Direct Todoist API integration via curl/jq. Lightweight, reliable, and uses working v1/v2 endpoints.
homepage: https://developer.todoist.com
metadata:
  clawdbot:
    emoji: "✅"
    requires:
      bins: ["curl", "jq"]
      env: ["TODOIST_API_TOKEN"]
---

# Todoist API (REST v2 & API v1)

This skill provides direct API access to Todoist. Use this when the CLI is unavailable or failing.

## Setup
Ensure `TODOIST_API_TOKEN` is set or use the token from `~/.openclaw/.secrets/todoist_token.json`.

## Core Commands (REST v2)

### List Active Tasks
```bash
curl -H "Authorization: Bearer $TODOIST_API_TOKEN" https://api.todoist.com/rest/v2/tasks | jq .
```
*Note: If rest/v2 returns 410, use `api/v1/tasks` (see below).*

### Create Task
```bash
curl -X POST -H "Authorization: Bearer $TODOIST_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"content": "New Task", "due_string": "today"}' \
     https://api.todoist.com/rest/v2/tasks
```

### Close (Complete) Task
```bash
curl -X POST -H "Authorization: Bearer $TODOIST_API_TOKEN" https://api.todoist.com/rest/v2/tasks/<task_id>/close
```

## Fallback / Legacy Commands (API v1)

Use these if REST v2 endpoints return `410 Gone`.

### List Tasks (v1)
```bash
curl -H "Authorization: Bearer $TODOIST_API_TOKEN" https://api.todoist.com/api/v1/tasks | jq .results
```

### Create Task (v1)
```bash
curl -X POST -H "Authorization: Bearer $TODOIST_API_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"content": "v1 Task", "project_id": "6g382hF2W96x2hvr"}' \
     https://api.todoist.com/api/v1/tasks
```

### Completed Tasks (v1)
```bash
curl -H "Authorization: Bearer $TODOIST_API_TOKEN" \
     "https://api.todoist.com/api/v1/tasks/completed/by_completion_date?since=2026-03-01T00:00:00Z&until=2026-03-04T23:59:59Z" | jq .items
```

## Projects & Sections

### List Projects
```bash
curl -H "Authorization: Bearer $TODOIST_API_TOKEN" https://api.todoist.com/rest/v2/projects
```

### List Sections
```bash
curl -H "Authorization: Bearer $TODOIST_API_TOKEN" "https://api.todoist.com/rest/v2/sections?project_id=<project_id>"
```
