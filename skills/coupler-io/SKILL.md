# Coupler.io

Read-only data access via Coupler.io's MCP server.

**Author:** Coupler.io Team
**Homepage:** [coupler.io](https://coupler.io)

## Prerequisites

- [mcporter](https://github.com/openclaw/mcporter) CLI installed and on PATH
- Coupler.io account with at least one data flow configured to OpenClaw destination

## Quick Reference

```bash
mcporter call mcp-coupler-io-mcp.list-dataflows
mcporter call mcp-coupler-io-mcp.get-dataflow dataflowId=<uuid>
mcporter call mcp-coupler-io-mcp.get-schema executionId=<exec-id>
mcporter call mcp-coupler-io-mcp.get-data executionId=<exec-id> query="SELECT * FROM data LIMIT 10"
```

---

## Connection Setup

> **Endpoint verification:** This skill connects to `auth.coupler.io` (OAuth) and `mcp.coupler.io` (MCP data). These are official Coupler.io endpoints. You can verify them via your Coupler.io account (AI integrations page).

> **Transport:** This MCP uses **streamable HTTP**, not SSE. If you see "SSE error" in output, ignore the misleading label — it's still HTTP.

### 1. Authenticate and add server in one step

**Do not** use `mcporter config add` followed by `mcporter auth` separately — this creates a config entry without auth metadata and causes a 401 loop. Instead, do it all in one command:

```bash
mcporter auth --http-url https://mcp.coupler.io/mcp --persist config/mcporter.json
```

This auto-detects OAuth, opens the browser for Coupler.io login (PKCE flow), and saves the server definition + tokens on success.

To re-authenticate or clear stale tokens:

```bash
mcporter auth --http-url https://mcp.coupler.io/mcp --persist config/mcporter.json --reset
```

### 2. Ensure `"auth": "oauth"` is in config

After auth, check `config/mcporter.json`. mcporter won't use cached tokens unless the entry has `"auth": "oauth"`. It should look like:

```json
{
  "mcpServers": {
    "mcp-coupler-io-mcp": {
      "baseUrl": "https://mcp.coupler.io/mcp",
      "auth": "oauth"
    }
  }
}
```

If `"auth": "oauth"` is missing, add it manually.

### 3. Verify

```bash
mcporter list mcp-coupler-io-mcp
```

Should return 4 tools: `get-data`, `get-schema`, `list-dataflows`, `get-dataflow`.

> **Note:** The server name is auto-generated as `mcp-coupler-io-mcp` from the URL. Use this name in all subsequent commands.

---

## Token Refresh

mcporter handles token refresh automatically on 401 errors. No manual intervention needed.

If you need to force a fresh token: `mcporter auth mcp-coupler-io-mcp --reset`

---

## MCP Tools

### list-dataflows

List all data flows with OpenClaw destination.

```bash
mcporter call mcp-coupler-io-mcp.list-dataflows --output json
```

### get-dataflow

Get flow details including `lastSuccessfulExecutionId`.

```bash
mcporter call mcp-coupler-io-mcp.get-dataflow dataflowId=<uuid> --output json
```

### get-schema

Get column definitions. Column names are in `columnName` (e.g., `col_0`, `col_1`).

```bash
mcporter call mcp-coupler-io-mcp.get-schema executionId=<exec-id>
```

### get-data

Run SQL on flow data. Table is always `data`.

```bash
mcporter call mcp-coupler-io-mcp.get-data executionId=<exec-id> query="SELECT col_0, col_1 FROM data WHERE col_2 > 100 LIMIT 50"
```

**Always sample first** (`LIMIT 5`) to understand structure before larger queries.

---

## Typical Workflow

```bash
# 1. List flows, find ID
mcporter call mcp-coupler-io-mcp.list-dataflows --output json

# 2. Get execution ID
mcporter call mcp-coupler-io-mcp.get-dataflow dataflowId=<id> --output json

# 3. Check schema
mcporter call mcp-coupler-io-mcp.get-schema executionId=<exec-id>

# 4. Query
mcporter call mcp-coupler-io-mcp.get-data executionId=<exec-id> query="SELECT * FROM data LIMIT 10"
```

---

## Constraints

- Read-only: cannot modify flows, sources, or data
- Only flows with OpenClaw destination are visible
- Tokens expire in 2 hours (mcporter refreshes automatically)
