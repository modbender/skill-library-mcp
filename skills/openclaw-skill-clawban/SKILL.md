---
name: kanban-workflow
description: Kanban Workflow is a TypeScript skill for a stage-based agentic co-worker that integrates PM platforms via CLI-first adapters (CLIs or small wrapper scripts). It provides setup + verbs (show/next/start/update/ask/complete/create) around a canonical stage set (backlog/blocked/in-progress/in-review), plus polling/diffing foundations and automation hooks.

# Skill packaging / runtime requirements
requirements:
  # Core runtime
  binaries:
    - node
    - npm
  node:
    install: npm ci

  # Adapter-specific CLIs (only required if you select that adapter at setup time)
  adapters:
    github:
      binaries: [gh]
    planka:
      binaries: [planka-cli]
    plane:
      # ClawHub skill `plane` (owner: vaguilera-jinko)
      binaries: [plane]
    linear:
      # Uses LINEAR_API_KEY (ClawHub skill `linear`, owner: ManuelHettich) via scripts/linear_json.sh.
      binaries: [bash, curl, jq]

  # Environment variables
  env:
    # No env vars are required by Kanban Workflow itself.
    # Auth is inherited from the selected platform CLI.
    required: []
    optional:
      # Required when using the Plane adapter (via ClawHub skill `plane`).
      - PLANE_API_KEY
      - PLANE_WORKSPACE
      # Required when using the Linear adapter (via ClawHub skill `linear`).
      - LINEAR_API_KEY
---

# Kanban Workflow (core)

## Goal

Provide a reusable core for a project-management “co-worker” that:

- Uses the existing `stage:*` lifecycle as the canonical state machine.
- Integrates with PM platforms via **adapter-managed auth** (external CLIs/scripts; may require env vars like API keys). Kanban Workflow does not run interactive OAuth flows or persist secrets.
- Centralizes workflow/rules/runbooks so GitHub/Planka/Plane/Linear implementations share logic.

Queue semantics (requirements):
- `next` / `autopilot-tick` operate on **assigned-to-me only** items (across all configured scopes) for every adapter.
- Multi-scope monitoring is allowed, but it must enforce consistent stage/list/status names across all monitored scopes so a single `stageMap` is valid everywhere.

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

- Call existing CLIs (e.g. `gh`, `planka-cli`, `plane`), relying on their auth/session (Plane uses `PLANE_API_KEY` + `PLANE_WORKSPACE`; Linear uses `LINEAR_API_KEY` via the ClawHub skill `linear`).
- Compose multiple CLI calls to implement higher-level operations.
- Synthesize events by polling + snapshot diffing when webhooks or event types are missing.

Canonical adapter entrypoints live in `src/adapters/`:
- `github.ts` (gh CLI)
- `planka.ts` (planka-cli)
- `plane.ts` (ClawHub skill `plane` CLI; owner: `vaguilera-jinko`)
- `linear.ts` (ClawHub skill `linear` auth convention via `scripts/linear_json.sh`)

See also: `src/adapters/README.md` for CLI links and assumptions.

## Entry points

Library entry points:
- `tick()` (poll → normalize → diff → events)
- verb-level workflow helpers: `show`, `next`, `start`, `update`, `ask`, `complete`, `create`, `autopilot-tick`
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

Optional autopilot scheduling:
- `--autopilot-cron-expr "*/5 * * * *"` (default)
- `--autopilot-cron-tz "Europe/Berlin"` (optional)
- `--autopilot-install-cron` (creates an OpenClaw cron job that runs `kanban-workflow autopilot-tick`)

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
2) Finish and validate the Plane + Linear adapters (consume ClawHub skill `plane` output schema; Linear uses `scripts/linear_json.sh` JSON compatibility wrapper).
3) Decide on the authoritative mapping rule for stage → platform state (names vs explicit mapping table) and codify it.
4) Add a small CLI surface for Kanban Workflow itself (e.g. `kanban-workflow tick --adapter plane --workspace ... --project ...`).
