---
name: kanban-workflow
description: Kanban Workflow is a TypeScript skill for a stage-based agentic co-worker that integrates PM platforms via CLI-auth adapters only (no direct HTTP auth). It provides setup + verbs (show/next/start/update/ask/complete/create) around a canonical stage set (backlog/blocked/in-progress/in-review), plus polling/diffing foundations and automation hooks.
---

# Kanban Workflow (core)

## Goal

Provide a reusable core for a project-management “co-worker” that:

- Uses the existing `stage:*` lifecycle as the canonical state machine.
- Integrates with PM platforms via **CLI-managed auth** only (no direct HTTP auth handling).
- Centralizes workflow/rules/runbooks so GitHub/Planka/Plane/Linear implementations share logic.

## Canonical stage model

Treat these labels/states as canonical (and the **only** stages the agent should consider):

- `stage:backlog`
- `stage:blocked`
- `stage:in-progress`
- `stage:in-review`

Notes:
- Done/closed is platform-specific and intentionally not part of the canonical stage set.

Adapters map platform concepts (labels, lists, statuses, custom fields) into this canonical set.

## Architecture (ports & adapters)

### Core (platform-agnostic)

- Canonical entities: `WorkItem`, `Project`, `Comment`, `Stage`.
- Canonical events: `WorkItemCreated`, `WorkItemUpdated`, `StageChanged`, `CommentAdded`, etc.
- Workflow engine: stage-based worker loop + clarification/comment templates.
- State: cursors + dedupe + snapshots for diffing.

### Adapters (platform-specific)

Adapters are “smart wrappers” that:

- Call existing CLIs (e.g. `gh`, `planka-cli`, `plane-cli`, `linear-cli`), relying on their auth/session.
- Compose multiple CLI calls to implement higher-level operations.
- Synthesize events by polling + snapshot diffing when webhooks or event types are missing.

Canonical adapter entrypoints live in `src/adapters/`:
- `github.ts` (gh CLI)
- `planka.ts` (planka-cli)
- `plane.ts` (plane-cli; Api2Cli workspace)
- `linear.ts` (linear-cli; Api2Cli workspace)

See also: `src/adapters/README.md` for CLI links and assumptions.

## Entry points

Library entry points:
- `tick()` (poll → normalize → diff → events)
- verb-level workflow helpers: `show`, `next`, `start`, `update`, `ask`, `complete`, `create`
- automations: `runProgressAutoUpdates()`

CLI entry point:
- `src/cli.ts` (provides `kanban-workflow <verb>`; see README for setup flags)

## CLI ergonomics: "What next" tips

All `kanban-workflow <verb>` commands print a `What next:` tip after execution to guide the canonical flow:

`setup` → `next` → `start` → (`ask` | `update`) → `complete` → `next`

After `start`, the tip additionally reminds you to run the actual execution/implementation work in a **subagent**, then report back via `ask`/`update`.

If `config/kanban-workflow.json` is missing or invalid, **all commands** error and instruct you to complete setup.

## Setup (flags-only)

Setup writes `config/kanban-workflow.json` and validates that the selected platform CLI is installed + authenticated.

Required:
- `kanban-workflow setup --adapter <github|plane|linear|planka> ...`
- stage mapping flags: `--map-backlog`, `--map-blocked`, `--map-in-progress`, `--map-in-review`

Adapter flags (summary):
- GitHub: `--github-repo <owner/repo>`, optional `--github-project-number <number>`
- Plane: `--plane-workspace-slug <slug>`, `--plane-project-id <uuid>`, optional `--plane-order-field <field>`
- Linear: `--linear-team-id <id>` or `--linear-project-id <id>`, optional `--linear-view-id <id>`
- Planka: `--planka-board-id <id>`, `--planka-backlog-list-id <id>`

## Continuous status updates

While a task is in `stage:in-progress`, Kanban Workflow can post an automatic progress update comment every 5 minutes.
Use `runProgressAutoUpdates()` and persist its `state` in your agent/runtime.

## Recommended repo layout

- `scripts/`: deterministic helper scripts used by adapters or the core.
- `references/`: schemas and adapter notes (loaded on demand).
- `assets/`: runbooks/SOP templates.

## Repo status

- The **current core implementation is in TypeScript** under `src/`.

## Next implementation steps

1) Extend the adapter port to include idempotent write operations (comment/transition/label) in addition to `fetchSnapshot()`.
2) Finish and validate the Plane + Linear adapters (consume `plane-cli` / `linear-cli` output schemas).
3) Decide on the authoritative mapping rule for stage → platform state (names vs explicit mapping table) and codify it.
4) Add a small CLI surface for Kanban Workflow itself (e.g. `kanban-workflow tick --adapter plane --workspace ... --project ...`).
