---
name: "unitask-task-agent"
description: "Manage tasks + time blocks in Unitask (unitask.app) via scoped API token (CLI or MCP)."
homepage: https://unitask.app
read_when:
  - User wants to manage Unitask tasks from an AI agent
  - User wants to time-block today using Unitask scheduled_start + duration_minutes
metadata: {"clawdbot":{"emoji":"✅"}}
---

# Unitask Task Agent

## Purpose

This skill lets an AI agent safely manage a user's Unitask account using **scoped API tokens**.

It is designed for **hosted use on unitask.app**, so end users do not need to run any local server code.

Supported operations:
- List tasks
- Get one task
- Create task
- Update task status
- Delete task (soft delete)
- Read/update settings (optional one-time setup)
- Plan day time blocks (preview/apply time-blocking)

Subtasks:
- Subtasks are supported as tasks with a `parent_id`.
- Create a subtask by creating a task with `parent_id=<parent task id>`.

## When to use

Use this skill when the user asks for things like:
- "List my tasks / what's next?"
- "Create a task for X"
- "Mark these tasks done"
- "Time-block my day from 9am to 5pm"

## Required setup

1. User creates a Unitask API token from `Unitask -> Dashboard -> Settings -> API`.
2. User stores it in their agent/app as a secret/env var: `UNITASK_API_KEY=<token>`.

Never ask users to paste full tokens in chat logs. Ask them to set environment variables instead.

## Scope model

- `read`: required to read/list tasks.
- `write`: create/update tasks.
- `delete`: delete tasks.
- If `write` or `delete` is granted, `read` must also be granted.

## Hosted MCP (unitask.app, HTTPS)

Use the hosted MCP endpoint:

- `https://unitask.app/api/mcp`

Auth header (recommended):
- `Authorization: Bearer <UNITASK_API_KEY>`

## MCP tools

Exposed tools:
- `list_tasks` — filter by `status` (todo|done|archived), `limit` (1-500), `offset`, `parent_id`
- `get_task` — get one task by id
- `create_task` — title required; optional: description, parent_id, status, priority, due_date, start_date, recurrence, scheduled_start, duration_minutes
- `update_task_status` — change status (todo|done|archived)
- `delete_task` — soft-delete task + descendants
- `get_settings` — get user settings + quiz prefs
- `update_settings` — partial update settings/quiz
- `plan_day_timeblocks` — schedule time blocks in a window

Recommended usage for time blocking:
- Call `plan_day_timeblocks` with `apply=false` to preview.
- Only call again with `apply=true` after the user confirms the plan.

## Safety rules

- Use smallest required scope for the requested action.
- Confirm destructive actions (delete) unless user explicitly asks to proceed.
- Prefer `status=done` over delete when user intent is completion, not removal.
- For `plan_day_timeblocks`, prefer preview (`apply=false`) first; only apply after user confirms.
