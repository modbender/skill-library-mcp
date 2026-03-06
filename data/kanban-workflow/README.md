# Kanban Workflow

A TypeScript-first core skill for a stage-based “agentic co-worker” that integrates project-management platforms via **CLI-auth adapters** (no direct HTTP auth handling).

## What it is

Kanban Workflow standardizes a canonical workflow state machine using an existing `stage:*` lifecycle:

- `stage:backlog`
- `stage:blocked`
- `stage:in-progress`
- `stage:in-review`

Notes:
- Done/closed is platform-specific and intentionally **not** part of the canonical stage set.

It provides:
- Canonical models + event types
- Snapshot diffing to synthesize events (polling-friendly)
- A deterministic `tick()` runner
- Adapters that call existing CLIs using the user’s authenticated session

Currently supported adapters:
- **GitHub** via `gh` (in-repo adapter)
- **Planka** via `planka-cli` (voydz/planka-cli)
- **Plane** via `plane-cli` (simonvanlaak/plane-cli; a2c workspace)
- **Linear** via `linear-cli` (simonvanlaak/linear-cli; a2c workspace)

See `src/adapters/README.md` for links and notes.

## Repo layout

- `SKILL.md` — OpenClaw skill entrypoint
- `src/` — core library + adapters
- `tests/` — vitest tests
- `references/` — technical plan and notes

## CLI UX: "What next" tips

Every `kanban-workflow <verb>` execution prints a `What next:` tip line to guide the next step in the workflow.

If setup is not completed (missing/invalid `config/kanban-workflow.json`), **all commands** will fail with a clear error and instruct you to run `kanban-workflow setup`.

### Setup

Setup is flags-only (non-interactive) and writes `config/kanban-workflow.json`.

Common flags:
- `--adapter <github|plane|linear|planka>`
- `--force` (required to overwrite an existing config)

Stage mapping (required; map *platform stage/list/status name* → canonical stage):
- `--map-backlog <platform-name>`
- `--map-blocked <platform-name>`
- `--map-in-progress <platform-name>`
- `--map-in-review <platform-name>`

Adapter flags:
- GitHub: `--github-repo <owner/repo>`, optional `--github-project-number <number>`
- Plane: `--plane-workspace-slug <slug>`, `--plane-project-id <uuid>`, optional `--plane-order-field <field>`
- Linear: scope `--linear-team-id <id>` **or** `--linear-project-id <id>`, optional ordering `--linear-view-id <id>`
- Planka: `--planka-board-id <id>`, `--planka-backlog-list-id <id>`

### Continuous status updates

While an item is in `stage:in-progress`, Kanban Workflow can post an **automatic progress update comment every 5 minutes**. The helper is exported as:

- `runProgressAutoUpdates()` (see `src/automation/progress_updates.ts`)

## Development

Prereqs:
- Node.js

Install:
```bash
npm install
```

Run tests:
```bash
npm test
```

Build (optional):
```bash
npm run build
```

## Adapters

Adapters live in `src/adapters/`.

- GitHub: uses **GitHub CLI** (`gh`, incl. `gh api`)
- Planka: uses **planka-cli** (https://github.com/voydz/planka-cli)
- Plane: uses **plane-cli** (https://github.com/simonvanlaak/plane-cli)
- Linear: uses **linear-cli** (https://github.com/simonvanlaak/linear-cli)

Notes:
- Kanban Workflow itself does **not** handle HTTP auth tokens. Authenticate via the CLI you use.
- For Plane/Linear, the CLI is an **Api2Cli (a2c)** workspace + wrapper.

## Status

Early scaffolding / prototype. Interfaces and CLI surface are expected to change.
