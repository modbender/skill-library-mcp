# Taskline API Reference

## Authentication
All requests require the `X-API-Key` header with the user's API key.

## Task Statuses
- `not_started` - Task not yet begun
- `in_progress` - Currently being worked on
- `waiting` - Blocked or waiting for something
- `completed` - Finished
- `cancelled` - No longer needed

## Priority Values
Free-text field, but common values:
- `high`, `urgent`, `critical`
- `medium`, `normal`
- `low`

## Date Formats
- ISO 8601: `2026-02-20T15:30:00.000Z`
- Date only: `2026-02-20` (assumes start of day in user's timezone)
- Relative parsing should handle: "tomorrow", "friday", "next week", "in 3 days"

## Example API Calls

### Create Task
```bash
curl -X POST http://localhost:5173/api/v1/tasks \
  -H "X-API-Key: API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix authentication bug",
    "description": "User login failing on mobile devices",
    "status": "not_started",
    "priority": "high",
    "dueAt": "2026-02-20T17:00:00"
  }'
```

### List Tasks
```bash
# All tasks
curl -H "X-API-Key: API_KEY" http://localhost:5173/api/v1/tasks

# Filter by status
curl -H "X-API-Key: API_KEY" "http://localhost:5173/api/v1/tasks?status=in_progress"

# With pagination
curl -H "X-API-Key: API_KEY" "http://localhost:5173/api/v1/tasks?limit=10&offset=0"
```

### Update Task Status
```bash
curl -X PATCH http://localhost:5173/api/v1/tasks/TASK_ID \
  -H "X-API-Key: API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'
```

### Reports
```bash
# Summary report
curl -H "X-API-Key: API_KEY" http://localhost:5173/api/v1/reports/summary

# Overdue tasks
curl -H "X-API-Key: API_KEY" http://localhost:5173/api/v1/reports/overdue

# By project
curl -H "X-API-Key: API_KEY" http://localhost:5173/api/v1/reports/by-project
```

## Response Formats

### Task Object
```json
{
  "id": "uuid",
  "title": "Task title",
  "description": "Task description", 
  "status": "not_started",
  "priority": "high",
  "dueAt": "2026-02-20T17:00:00.000Z",
  "boardDate": null,
  "completedAt": null,
  "createdAt": "2026-02-16T10:00:00.000Z",
  "updatedAt": "2026-02-16T10:00:00.000Z",
  "accountablePerson": {
    "id": "uuid",
    "displayName": "Brett",
    "email": "brett@example.com"
  }
}
```

### Summary Report
```json
{
  "not_started": 5,
  "in_progress": 3, 
  "waiting": 1,
  "completed": 12,
  "cancelled": 0,
  "total": 21
}
```