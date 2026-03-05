---
name: todoist-cli
description: Manage Todoist tasks, projects, labels, and sections via the `todoist` CLI. Use when a user asks to add/complete/list tasks, show today's tasks, search tasks, or manage projects.
homepage: https://github.com/buddyh/todoist-cli
metadata:
  {
    "openclaw":
      {
        "emoji": "✅",
        "requires": { "bins": ["todoist"] },
        "env": { "TODOIST_API_TOKEN": "" },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "buddyh/tap/todoist",
              "bins": ["todoist"],
              "label": "Install todoist (brew)",
            },
            {
              "id": "go",
              "kind": "go",
              "module": "github.com/buddyh/todoist-cli/cmd/todoist@latest",
              "bins": ["todoist"],
              "label": "Install todoist-cli (go)",
            },
          ],
      },
  }
---

# Todoist CLI

A fast, full-featured Todoist CLI written in Go.

## Authentication

Get your API token from https://todoist.com/app/settings/integrations/developer

```bash
# Interactive
todoist auth

# Direct
todoist auth <your-token>

# Or set environment variable
export TODOIST_API_TOKEN=<your-token>
```

## Tasks

```bash
# Show today's tasks (default)
todoist

# List all tasks
todoist tasks --all

# Filter tasks
todoist tasks --filter "p1"        # High priority
todoist tasks --filter "overdue"   # Overdue
todoist tasks -p Work              # By project

# Show task descriptions and comments
todoist tasks -p Work --details

# Add a task
todoist add "Buy groceries"
todoist add "Call mom" -d tomorrow
todoist add "Urgent" -P 1 -d "today 5pm" -l urgent

# Complete a task
todoist complete <task-id>
todoist done <task-id>

# Reopen completed task
todoist reopen <task-id>

# View task details
todoist view <task-id>

# Update a task
todoist update <task-id> --due "next monday"
todoist update <task-id> -P 2

# Delete a task
todoist delete <task-id>

# Move a task (Kanban workflows)
todoist move <task-id> --section "In Progress"
todoist move <task-id> --project "Work"

# Search
todoist search "meeting"
```

## Projects

```bash
# List projects
todoist projects

# Create project
todoist projects add "New Project" --color blue
```

## Labels

```bash
# List labels
todoist labels

# Create label
todoist labels add urgent --color red
```

## Sections

```bash
# List sections
todoist sections -p Work

# Create section
todoist sections add "In Progress" -p Work
```

## Comments

```bash
# View comments on a task
todoist comment <task-id>

# Add a comment
todoist comment <task-id> "This is a note"
```

## Completed Tasks

```bash
# Show recently completed
todoist completed

# Filter by date
todoist completed --since 2024-01-01 --limit 50
```

## JSON Output

All commands support `--json` for machine-readable output:

```bash
todoist tasks --json | jq '.[] | .content'
```

## Command Reference

| Command | Description |
|---------|-------------|
| `todoist` | Show today's tasks |
| `todoist tasks` | List tasks with filters |
| `todoist add` | Create a new task |
| `todoist complete` | Mark task complete |
| `todoist done` | Alias for complete |
| `todoist reopen` | Reopen completed task |
| `todoist delete` | Delete a task |
| `todoist update` | Update a task |
| `todoist move` | Move task to section/project |
| `todoist view` | View task details |
| `todoist search` | Search tasks |
| `todoist projects` | List/manage projects |
| `todoist labels` | List/manage labels |
| `todoist sections` | List/manage sections |
| `todoist comment` | View/add comments |
| `todoist completed` | Show completed tasks |
| `todoist auth` | Authenticate |

## Priority Mapping

| CLI | Todoist |
|-----|---------|
| `-P 1` | p1 (highest) |
| `-P 2` | p2 |
| `-P 3` | p3 |
| `-P 4` | p4 (lowest) |

## Notes

- All commands support `--json` for machine-readable output
