# Setup — Apple Health

Read this silently when `~/apple-health/` does not exist or is empty.
Start the conversation naturally and focus on enabling the connection fast.

## Priority Order

### 1. Confirm Goal and Client
Ask what the user wants first:
- connect now
- only evaluate options
- troubleshoot existing MCP setup

Then confirm the MCP client (for example Claude Desktop, Cursor, or another MCP-compatible client).

### 2. Confirm Data Source
State this clearly: terminal agents do not read live HealthKit directly.
This workflow uses Apple Health exports in CSV format.

If user has no export yet:
1. Ask them to export Apple Health CSV data from iPhone.
2. Ask where the unzipped export folder is on their computer.
3. Continue only after they provide a concrete local path.

### 3. Wire MCP Server
Use the config from `mcp-config.md` with:
- command `npx`
- package `@neiltron/apple-health-mcp`
- env `HEALTH_DATA_DIR` set to a verified absolute path

If configuration is partial or placeholder-based, fix it before testing queries.

Preflight before first run:
1. Check `node -v` and prefer LTS (18, 20, or 22).
2. Run `npx -y @neiltron/apple-health-mcp` once.
3. If startup fails with missing `duckdb.node`, switch Node version and retry.

### 4. Run Verification Sequence
After wiring:
1. Run `health_schema`
2. Run one bounded query from `query-recipes.md`
3. Confirm expected date range and units

If any step fails, do not proceed to analysis. Fix integration first.

If MCP still fails after Node LTS switch, use the fallback flow in `fallback-cli.md`.

## What to Save

| Save to | Content |
|---------|---------|
| `memory.md` | Status, integration mode, last validated export path, freshness timestamp |
| `integrations.md` | MCP client config decisions and known working command/env |
| `query-log.md` | Queries that worked, plus caveats on units and table names |

## Guardrails

- Never claim real-time Apple Health sync from terminal-only setup.
- Never expose raw CSV rows unless user asks.
- Always disclose when analysis comes from old exports.
