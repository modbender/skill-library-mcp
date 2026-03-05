# Kanban Workflow adapters

Adapters are **CLI-first** integrations. Kanban Workflow delegates authentication to adapter-specific CLIs/scripts (which may use a local CLI session *or* environment variables like API keys). Kanban Workflow itself does not implement OAuth flows or store tokens.

## GitHub

- CLI: **GitHub CLI (`gh`)**
- Link: https://cli.github.com/
- Auth: `gh auth login` / `gh auth status`

## Linear

- Auth + conventions: ClawHub skill **`linear`** (owner: ManuelHettich)
  - Requires `LINEAR_API_KEY`
  - Provides `{baseDir}/scripts/linear.sh` for interactive use

Kanban Workflow’s `LinearAdapter` expects a **JSON-first** CLI surface.
This repo provides `scripts/linear_json.sh` as a small compatibility wrapper that speaks Linear GraphQL and outputs the JSON schema the adapter consumes.

Advanced usage: you can still point the adapter at a different JSON-capable binary via `bin` + `baseArgs`.

## Planka

- CLI: **planka-cli**
- Link: https://github.com/voydz/planka-cli
- Planka project: https://github.com/plankanban/planka

The adapter defaults to calling `planka-cli cards list --json`. If your installed version differs, pass custom `listArgs`.

## Plane

- Project: https://github.com/makeplane/plane
- CLI: ClawHub skill **`plane`** (owner: `vaguilera-jinko`)
  - Binary: `plane`

Auth is handled by the `plane` CLI via environment variables:

- `PLANE_API_KEY`
- `PLANE_WORKSPACE`

The adapter calls the `plane` binary directly (no a2c workspace wrapper).

## Contributing a new adapter

1) Pick/define a CLI that can list work items as JSON.
2) Implement `fetchSnapshot()` mapping to canonical `WorkItem` + `Stage`.
3) Add vitest coverage with mocked CLI output.
