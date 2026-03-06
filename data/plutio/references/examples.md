# Plutio Integration Examples

These examples show common workflows with the Plutio skill.

**Note:** These examples use bash syntax. For **PowerShell 7** examples, see [powershell-workflows.md](powershell-workflows.md).

To convert bash examples to PowerShell:
- Replace `\` line continuations with `` ` ``
- Replace `~/` with `$env:USERPROFILE\`
- Replace `$(command)` with `$(command)` (same in PowerShell)
- Use `ConvertFrom-Json` for JSON output

## Setup & Authentication

Store credentials securely in Bitwarden or your password manager. The CLI will cache the access token locally (~1 hour).

```bash
export PLUTIO_SUBDOMAIN="grewing"
export PLUTIO_APP_KEY="your_app_key_here"
export PLUTIO_SECRET="your_secret_here"

# Or use inline in each command:
python3 plutio-cli.py list-projects \
  --subdomain $PLUTIO_SUBDOMAIN \
  --app-key $PLUTIO_APP_KEY \
  --secret $PLUTIO_SECRET
```

## Workflow 1: Check Today's Tasks

List all open tasks due today:

```bash
#!/bin/bash
# Get today's date
TODAY=$(date +%Y-%m-%d)

# List projects first
python3 plutio-cli.py list-projects \
  --subdomain grewing \
  --app-key $PLUTIO_APP_KEY \
  --secret $PLUTIO_SECRET | grep "ID:"

# For each project, list tasks
python3 plutio-cli.py list-tasks \
  --project-id "project_id_here" \
  --subdomain grewing \
  --app-key $PLUTIO_APP_KEY \
  --secret $PLUTIO_SECRET \
  --status open
```

## Workflow 2: Create a New Task from Calendar Event

When a calendar event is created, automatically add a task to Plutio:

```bash
#!/bin/bash
# Parse calendar event details
PROJECT_ID="your_project_id"
TASK_TITLE="Calendar: Meeting with Client"
TASK_DUE="2026-03-15"
TASK_PRIORITY="high"

python3 plutio-cli.py create-task \
  --project-id "$PROJECT_ID" \
  --title "$TASK_TITLE" \
  --due-date "$TASK_DUE" \
  --priority "$TASK_PRIORITY" \
  --status "open" \
  --subdomain grewing \
  --app-key $PLUTIO_APP_KEY \
  --secret $PLUTIO_SECRET
```

## Workflow 3: Complete All Tasks in a Sprint

Mark multiple tasks as closed:

```bash
#!/bin/bash
PROJECT_ID="your_project_id"

# Get all open tasks
TASKS=$(python3 plutio-cli.py list-tasks \
  --project-id "$PROJECT_ID" \
  --subdomain grewing \
  --app-key $PLUTIO_APP_KEY \
  --secret $PLUTIO_SECRET \
  --json | jq -r '.[] | select(.priority=="high") | ._id')

# Close each task
for TASK_ID in $TASKS; do
  python3 plutio-cli.py update-task \
    --task-id "$TASK_ID" \
    --status "closed" \
    --subdomain grewing \
    --app-key $PLUTIO_APP_KEY \
    --secret $PLUTIO_SECRET
done
```

## Workflow 4: Assign Task to Person

Find a person by name, then assign a task to them:

```bash
#!/bin/bash
PROJECT_ID="your_project_id"
TASK_ID="your_task_id"
PERSON_NAME="John Doe"

# List people to find ID
PERSON_ID=$(python3 plutio-cli.py list-people \
  --subdomain grewing \
  --app-key $PLUTIO_APP_KEY \
  --secret $PLUTIO_SECRET \
  --json | jq -r ".[] | select(.name.first==\"John\") | ._id" | head -1)

# Assign task
python3 plutio-cli.py update-task \
  --task-id "$TASK_ID" \
  --assignee-id "$PERSON_ID" \
  --subdomain grewing \
  --app-key $PLUTIO_APP_KEY \
  --secret $PLUTIO_SECRET
```

## Workflow 5: OpenClaw Integration (Matrix Notification)

In OpenClaw, create a Python script that:
1. Queries Plutio for tasks
2. Sends Matrix notification for high-priority items

```python
#!/usr/bin/env python3
import subprocess
import json
from message import send_message

# Get high-priority tasks
result = subprocess.run([
    "python3", "/home/mirko/.openclaw/workspace/skills/plutio/scripts/plutio-cli.py",
    "list-tasks",
    "--project-id", "project_id",
    "--subdomain", "grewing",
    "--app-key", os.getenv("PLUTIO_APP_KEY"),
    "--secret", os.getenv("PLUTIO_SECRET"),
    "--json"
], capture_output=True, text=True)

tasks = json.loads(result.stdout)
high_priority = [t for t in tasks if t.get("priority") == "high"]

if high_priority:
    msg = "🔴 **High Priority Tasks:**\n"
    for t in high_priority:
        msg += f"• {t['title']}\n"
    
    send_message(
        to="@mirko:matrix.org",
        message=msg,
        channel="matrix"
    )
```

**For PowerShell users:** See [powershell-workflows.md](powershell-workflows.md) for an equivalent PowerShell implementation.

## Workflow 6: Bulk Update Task Fields

Update multiple tasks with new custom field values:

```bash
#!/bin/bash
PROJECT_ID="your_project_id"
CUSTOM_FIELDS='{"status_custom":"in_progress","reviewed":true}'

# Get all open tasks
TASKS=$(python3 plutio-cli.py list-tasks \
  --project-id "$PROJECT_ID" \
  --subdomain grewing \
  --app-key $PLUTIO_APP_KEY \
  --secret $PLUTIO_SECRET \
  --json | jq -r '.[].\_id')

# Update each
for TASK_ID in $TASKS; do
  python3 plutio-cli.py update-task \
    --task-id "$TASK_ID" \
    --custom-fields "$CUSTOM_FIELDS" \
    --subdomain grewing \
    --app-key $PLUTIO_APP_KEY \
    --secret $PLUTIO_SECRET
done
```

## Workflow 7: Query Tasks by Custom Filters

Get all tasks assigned to you with due date in next 7 days:

```bash
#!/bin/bash
PROJECT_ID="your_project_id"
MY_PERSON_ID="your_person_id"

# List tasks, filter with jq
python3 plutio-cli.py list-tasks \
  --project-id "$PROJECT_ID" \
  --subdomain grewing \
  --app-key $PLUTIO_APP_KEY \
  --secret $PLUTIO_SECRET \
  --json | jq -r ".[] | 
    select(.assigneeId==\"$MY_PERSON_ID\") | 
    select(.dueDate != null) |
    \"\(.title) - Due: \(.dueDate[:10])\""
```

## Error Handling

### Common Errors

**401 Unauthorized**
- Check app key and secret are correct
- Token may have expired; the CLI will automatically refresh

**404 Not Found**
- Project ID or task ID doesn't exist
- Use `list-projects` or `list-tasks` to verify IDs

**400 Bad Request**
- Invalid field value (e.g., wrong status name)
- Check API reference for valid values

**429 Rate Limited**
- Hit Plutio's 1000 calls/hour limit
- Wait a few minutes before retrying

### Debugging

Add `--json` flag to see raw API responses:

```bash
python3 plutio-cli.py list-tasks \
  --project-id ID \
  --subdomain grewing \
  --app-key KEY \
  --secret SECRET \
  --json  # See full response structure
```

---

*Last updated: 2026-03-01*
