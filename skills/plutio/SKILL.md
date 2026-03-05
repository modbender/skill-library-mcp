---
name: plutio
description: Manage Plutio projects and tasks. Use when you need to create, update, close, or query tasks and projects in Plutio (task/project management platform). Supports listing projects, viewing tasks, creating tasks with full field support, updating task details (status, description, assignee, priority, dates), and closing tasks.
---

# Plutio Skill

Integrate with [Plutio](https://plutio.com/) for project and task management via REST API.

**Platforms**: Works with Linux/macOS (bash) and Windows (PowerShell 7). See [references/powershell-workflows.md](references/powershell-workflows.md) for PowerShell-specific examples.

## Setup

**Complete setup guide**: See [references/setup-guide.md](references/setup-guide.md) for:
- How to get API credentials from Plutio
- Configuring via OpenClaw chat (recommended)
- Command-line setup for Linux, macOS, and Windows
- Secure credential storage (Bitwarden, environment variables)
- Troubleshooting common issues

**Quick summary**:

1. **Get credentials** from Plutio (Settings > API > Create Application)
2. **Ask OpenClaw to configure** (easiest): _"Setup Plutio with Client ID: XXX and Secret: YYY"_
3. **Or set environment variables**:
   - Linux/macOS: `export PLUTIO_APP_KEY="..."`
   - Windows PowerShell: `$env:PLUTIO_APP_KEY = "..."`
4. **Python 3** must be installed

The skill caches access tokens locally (valid for ~1 hour), then automatically refreshes when needed.

## Quick Start

### List all projects
```powershell
python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py `
  --subdomain grewing `
  --app-key YOUR_APP_KEY `
  --secret YOUR_SECRET `
  list-projects
```

### List tasks in a project
```powershell
python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py `
  --subdomain grewing `
  --app-key YOUR_APP_KEY `
  --secret YOUR_SECRET `
  list-tasks --project-id PROJECT_ID
```

### Create a task
```powershell
python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py `
  --subdomain grewing `
  --app-key YOUR_APP_KEY `
  --secret YOUR_SECRET `
  create-task `
    --title "My Task Title" `
    --board-id BOARD_ID `
    --group-id GROUP_ID
```

**Note**: To make tasks appear in the Plutio UI, you **must** provide both `--board-id` (Task List board ID) and `--group-id` (column/group ID like Backlog, In Progress, Done).

### List people (team members)
```powershell
python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py `
  --subdomain grewing `
  --app-key YOUR_APP_KEY `
  --secret YOUR_SECRET `
  list-people
```

## Common Operations

### Create a task with all fields
```powershell
python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py create-task `
  --subdomain grewing `
  --project-id PROJECT_ID `
  --title "Task Title" `
  --description "Detailed description" `
  --priority "high" `
  --status "open" `
  --assignee-id PERSON_ID `
  --due-date "2026-03-15" `
  --app-key YOUR_APP_KEY `
  --secret YOUR_SECRET
```

Supported fields when creating/updating tasks:
- `title` - Task name
- `description` - Task details
- `status` - `open`, `in_progress`, `closed`, or custom status name
- `priority` - `low`, `medium`, `high`, `urgent`
- `assignee-id` - Person ID to assign task to
- `due-date` - ISO format (YYYY-MM-DD)
- `label-ids` - Comma-separated label IDs
- `custom-fields` - JSON string with custom field values

### Close a task
```powershell
python3 $env:USERPROFILE\.openclaw\workspace\skills\plutio\scripts\plutio-cli.py update-task `
  --subdomain grewing `
  --task-id TASK_ID `
  --status "closed" `
  --app-key YOUR_APP_KEY `
  --secret YOUR_SECRET
```

## API Reference

See [references/api-endpoints.md](references/api-endpoints.md) for:
- Full endpoint documentation
- Response schemas
- Field descriptions
- Rate limits and pagination

## How It Works

1. **Authentication**: Exchanges app key + secret for temporary access token
2. **API Calls**: Uses token for authenticated requests to Plutio REST API
3. **Token Caching**: Stores token locally for faster subsequent calls
4. **Error Handling**: Reports API errors clearly with troubleshooting hints

## Important Notes on Plutio v1.11 API

**Supported Operations:**
- ✅ List projects
- ✅ List tasks (all tasks in workspace or by board)
- ✅ Create tasks (with board and group IDs)
- ✅ List people/team members

**Key Requirements for v1.11:**
- **Tasks need both `taskBoardId` AND `taskGroupId`** to appear in the Plutio UI
- Tasks without these parameters are created but remain hidden from the interface
- Get your board and group IDs from the Plutio project's Task List

**Known Limitations (v1.11):**
- `projectId` parameter doesn't work - use `taskBoardId` instead
- Task creation supports: title, board ID, group ID only
- Other fields (status, priority, description) are not supported in the create endpoint
- Task updates via API have permission restrictions (use Plutio UI)
- To add details to tasks, edit them directly in Plutio UI
- Contact Plutio support for advanced field support

## Troubleshooting

**"Unauthorized" error**: 
- Verify Client ID and Secret are copied exactly from Plutio Settings > API manager
- Check that the API application is created and visible in your API manager
- Ensure you're using v1.11 or later

**"Project not found"**: Verify project ID with `list-projects`

**"Rate limited"**: Plutio has 1000 calls/hour limit. Wait before retrying.

**Tasks not appearing in results**: Check the Plutio UI directly - the API may have caching delays.

## Integration Examples

### For PowerShell Users

Complete PowerShell 7 workflows and examples: See [references/powershell-workflows.md](references/powershell-workflows.md) for:
- Daily task briefings
- Batch task operations
- Integration with Windows Task Scheduler
- Error handling patterns

### For OpenClaw Integration

In OpenClaw, you could create a script that:
1. Checks calendar for upcoming deadline
2. Queries Plutio for tasks due that day
3. Sends reminder via Matrix

See the scripts/ folder and references/ for implementation examples.

---

*Last updated: 2026-03-01*
