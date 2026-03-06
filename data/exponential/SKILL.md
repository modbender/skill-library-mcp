---
name: exponential
version: 1.0.0
description: Manage tasks, projects, and workspaces in Exponential via the `exponential` CLI. Use when creating, listing, or updating actions/tasks, viewing projects, checking today's tasks, managing kanban boards, or any Exponential productivity workflow. Triggers on "create a task", "what's on my plate", "list actions", "update task", "exponential", "daily plan", or project management requests.
---

# Exponential CLI Skill

Exponential is an AI-native productivity platform. This skill uses the `exponential` CLI to manage actions (tasks), projects, and workspaces.

## Prerequisites

```bash
npm install -g exponential-cli
exponential auth login --token <JWT> --api-url https://www.exponential.im
```

Verify: `exponential --help` should show available commands.

## Commands

### Actions (Tasks)

**List actions:**
```bash
exponential actions list [--project <id>] [--status <BACKLOG|TODO|IN_PROGRESS|IN_REVIEW|DONE>] [--assignee <id>]
```

**Today's actions:**
```bash
exponential actions today [--workspace <id>]
```

**Date range:**
```bash
exponential actions range --start 2026-01-01 --end 2026-01-31 [--workspace <id>]
```

**Kanban board:**
```bash
exponential actions kanban [--project <id>] [--status <status>] [--assignee <id>]
```

**Create action:**
```bash
exponential actions create -n "Task name" [-d "Description"] [-p <projectId>] [--priority "1st Priority"] [--due 2026-03-01] [--effort 60]
```

**Update action:**
```bash
exponential actions update --id <actionId> [-n "New name"] [-d "New desc"] [-p <projectId>] [--priority "2nd Priority"] [--status COMPLETED] [--kanban DONE] [--due 2026-03-15]
```
Clear a due date: `--due null`

### Projects

```bash
exponential projects list
```

### Workspaces

```bash
exponential workspaces list
```

## Priority Values

`Quick` | `Scheduled` | `1st Priority` | `2nd Priority` | `3rd Priority` | `4th Priority` | `5th Priority` | `Errand` | `Remember` | `Watch` | `Someday Maybe`

## Kanban Statuses

`BACKLOG` | `TODO` | `IN_PROGRESS` | `IN_REVIEW` | `DONE` | `CANCELLED`

## Action Statuses

`ACTIVE` | `COMPLETED` | `CANCELLED`

## Output

- **TTY** (interactive): pretty-printed with colors
- **Piped/scripted**: JSON output (auto-detected)
- Force JSON: `--json`
- Force pretty: `--pretty`

## JSON Output Shape

Actions list:
```json
{
  "actions": [{ "id": "...", "name": "...", "status": "ACTIVE", "priority": "1st Priority", "kanbanStatus": "TODO", "project": { "id": "...", "name": "..." }, "dueDate": null }],
  "total": 1,
  "filters": {}
}
```

Single action (create/update):
```json
{ "id": "...", "name": "...", "status": "ACTIVE", "priority": "Quick", "kanbanStatus": "TODO", "project": { "id": "...", "name": "..." } }
```

## Workflow Patterns

**Create tasks for a project:**
1. `exponential projects list` → find the project ID
2. `exponential actions create -n "Task" -p <projectId> --priority "1st Priority"`

**Triage daily work:**
1. `exponential actions today` → see what's due
2. `exponential actions update --id <id> --kanban IN_PROGRESS` → start working
3. `exponential actions update --id <id> --kanban DONE` → mark complete

**Review project board:**
1. `exponential actions kanban --project <id>` → see full board
2. Filter by status: `--status IN_PROGRESS`
