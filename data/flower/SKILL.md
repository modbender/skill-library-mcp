---
name: flower
description: Manage projects and tasks with the Flower project management API via MCP. Use when creating, updating, or searching tasks/tickets, managing projects and columns, or integrating with Flower/Kanban boards. Requires @xferops/flower-mcp and a Flower API token.
---

# Flower MCP

Project management via MCP (Model Context Protocol).

## Setup

Install the MCP server:

```bash
npx -y @xferops/flower-mcp
```

Configure in your MCP client (e.g., `~/.mcporter/mcporter.json`):

```json
{
  "mcpServers": {
    "flower": {
      "command": "npx",
      "args": ["-y", "@xferops/flower-mcp"],
      "env": {
        "FLOWER_URL": "https://flower.xferops.com",
        "FLOWER_TOKEN": "your-api-token"
      }
    }
  }
}
```

Get your API token from Flower → Settings → API Tokens.

## Tools (25 total)

### Teams & Projects
- `flower_list_teams` — List all teams
- `flower_get_project` — Get project with columns and tasks
- `flower_list_projects` — List projects in a team

### Tasks
- `flower_list_tasks` — List tasks (filter by projectId, columnId, assigneeId)
- `flower_get_task` — Get task details
- `flower_create_task` — Create task (projectId, columnId, title required)
- `flower_update_task` — Update task fields
- `flower_delete_task` — Delete a task
- `flower_move_task` — Move to different column
- `flower_search_tasks` — Search by title, description, or ticket number

### Columns
- `flower_list_columns` — List columns in a project
- `flower_create_column` — Create a column
- `flower_update_column` — Update column name/position
- `flower_delete_column` — Delete a column

### Comments
- `flower_list_comments` — List comments on a task
- `flower_create_comment` — Add a comment
- `flower_update_comment` — Edit a comment
- `flower_delete_comment` — Delete a comment

### Users & Members
- `flower_list_users` — List all users
- `flower_get_current_user` — Get authenticated user
- `flower_list_team_members` — List team members
- `flower_add_team_member` — Add user to team
- `flower_remove_team_member` — Remove from team

### Notifications
- `flower_get_notification_preferences` — Get notification settings
- `flower_update_notification_preferences` — Update settings

## Common Patterns

### Find a ticket by number

```bash
mcporter call flower.flower_search_tasks query="#123"
```

### Create a task

```bash
mcporter call flower.flower_create_task \
  projectId=<id> \
  columnId=<id> \
  title="Task title" \
  description="Details" \
  priority=HIGH \
  type=BUG
```

### Move task to different column

```bash
mcporter call flower.flower_move_task \
  taskId=<id> \
  columnId=<new-column-id>
```

### Add a comment

```bash
mcporter call flower.flower_create_comment \
  taskId=<id> \
  content="Comment text"
```

## Field Values

**Priority:** `LOW`, `MEDIUM`, `HIGH`, `URGENT`

**Type:** `TASK`, `BUG`, `STORY`

**PR fields:** `prUrl`, `prNumber`, `prRepo` (for GitHub PR linking)
