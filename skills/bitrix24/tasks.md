# Tasks

## Basic Operations

```bash
# Create task
curl -s "${BITRIX24_WEBHOOK_URL}tasks.task.add.json" \
  -d 'fields[TITLE]=Task title&fields[DESCRIPTION]=Detailed description&fields[RESPONSIBLE_ID]=1&fields[DEADLINE]=2026-03-01T18:00:00&fields[PRIORITY]=2' | jq .result

# List tasks (my tasks by default)
curl -s "${BITRIX24_WEBHOOK_URL}tasks.task.list.json" \
  -d 'select[]=ID&select[]=TITLE&select[]=STATUS&select[]=DEADLINE&select[]=RESPONSIBLE_ID&select[]=PRIORITY' | jq .result

# Get task by ID
curl -s "${BITRIX24_WEBHOOK_URL}tasks.task.get.json" -d 'taskId=456' | jq '.result.task'

# Update task
curl -s "${BITRIX24_WEBHOOK_URL}tasks.task.update.json" \
  -d 'taskId=456&fields[TITLE]=Updated title&fields[DEADLINE]=2026-03-15T18:00:00' | jq .result

# Complete task
curl -s "${BITRIX24_WEBHOOK_URL}tasks.task.complete.json" -d 'taskId=456' | jq .result

# Reopen task
curl -s "${BITRIX24_WEBHOOK_URL}tasks.task.renew.json" -d 'taskId=456' | jq .result

# Delegate task
curl -s "${BITRIX24_WEBHOOK_URL}tasks.task.delegate.json" \
  -d 'taskId=456&userId=2' | jq .result

# Delete task
curl -s "${BITRIX24_WEBHOOK_URL}tasks.task.delete.json" -d 'taskId=456' | jq .result
```

## Filtering

```bash
# Tasks by status
curl -s "${BITRIX24_WEBHOOK_URL}tasks.task.list.json" \
  -d 'filter[STATUS]=3&select[]=ID&select[]=TITLE' | jq .result

# Tasks assigned to specific user
curl -s "${BITRIX24_WEBHOOK_URL}tasks.task.list.json" \
  -d 'filter[RESPONSIBLE_ID]=1&select[]=ID&select[]=TITLE&select[]=STATUS' | jq .result

# Tasks created by specific user
curl -s "${BITRIX24_WEBHOOK_URL}tasks.task.list.json" \
  -d 'filter[CREATED_BY]=1&select[]=ID&select[]=TITLE' | jq .result

# Overdue tasks
curl -s "${BITRIX24_WEBHOOK_URL}tasks.task.list.json" \
  -d 'filter[<DEADLINE]=2026-02-21T00:00:00&filter[!STATUS]=5&select[]=ID&select[]=TITLE&select[]=DEADLINE' | jq .result

# High priority tasks
curl -s "${BITRIX24_WEBHOOK_URL}tasks.task.list.json" \
  -d 'filter[PRIORITY]=2&select[]=ID&select[]=TITLE&select[]=PRIORITY' | jq .result
```

## Checklists

```bash
# Add checklist item
curl -s "${BITRIX24_WEBHOOK_URL}task.checklistitem.add.json" \
  -d 'TASKID=456&FIELDS[TITLE]=Subtask text' | jq .result

# List checklist items
curl -s "${BITRIX24_WEBHOOK_URL}task.checklistitem.getlist.json" \
  -d 'TASKID=456' | jq .result

# Complete checklist item
curl -s "${BITRIX24_WEBHOOK_URL}task.checklistitem.complete.json" \
  -d 'TASKID=456&ITEMID=789' | jq .result

# Delete checklist item
curl -s "${BITRIX24_WEBHOOK_URL}task.checklistitem.delete.json" \
  -d 'TASKID=456&ITEMID=789' | jq .result
```

## Comments

```bash
# Add comment to task
curl -s "${BITRIX24_WEBHOOK_URL}task.commentitem.add.json" \
  -d 'TASKID=456&FIELDS[POST_MESSAGE]=Comment text' | jq .result

# List comments
curl -s "${BITRIX24_WEBHOOK_URL}task.commentitem.getlist.json" \
  -d 'TASKID=456' | jq .result
```

## Planner

```bash
# Get tasks from "My Plan" for today
curl -s "${BITRIX24_WEBHOOK_URL}task.planner.getlist.json" | jq .result
```

## Reference

**Task statuses:**
| Status | ID |
|---|---|
| New (not viewed) | `1` |
| Waiting | `2` |
| In progress | `3` |
| Supposedly completed | `4` |
| Completed | `5` |
| Deferred | `6` |

**Priority:** `0` = Low, `1` = Medium (default), `2` = High.

**Key fields:** TITLE, DESCRIPTION, RESPONSIBLE_ID, CREATED_BY, DEADLINE, START_DATE_PLAN, END_DATE_PLAN, PRIORITY, STATUS, GROUP_ID (project), TAGS, TIME_ESTIMATE (seconds), ALLOW_TIME_TRACKING.

## More Methods (MCP)

This file covers common task methods. For additional methods or updated parameters, use MCP:
- `bitrix-search "task"` — find all task-related methods
- `bitrix-search "task checklist"` — find checklist methods
- `bitrix-method-details tasks.task.add` — get full spec for any method
