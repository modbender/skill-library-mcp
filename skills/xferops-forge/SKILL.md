---
name: forge
description: Manage projects and tasks with the Forge project management API via MCP. Use when creating, updating, or searching tasks/tickets, managing projects and columns, or integrating with Forge/Kanban boards. Requires @xferops/forge-mcp and a Forge API token.
---

# Forge MCP

Project management via MCP (Model Context Protocol).

## Setup

Install the MCP server:

```bash
npx -y @xferops/forge-mcp
```

Configure in your MCP client (e.g., `~/.mcporter/mcporter.json`):

```json
{
  "mcpServers": {
    "forge": {
      "command": "npx",
      "args": ["-y", "@xferops/forge-mcp"],
      "env": {
        "FLOWER_URL": "https://forge.xferops.com",
        "FLOWER_TOKEN": "your-api-token"
      }
    }
  }
}
```

Get your API token from Forge → Settings → API Tokens.

## Tools (25 total)

### Teams & Projects
- `forge_list_teams` — List all teams
- `forge_get_project` — Get project with columns and tasks
- `forge_list_projects` — List projects in a team

### Tasks
- `forge_list_tasks` — List tasks (filter by projectId, columnId, assigneeId)
- `forge_get_task` — Get task details
- `forge_create_task` — Create task (projectId, columnId, title required)
- `forge_update_task` — Update task fields
- `forge_delete_task` — Delete a task
- `forge_move_task` — Move to different column
- `forge_search_tasks` — Search by title, description, or ticket number

### Columns
- `forge_list_columns` — List columns in a project
- `forge_create_column` — Create a column
- `forge_update_column` — Update column name/position
- `forge_delete_column` — Delete a column

### Comments
- `forge_list_comments` — List comments on a task
- `forge_create_comment` — Add a comment
- `forge_update_comment` — Edit a comment
- `forge_delete_comment` — Delete a comment

### Users & Members
- `forge_list_users` — List all users
- `forge_get_current_user` — Get authenticated user
- `forge_list_team_members` — List team members
- `forge_add_team_member` — Add user to team
- `forge_remove_team_member` — Remove from team

### Notifications
- `forge_get_notification_preferences` — Get notification settings
- `forge_update_notification_preferences` — Update settings

## Common Patterns

### Find a ticket by number

```bash
mcporter call forge.forge_search_tasks query="#123"
```

### Create a task

```bash
mcporter call forge.forge_create_task \
  projectId=<id> \
  columnId=<id> \
  title="Task title" \
  description="Details" \
  priority=HIGH \
  type=BUG
```

### Move task to different column

```bash
mcporter call forge.forge_move_task \
  taskId=<id> \
  columnId=<new-column-id>
```

### Add a comment

```bash
mcporter call forge.forge_create_comment \
  taskId=<id> \
  content="Comment text"
```

## Field Values

**Priority:** `LOW`, `MEDIUM`, `HIGH`, `URGENT`

**Type:** `TASK`, `BUG`, `STORY`

**PR fields:** `prUrl`, `prNumber`, `prRepo` (for GitHub PR linking)