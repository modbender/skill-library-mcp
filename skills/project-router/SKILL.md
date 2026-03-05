---
name: project-router
description: "Terminal-first project bootstrapper and workspace context manager. Use when the user asks for /project-style workflows: detect current project, read project context/brief, run standardized targets (build/test/lint/deploy), init a .project bundle via plan/apply, manage artifacts, or expose these actions via MCP server mcp-project-router and CLI project."
---

# project-router

This skill is Safa’s **canonical project management + context switching control plane**.

Core idea:
- **Canonical PM is local + queryable (SQLite)**: projects, tasks, context packs.
- **Trello is a tracking backend/UI**: cards mirror canonical tasks; lists mirror status; labels mirror priority.
- The “killer feature” is **context switching**: load the right docs/code/index for a project/task quickly and deterministically.

It provides:
- CLI: `project <verb> ...`
- MCP server: `mcp-project-router` (tools mirror the CLI)
- Per-project bundle stored in `.project/` (brief, targets, artifact index)
- A canonical task store (SQLite) + Trello sync adapter

## Project bundle layout (v1)

The `.project/` bundle is the **project-local** context nucleus. The canonical PM DB points at these bundles.

Inside a project root:
- `.project/project.json` — structured manifest
- `.project/PROJECT.md` — living brief
- `.project/targets.json` — target definitions (commands)
- `.project/index/artifacts.json` — artifact index
- `.project/history/plans/*.json` — plans
- `.project/history/applies/*.json` — apply receipts

## CLI quick start

### Baseline / existing commands

From anywhere inside a repo/workspace:
- `project detect`
- `project context`
- `project target list`
- `project target run <name>`

Initialize a bundle (dry-run plan + apply):
- `project init` (prints plan)
- `project apply <planId>`

Artifacts:
- `project artifact add <path|url> [--tags a,b,c]` (plan + apply)

### Canonical PM + context switching (new)

> Note: these verbs are the target UX. Implementations should remain idempotent and safe.

Project registration:
- `project pm project add <slug> --name "..." --root <path>`
- `project pm project list`

Task management:
- `project pm task add <slug> "<title>" --priority P0|P1|P2|P3 [--status inbox|next|doing|blocked|waiting|done]`
- `project pm task list [--project <slug>] [--status ...]`
- `project pm task set-status <taskId> <status>`

Context switching:
- `project pm switch <slug>`
  - prints pinned docs + top targets + active tasks
- `project pm focus <taskId>`
  - loads task-linked files/artifacts and updates the task activity log

Trello sync:
- `project pm trello sync [--project <slug>]`
  - ensures the single "Safa — PM" Trello board exists
  - ensures lists exist (Inbox/Next/Doing/Blocked/Waiting/Done)
  - upserts cards for canonical tasks
  - moves cards to match status
  - applies priority labels (P0..P3)

## MCP quick start (via mcporter)

- `mcporter list mcp-project-router --schema --timeout 120000 --json`

Examples:
- Detect:
  - `mcporter call --server mcp-project-router --tool project_detect --args '{}'`
- Read context:
  - `mcporter call --server mcp-project-router --tool project_context_read --args '{}'`
- Run target:
  - `mcporter call --server mcp-project-router --tool project_target_run --args '{"target":"test"}'`

## Trello backend conventions

Single-board setup:
- Board name: `Safa — PM` (or configurable)
- Lists == canonical statuses:
  - `Inbox`, `Next`, `Doing`, `Blocked`, `Waiting`, `Done`
- Card title: `[<project_slug>] <task_title>`
- Card description begins with a machine block for idempotency:
  ```yaml
  --- pm ---
  task_id: <stable-id>
  project: <slug>
  status: <status>
  priority: P0|P1|P2|P3
  ---
  ```
- Labels (priority, color-coded):
  - `P0` = red
  - `P1` = orange
  - `P2` = yellow
  - `P3` = blue

## Canonical PM storage (SQLite)

Recommended DB location (in workspace):
- `/home/safa/clawd/data/pm/pm.sqlite`

Minimum tables (v0):
- `projects(slug PRIMARY KEY, name, root_path, created_at, updated_at)`
- `tasks(task_id PRIMARY KEY, project_slug, title, status, priority, created_at, updated_at)`
- `task_refs(task_id, kind, ref)` (file paths / urls / artifacts)
- `external_refs(task_id, system, external_id, meta_json)` (e.g., Trello card_id/list_id)

## Safety

- Project bundle writes remain **plan/apply**.
- Canonical PM writes should be idempotent and auditable (timestamps + activity log).
- Trello sync should be safe to re-run repeatedly (upsert by `task_id` marker; never duplicate cards).
- `project_target_run` executes commands defined in `.project/targets.json`.
