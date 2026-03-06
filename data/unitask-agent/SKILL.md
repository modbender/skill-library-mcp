---
name: "unitask-agent"
description: "Start finishing tasks instead of just organizing them: connect your OpenClaw agent to Unitask (unitask.app) to manage and do your tasks with secure prioritization, tags, time blocks and more."
homepage: https://unitask.app
read_when:
  - User wants to manage Unitask tasks from an AI agent
  - User wants to time-block today using Unitask scheduled_start + duration_minutes
metadata: {"clawdbot":{"emoji":"✅","requires":{"env":["UNITASK_API_KEY"]},"primaryEnv":"UNITASK_API_KEY"}}
---

# Unitask Agent

## Purpose

This skill lets an AI agent safely manage a user's Unitask account using **scoped API tokens**.
Unitask is in **public beta**. Anyone can sign up at `https://unitask.app`.

Supported operations:
- List tasks
- Get one task
- Create task
- Update task fields (`update_task`)
- Update status (`update_task_status`)
- Move subtask to a different parent (`move_subtask`)
- Merge parent tasks (`merge_parent_tasks`)
- List/create/update/delete tags
- Add/remove tags on tasks
- Delete task (soft delete)
- Read/update settings (optional one-time setup)
- Plan day time blocks (preview/apply)

Subtasks:
- Subtasks are tasks with a `parent_id`.
- Create a subtask via `create_task` with `parent_id=<parent id>`.

## Required setup

1. User signs up (public beta) at `https://unitask.app` if they do not already have an account.
2. User creates a Unitask API token from `Unitask -> Dashboard -> Settings -> API`.
3. User stores it in their agent/app secret store as: `UNITASK_API_KEY=<token>`.

Never ask users to paste full tokens in chat logs.

## Scope model

- `read`: required for read/list actions.
- `write`: required for create/update/move/merge actions.
- `delete`: required for delete actions.
- If `write` or `delete` is granted, `read` must also be granted.

## Hosted MCP (unitask.app, HTTPS)

Endpoint:
- `https://unitask.app/api/mcp`

Auth header (recommended):
- `Authorization: Bearer <UNITASK_API_KEY>`

## MCP tools

- `list_tasks` — filter by `status` (`todo|done`), `limit`, `offset`, `parent_id`, `tag_id`
  - advanced filters: `view` (`today|upcoming`), `tz`, `window_days`, `due_from`, `due_to`, `start_from`, `start_to`, `sort_by`, `sort_dir`
- `get_task` — fetch one task
- `create_task` — create task/subtask
- `update_task` — full mutable field update
- `update_task_status` — status-only helper
- `move_subtask` — move a subtask between parents (`dry_run` default true)
- `merge_parent_tasks` — merge parent trees (`dry_run` default true)
- `delete_task` — soft-delete task + descendants
- `list_tags` — list available tags
- `get_tag` — fetch one tag
- `create_tag` — create a tag
- `update_tag` — edit tag name/color/deleted
- `delete_tag` — soft-delete tag
- `add_task_tag` — attach tag to task
- `remove_task_tag` — detach tag from task
- `get_settings` — get user settings
- `update_settings` — update settings/quiz
- `plan_day_timeblocks` — preview/apply schedule

## Safety rules

- Use smallest required scope for the requested action.
- For public beta, keep least-privilege scopes by workflow: `read`, `write`, `delete`.
- Confirm destructive actions (delete) unless user explicitly asks to proceed.
- Prefer `status=done` over delete when intent is completion.
- For `move_subtask` and `merge_parent_tasks`, keep `dry_run=true` first and apply only after confirmation.
