---
name: plane-cli
description: Plane (developers.plane.so) CLI powered by Api2Cli (a2c). Includes an a2c workspace (plane) plus a wrapper script to list workspaces/projects, fetch issues (work items), set issue state, and add HTML comments.
metadata: {"openclaw":{"emoji":"🗂️","requires":{"bins":["a2c"]}}}
---

# plane-cli

A thin OpenClaw skill wrapper around the **Plane API** using **Api2Cli (a2c)**.

This skill ships:
- an `a2c/` workspace named **`plane`**
- a wrapper script: `scripts/plane`

## Requirements

- `a2c` installed and available on `PATH`
- Plane credentials in env:
  - `PLANE_API_KEY` (required)
  - `PLANE_BASE_URL` (optional; defaults to `https://api.plane.so`)

## Usage

Call via the wrapper script (recommended):

```bash
./scripts/plane --help
./scripts/plane whoami
./scripts/plane get_workspaces
./scripts/plane projects <workspace_slug>
./scripts/plane states <workspace_slug> <project_uuid>
./scripts/plane workitems <workspace_slug> <project_uuid>
./scripts/plane workitem <workspace_slug> <project_uuid> <issue_uuid>
./scripts/plane set-state <workspace_slug> <project_uuid> <issue_uuid> <state_uuid>
./scripts/plane comment <workspace_slug> <project_uuid> <issue_uuid> '<p>Hello</p>'
```

Notes:
- Plane “work items” are called **issues** in the Plane API.
- `set-state` sends `{"state_id": "..."}`.
- `comment` sends `{"comment_html": "<p>...</p>"}`.

## Smoke test

```bash
# 1) Help works
./scripts/plane --help

# 2) Auth sanity check (requires valid env)
export PLANE_API_KEY="plane_api_..."
export PLANE_BASE_URL="https://api.plane.so"  # optional
./scripts/plane whoami
```
