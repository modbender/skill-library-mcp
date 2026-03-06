---
name: plane-so-cli
description: "Manage Plane.so projects and work items using a zero-dependency Python CLI. List projects, create/update/assign issues, add comments, search workspace. The plane-so-cli binary is bundled in scripts/."
license: MIT
compatibility: Requires Python 3.8+ and internet access to reach the Plane.so API.
homepage: https://github.com/luiseduardoaugusto/plane-so-cli
metadata: {"openclaw": {"requires": {"env": ["PLANE_API_KEY", "PLANE_WORKSPACE"], "bins": ["python3"]}, "primaryEnv": "PLANE_API_KEY", "emoji": "✈️", "homepage": "https://github.com/luiseduardoaugusto/plane-so-cli"}}
---

# Plane.so CLI Skill

Interact with [Plane.so](https://plane.so) project management via a clean, auditable Python CLI.

**Zero dependencies** — uses only Python 3.8+ stdlib. The `plane-so-cli` executable is bundled in `scripts/plane-so-cli` and available on PATH after installation.

## Setup

Set these environment variables:

```bash
export PLANE_API_KEY="your-api-key"
export PLANE_WORKSPACE="your-workspace-slug"
```

Get your API key: **Plane > Profile Settings > Personal Access Tokens**

## Commands

### User & Workspace

```bash
plane-so-cli me                        # Show current user
plane-so-cli projects list             # List all active projects
plane-so-cli members                   # List workspace members
```

### Issues (Work Items)

```bash
plane-so-cli issues list -p PROJECT_ID
plane-so-cli issues list -p PROJECT_ID --state STATE_ID
plane-so-cli issues list -p PROJECT_ID --priority high
plane-so-cli issues list -p PROJECT_ID --assignee USER_ID
plane-so-cli issues get -p PROJECT_ID ISSUE_ID
plane-so-cli issues create -p PROJECT_ID --name "Fix bug" --priority high
plane-so-cli issues create -p PROJECT_ID --name "Task" --assignee USER_ID
plane-so-cli issues update -p PROJECT_ID ISSUE_ID --state STATE_ID
plane-so-cli issues update -p PROJECT_ID ISSUE_ID --priority medium
plane-so-cli issues assign -p PROJECT_ID ISSUE_ID USER_ID_1 USER_ID_2
plane-so-cli issues delete -p PROJECT_ID ISSUE_ID
plane-so-cli issues search "login bug"
plane-so-cli issues my
```

### Comments, States & Labels

```bash
plane-so-cli comments list -p PROJECT_ID -i ISSUE_ID
plane-so-cli comments add -p PROJECT_ID -i ISSUE_ID "Comment text"
plane-so-cli states -p PROJECT_ID
plane-so-cli labels -p PROJECT_ID
```

### Cycles & Modules

```bash
plane-so-cli cycles list -p PROJECT_ID
plane-so-cli cycles get -p PROJECT_ID CYCLE_ID
plane-so-cli modules list -p PROJECT_ID
plane-so-cli modules get -p PROJECT_ID MODULE_ID
```

## Output Formats

Default is human-readable table. Use `-f json` for raw JSON:

```bash
plane-so-cli projects list -f json
```

## Typical Workflow

1. `plane-so-cli projects list` — find project ID
2. `plane-so-cli members` — find member IDs for assignment
3. `plane-so-cli states -p PROJECT_ID` — see available states
4. `plane-so-cli issues create -p PROJECT_ID --name "Task" --assignee USER_ID`
5. `plane-so-cli comments add -p PROJECT_ID -i ISSUE_ID "Started working"`

## Security & Privacy

This skill communicates **only** with the Plane.so API. The API host is hardcoded to `api.plane.so` and cannot be overridden.

| Endpoint | Data sent | Purpose |
|----------|-----------|---------|
| `https://api.plane.so/api/v1/*` | API key (header), project/issue data (body) | All Plane.so operations |

- Your `PLANE_API_KEY` is sent as an `X-API-Key` header exclusively to `https://api.plane.so`
- The API host is hardcoded — no environment variable can redirect requests to another domain
- No data is cached, logged, or stored locally
- No telemetry or analytics are collected
- The full source code is auditable at [github.com/luiseduardoaugusto/plane-so-cli](https://github.com/luiseduardoaugusto/plane-so-cli) and bundled in `scripts/plane-so-cli`
