---
name: docker-mcp-toolkit
description: Control and use an MCP Toolkit running in Docker. Use when setting up Docker MCP Toolkit (docker compose up/down), checking status/logs, configuring environment variables/secrets, listing available MCP tools/servers, or invoking MCP tools (typically via a local HTTP endpoint) to connect OpenClaw workflows to external systems like Postgres/Neon.
---

# Docker MCP Toolkit

Run, manage, and invoke Docker Desktop’s **MCP Toolkit** using the `docker mcp` CLI.

## Install + preflight (Docker Desktop)

1) Install/upgrade Docker Desktop (MCP Toolkit is in Docker Desktop 4.62+ per docs).

2) Enable MCP Toolkit:
- Docker Desktop → **Settings** → **Beta features** → **Enable Docker MCP Toolkit** → **Apply**.

3) Preflight:

```bash
./scripts/preflight.sh
```

## Quick start

List enabled servers/tools:

```bash
./scripts/servers.sh
./scripts/tools.sh
```

## Core operations

- List/enable/disable servers:
  - `./scripts/servers.sh`
  - `./scripts/server-enable.sh <server-name>`
  - `./scripts/server-disable.sh <server-name>`

- List tools:
  - `./scripts/tools.sh`

- Invoke a tool (via Docker’s gateway/tool runner):

```bash
./scripts/call-tool.sh --tool "mcp-find" --json '{"query":"postgres","limit":5}'
```

Notes:
- `call-tool.sh` requires `jq`.
- `docker mcp tools call` uses `key=value` tokens.
- Non-string values use `:=` (example: `limit:=5`, `activate:=true`).
- This skill currently supports only **primitive** JSON values (string/number/bool/null). Nested objects/arrays are rejected.
- For tools requiring object arguments (e.g. `mcp-config-set`), call `docker mcp tools inspect <tool> --format json` then run `docker mcp tools call ...` directly until this skill adds a tested encoder.

## How invocation works (important)

Docker MCP Toolkit runs an MCP Gateway and exposes tools through it. This skill intentionally uses the **`docker mcp tools …`** commands so OpenClaw can invoke tools without needing native MCP client support.

If you need a true MCP client connection (stdio/SSE), pair this skill with the `mcporter` skill.

## Secrets and safety

- Prefer Docker Desktop’s secrets/keychain integration when possible.
- Do not expose gateway ports publicly.
- Use least-privilege credentials (separate Neon role with only required grants).

For hardening guidance, read: `references/security.md`.

## Troubleshooting

- If commands say “Docker Desktop is not running”: start Docker Desktop.
- If MCP Toolkit isn’t visible: confirm it’s enabled in **Beta features**.
- If a tool call fails: run `docker mcp tools --verbose inspect <tool>` and check Docker Desktop MCP Toolkit UI for server configuration.
