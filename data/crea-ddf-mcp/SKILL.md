---
name: crea-ddf-mcp
description: Query CREA/REALTOR.ca DDF via a hardened MCP server and CLI for institutional-grade listing data retrieval, metadata inspection, and media access. Use when a user needs DDF tools in Claude MCP, OpenClaw, or scripted research workflows.
---

# CREA DDF MCP

Use this skill to run DDF as a governed MCP/CLI integration for downstream analysis and automations.

## Workflow

### 1. Configure DDF credentials

Set environment variables:

- `DDF_BASE_URL`
- `DDF_AUTH_URL`
- `DDF_TOKEN_GRANT` (`client_credentials` or `password`)
- `DDF_CLIENT_ID` + `DDF_CLIENT_SECRET` (for client credentials)
- `DDF_USERNAME` + `DDF_PASSWORD` (for password grant)

Optional operational controls:

- `DDF_HTTP_TIMEOUT_MS`, `DDF_HTTP_RETRIES`, `DDF_HTTP_RPS`, `DDF_HTTP_BURST`
- `DDF_MEDIA_ENTITY`, `DDF_MEDIA_RECORD_KEY_FIELD`, `DDF_MEDIA_ORDER_FIELD`

### 2. Build and run MCP

```bash
npm --workspace @fub/crea-ddf-mcp run build
node packages/crea-ddf-mcp/dist/mcp-server.js
```

### 3. Validate with CLI

```bash
npm --workspace @fub/crea-ddf-mcp run dev:cli -- search-properties --filters-json '{"city":"Toronto"}' --top 5
npm --workspace @fub/crea-ddf-mcp run dev:cli -- get-property --id "<ListingKey>"
npm --workspace @fub/crea-ddf-mcp run dev:cli -- get-metadata
```

### 4. Wire into Claude MCP/OpenClaw

Use `references/claude-mcp-config.md` for Claude setup and `references/openclaw-wiring.md` for OpenClaw runtime wiring.

## Safety Rules

- Prefer typed tools (`ddf.search_properties`, `ddf.get_property`) over raw calls.
- Keep field selections to allowlisted safe sets unless governance is updated.
- Treat data licensing/display obligations as upstream policy requirements.
- Never store credentials in plaintext files committed to git.
