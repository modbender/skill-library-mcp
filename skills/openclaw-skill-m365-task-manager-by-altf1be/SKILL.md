---
name: openclaw-skill-m365-task-manager-by-altf1be
description: "Manage lightweight Microsoft 365 task workflows with Microsoft To Do and Planner. Use when a user needs to quickly create, assign, track, and follow up operational tasks in M365 with clear owners, due dates, status, and daily reminders."
homepage: https://github.com/ALT-F1-OpenClaw/openclaw-skill-m365-task-manager
metadata:
  {"openclaw": {"emoji": "✅", "requires": {"env": ["M365_TENANT_ID", "M365_CLIENT_ID"]}, "primaryEnv": "M365_TENANT_ID"}}
---

# M365 Task Manager

Use this skill to perform real Microsoft Graph CRUD operations for Microsoft To Do tasks.

## Setup

1. Create an Entra app registration for delegated sign-in.
2. Add Microsoft Graph delegated permissions:
   - `Tasks.ReadWrite`
   - `User.Read`
   - `offline_access`
3. Configure environment variables:

```bash
M365_TENANT_ID=your-tenant-id-or-common
M365_CLIENT_ID=your-public-client-app-id
# optional
M365_TOKEN_CACHE_PATH=/home/user/.cache/openclaw/m365-task-manager-token.json
```

4. Install dependencies at repo root:

```bash
npm install
```

On first run, the script uses Device Code login and caches tokens for reuse.

## Commands

```bash
# profile connection
node skills/m365-task-manager/scripts/m365-todo.mjs info

# list Microsoft To Do lists
node skills/m365-task-manager/scripts/m365-todo.mjs lists

# list tasks
node skills/m365-task-manager/scripts/m365-todo.mjs tasks:list --list-name "Tasks"

# create task
node skills/m365-task-manager/scripts/m365-todo.mjs tasks:create --list-name "Tasks" --title "2026-03-01-submit-weekly-status-report" --due 2026-03-01

# update task
node skills/m365-task-manager/scripts/m365-todo.mjs tasks:update --list-name "Tasks" --task-id <TASK_ID> --status inProgress

# delete task
node skills/m365-task-manager/scripts/m365-todo.mjs tasks:delete --list-name "Tasks" --task-id <TASK_ID>
```

## Operating standard

- Task title pattern: `YYYY-MM-DD-short-action-owner`
- Required fields: title, owner, due date, status
- Status values: `Open`, `In Progress`, `Blocked`, `Done`

## References

- `references/playbook.md` for operating guidance.

## Scripts

- `scripts/m365-todo.mjs` for Graph CRUD on Microsoft To Do.
- `scripts/format-task-name.sh` for deterministic task naming.

## Author

Abdelkrim BOUJRAF - ALT-F1 SRL - https://www.alt-f1.be

## License

MIT
