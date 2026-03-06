---
name: clickup-pro
description: AI-powered ClickUp project management — tasks, spaces, folders, time tracking, comments, custom fields. AI task prioritization by urgency and importance, daily standup generator. Use for project management, sprint planning, and team coordination.
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+, ClickUp API key
metadata: {"openclaw": {"emoji": "\u2705", "requires": {"env": ["CLICKUP_API_KEY"]}, "primaryEnv": "CLICKUP_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# ✅ ClickUp Pro

AI-powered ClickUp task management for OpenClaw agents. Fork of clickup-api v1.0.3, massively improved with AI prioritization and standup generation.

## What's New vs clickup-api

- **AI task prioritization** — score tasks by urgency × importance using LLM
- **Daily standup generator** — auto-summarize done/in-progress/blocked
- **Time tracking** — start, stop, log time entries
- **Custom fields** — read and write custom fields
- **Comments** — add comments to tasks
- **Full CRUD** — spaces, folders, lists, tasks

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `CLICKUP_API_KEY` | ✅ | ClickUp personal API token |
| `OPENROUTER_API_KEY` | Optional | For AI prioritization and standups |

## Quick Start

```bash
# List workspaces (teams)
python3 {baseDir}/scripts/clickup_api.py workspaces

# List spaces
python3 {baseDir}/scripts/clickup_api.py spaces <team_id>

# List folders in a space
python3 {baseDir}/scripts/clickup_api.py folders <space_id>

# List lists in a folder
python3 {baseDir}/scripts/clickup_api.py lists <folder_id>

# List tasks in a list
python3 {baseDir}/scripts/clickup_api.py tasks <list_id>

# Create a task
python3 {baseDir}/scripts/clickup_api.py create-task <list_id> --name "Fix bug" --priority 2 --due "2026-02-20"

# Update a task
python3 {baseDir}/scripts/clickup_api.py update-task <task_id> --status "in progress" --assignee user123

# Add comment
python3 {baseDir}/scripts/clickup_api.py comment <task_id> --text "Working on this now"

# Time tracking
python3 {baseDir}/scripts/clickup_api.py start-timer <task_id>
python3 {baseDir}/scripts/clickup_api.py stop-timer <team_id>
python3 {baseDir}/scripts/clickup_api.py log-time <task_id> --duration 3600000 --description "Code review"

# AI prioritize tasks in a list
python3 {baseDir}/scripts/clickup_api.py prioritize <list_id>

# Daily standup summary
python3 {baseDir}/scripts/clickup_api.py standup <list_id>
```

## Commands

### Navigation
- `workspaces` — List all workspaces/teams
- `spaces <team_id>` — List spaces in a workspace
- `folders <space_id>` — List folders in a space
- `lists <folder_id>` — List lists in a folder (also: `folderless-lists <space_id>`)

### Tasks
- `tasks <list_id>` — List tasks (with `--status`, `--assignee`, `--subtasks` filters)
- `get-task <task_id>` — Get task details
- `create-task <list_id>` — Create task (`--name`, `--description`, `--priority 1-4`, `--due DATE`, `--assignee`)
- `update-task <task_id>` — Update task (`--name`, `--status`, `--priority`, `--due`, `--assignee`)
- `delete-task <task_id>` — Delete a task

### Time Tracking
- `start-timer <task_id>` — Start tracking time
- `stop-timer <team_id>` — Stop current timer
- `log-time <task_id>` — Log time entry (`--duration MS`, `--description`)

### Comments
- `comment <task_id>` — Add comment (`--text`)

### AI Features (require OPENROUTER_API_KEY)
- `prioritize <list_id>` — AI-score tasks by urgency × importance, output ranked list
- `standup <list_id>` — Generate daily standup (done, in progress, blocked)

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
