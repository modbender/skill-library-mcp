# Kanban Workflow

A TypeScript-first core skill for a stage-based “agentic co-worker” that integrates project-management platforms via **CLI-first adapters** (external CLIs or wrapper scripts; some use API keys via env vars). It also includes an `autopilot-tick` command intended to be run on a schedule (e.g. OpenClaw cron). Setup can optionally install that cron job.

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
- **Plane** via ClawHub skill `plane` (owner: `vaguilera-jinko`)
- **Linear** via ClawHub skill `linear` (ManuelHettich) + this repo’s `scripts/linear_json.sh` compatibility wrapper

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

## Security model

Kanban Workflow **does not** run interactive OAuth flows or persist secrets. Authentication is handled by the adapter’s CLI/script (often via an existing CLI session or an API key environment variable).

Instead, it shells out to a platform-specific CLI (e.g. `gh`, `plane`, `scripts/linear_json.sh`, `planka-cli`) and therefore acts with the **same privileges as that CLI session** on the host machine.

Implications:
- Anything the authenticated CLI can read/write, this skill can read/write.
- Keep your CLI sessions scoped appropriately (least privilege), and treat `config/kanban-workflow.json` as sensitive metadata (it contains IDs, not secrets).

See `SECURITY.md` for more detail.

## Development / install

Prereqs:
- Node.js + npm
- Adapter CLI(s) for the platform you plan to use:
  - GitHub: `gh`
  - Planka: `planka-cli`
  - Plane: ClawHub skill `plane` (binary `plane`; requires `PLANE_API_KEY` + `PLANE_WORKSPACE`)
  - Linear: `curl` + `jq` + `LINEAR_API_KEY` (via ClawHub skill `linear`); Kanban Workflow calls `scripts/linear_json.sh`

Install dependencies:
```bash
npm ci
```

Run tests:
```bash
npm test
```

Build:
```bash
npm run build
```

## Adapters

Adapters live in `src/adapters/`.

- GitHub: uses **GitHub CLI** (`gh`, incl. `gh api`)
- Planka: uses **planka-cli** (https://github.com/voydz/planka-cli)
- Plane: uses ClawHub skill **`plane`** (owner: `vaguilera-jinko`) (binary `plane`; env: `PLANE_API_KEY`, `PLANE_WORKSPACE`).
- Linear: uses ClawHub skill **`linear`** (ManuelHettich) auth convention (`LINEAR_API_KEY`) via this repo’s `scripts/linear_json.sh` wrapper.

Notes:
- Kanban Workflow itself does **not** manage platform auth flows.

## Status

Early scaffolding / prototype. Interfaces and CLI surface are expected to change.
