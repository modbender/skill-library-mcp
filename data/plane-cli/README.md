# plane-cli

A CLI for the **Plane** project management platform, built using **Api2Cli (a2c)**.

- Api2Cli: https://github.com/paulmooreparks/Api2Cli
- Plane API docs: https://developers.plane.so/api-reference/introduction

## Philosophy

- No custom HTTP client code.
- No auth management in our code: we read credentials from environment variables and let **a2c** inject headers.
- Ship a reproducible **a2c workspace** (`plane`) + a few helper scripts.

## Prerequisites

1) Install Api2Cli (`a2c`):
   - https://github.com/paulmooreparks/Api2Cli/releases

2) Create a Plane API key and export it:

```bash
export PLANE_BASE_URL="https://api.plane.so"  # change for self-hosted
export PLANE_API_KEY="plane_api_..."
```

## Install

Clone this repo and point a2c at the included config directory.

Option A (recommended): use the wrapper script (handles `-h/--help`):

```bash
git clone https://github.com/simonvanlaak/plane-cli
cd plane-cli

# one-off: use the wrapper
alias plane='$(pwd)/scripts/plane'

plane --help
plane whoami
```

Option B: call a2c directly:

```bash
alias plane='a2c --config "$(pwd)/a2c" --workspace plane'
plane help
```

## Commands (examples)

Set env:
```bash
export PLANE_BASE_URL="https://api.plane.so"  # change for self-hosted
export PLANE_API_KEY="plane_api_..."
```

Create a shell alias:
```bash
alias plane='a2c --config "$(pwd)/a2c" --workspace plane'
```

Sanity check:
```bash
plane whoami
# (equivalent to: plane get_users_me)
```

Help:
```bash
plane --help
# or: plane help
```

Discovery:
```bash
plane get_workspaces
plane projects <workspace_slug>
```

Clawban needs (Plane "work items" == Plane API "issues"):
```bash
plane states <workspace_slug> <project_uuid>
plane workitems <workspace_slug> <project_uuid>
plane workitem <workspace_slug> <project_uuid> <issue_uuid>

# change state
plane set-state <workspace_slug> <project_uuid> <issue_uuid> <state_uuid>

# add a comment (comment_html is the field Plane expects)
plane comment <workspace_slug> <project_uuid> <issue_uuid> '<p>Hello from plane-cli</p>'
```

## Smoke test

```bash
# prints curated help from the a2c workspace
./scripts/plane --help

# requires valid env
export PLANE_API_KEY="plane_api_..."
export PLANE_BASE_URL="https://api.plane.so"  # optional
./scripts/plane whoami
```

## OpenClaw / ClawHub

This repository is structured as an OpenClaw skill:
- `SKILL.md` documents usage
- `.clawhub/origin.json` contains the ClawHub slug/version metadata

## Payload field names (confirmed against Plane server source)

- **Set state**: PATCH `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/`
  - payload: `{ "state_id": "<state_uuid>" }`

- **Create comment**: POST `/api/v1/workspaces/{slug}/projects/{project_id}/issues/{issue_id}/comments/`
  - payload: `{ "comment_html": "<p>...</p>" }`
