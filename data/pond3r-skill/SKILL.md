---
name: pond3r-skill
description: Query crypto intelligence via Pond3r MCP — curated datasets, SQL queries, protocol metrics, yields, and market analysis. Use when the agent needs DeFi data, stablecoin yields, token opportunities, Polymarket trades, cross-protocol comparisons, or blockchain analytics.
---

# Pond3r Crypto Intelligence Skill

Use this skill when the agent needs to query crypto/DeFi data: yields, protocol metrics, token opportunities, market analysis, or blockchain analytics. Pond3r provides an MCP server with read-only SQL access to curated datasets.

## Prerequisites

- **API key**: Obtain at [makeit.pond3r.xyz/api-keys](https://makeit.pond3r.xyz/api-keys)
- **MCP setup**: Pond3r must be configured as an MCP server in the runtime (Claude Code, Cursor, Claude Desktop, etc.)

## Setup: Where Is the Agent Running?

The agent needs **MCP tools** (`list_datasets`, `get_schema`, `query`) to use Pond3r. Those tools come from the **runtime** that executes the agent — not from the skill or env vars alone.

| Runtime | How to enable Pond3r |
|---------|------------------------|
| **Cursor** | Cursor Settings → MCP Servers → Add server (URL + Authorization header). See [MCP Connection](#mcp-connection) below. |
| **Claude Desktop** | Add Pond3r to `claude_desktop_config.json` under `mcpServers`. Restart Claude. |
| **Claude Code** | Run `claude mcp add pond3r-data ...` (see below). |
| **OpenClaw (Docker/Telegram)** | Use the **CLI scripts** below. They call Pond3r MCP via HTTP. Set `POND3R_API_KEY` in `.env`; the agent runs the scripts and parses JSON output. |

**No extra info for the agent** — the skill is enough. For runtimes with native MCP, add the API key in the MCP server config. For OpenClaw, use the scripts and `POND3R_API_KEY` in env.

## MCP Connection

| Setting | Value |
|---------|-------|
| URL | `https://mcp.pond3r.xyz/mcp` |
| Transport | Streamable HTTP |
| Auth | `Authorization: Bearer <API_KEY>` |

### Cursor

1. Open **Cursor** → **Settings** (⌘+,) → **MCP**
2. Click **Add new MCP server**
3. Configure:
   - **URL**: `https://mcp.pond3r.xyz/mcp`
   - **Headers**: `Authorization: Bearer <YOUR_POND3R_API_KEY>`
     - Replace `<YOUR_POND3R_API_KEY>` with your key from [makeit.pond3r.xyz/api-keys](https://makeit.pond3r.xyz/api-keys)
     - Some clients support `Authorization: Bearer ${POND3R_API_KEY}` if that env var is set
4. Save and **restart Cursor** so tools load
5. Verify: start a new chat and ask for stablecoin yields — the agent should call `list_datasets`, `get_schema`, `query`

### Claude Code

```bash
claude mcp add pond3r-data \
  --transport http \
  https://mcp.pond3r.xyz/mcp \
  --header "Authorization: Bearer <API_KEY>"
```

### Claude Desktop (claude_desktop_config.json)

```json
{
  "mcpServers": {
    "pond3r": {
      "type": "http",
      "url": "https://mcp.pond3r.xyz/mcp",
      "headers": {
        "Authorization": "Bearer <API_KEY>"
      }
    }
  }
}
```

## CLI Scripts (OpenClaw / Any Runtime)

When MCP tools are not available (e.g. OpenClaw/Telegram), use these scripts. They call Pond3r MCP over HTTP. **Requires `POND3R_API_KEY` in env** (e.g. in `.env` loaded by docker-compose).

Scripts live at `/opt/pond3r-skill-scripts/` in the Docker image. When running locally, use `ceo-agent/skills/pond3r-skill/scripts/` or the workspace-relative path.

### 1) List datasets

```bash
node /opt/pond3r-skill-scripts/list-datasets.mjs
```

Output: JSON with all datasets and tables.

### 2) Get schema for a dataset

```bash
node /opt/pond3r-skill-scripts/get-schema.mjs --dataset-id <dataset_id>
```

### 3) Run a SQL query

```bash
node /opt/pond3r-skill-scripts/query.mjs --dataset-id <dataset_id> --sql "SELECT * FROM stablecoin_yields LIMIT 10"
```

Or from file:

```bash
node /opt/pond3r-skill-scripts/query.mjs --sql-file /tmp/query.sql
```

### Script workflow

1. Run `list-datasets.mjs` to discover datasets and table names.
2. Run `get-schema.mjs --dataset-id <id>` to see columns and types.
3. Run `query.mjs --dataset-id <id> --sql "SELECT ..."` with valid SQL (SELECT only, bare table names, LIMIT where appropriate).
4. Parse the JSON output and summarize for the user.

### Failure handling

- `Missing required env var: POND3R_API_KEY` → Add `POND3R_API_KEY` to `.env` and ensure it is loaded (e.g. docker-compose `env_file: .env`).
- `Pond3r MCP HTTP 401` → Invalid or expired API key; rotate key at makeit.pond3r.xyz/api-keys.
- `Pond3r MCP error: ...` → Check SQL syntax, table names, and row limits.

## Available Tools (Native MCP)

| Tool | Purpose |
|------|---------|
| `list_datasets` | List all datasets and their tables |
| `get_schema` | Get column names, types, descriptions for a dataset |
| `query` | Execute read-only SQL against a dataset |

## Query Rules

- **SELECT only** — write operations are not allowed
- **Bare table names** — use `SELECT * FROM stablecoin_yields`, not fully qualified paths
- **Results capped at 10,000 rows** — use `LIMIT` or `WHERE` filters for large datasets
- **Cost estimation** — queries exceeding tier limits are rejected before running

## Use Cases

1. **Protocol Intelligence**
   - Track AI agent launches, token graduations, protocol metrics
   - Daily yield farming reports across Aave, Compound, Convex

2. **Market Opportunity Detection**
   - New tokens on Uniswap with rising liquidity
   - Tokens with <$500K market cap and rising liquidity
   - Polymarket trades with highest volume

3. **Risk-Adjusted Analysis**
   - Multi-dimensional risk scoring (volatility, liquidity, market structure)
   - Liquidation risk monitoring for DeFi positions
   - Whale activity tracking

4. **Cross-Protocol & Cross-Chain**
   - Compare USDC yields across Aave and Compound on Arbitrum
   - Bridge volume analysis, ecosystem health comparison
   - Arbitrage opportunity detection

5. **Structured Data for Decisions**
   - Statistical analysis, trend identification
   - Volume pattern analysis, unusual trading activity
   - Sentiment scoring (Farcaster, influencer activity)

## Example Queries (Natural Language → SQL)

Agent asks in natural language; MCP tools discover schema and execute SQL. Example prompts:

- "What are the top 5 stablecoin yields on Ethereum right now?"
- "Show me Polymarket trades from the last 24 hours with the highest volume."
- "Compare USDC yields across Aave and Compound on Arbitrum."

## Workflow

1. **Discover available data**: Call `list_datasets` to see datasets and tables
2. **Understand schema**: Call `get_schema` for the dataset you need
3. **Write and run**: Use `query` with valid SQL (SELECT, bare table names, LIMIT where appropriate)
4. **Interpret results**: Use returned data for analysis, proposals, or decisions

## Runtime Enforcement (Mandatory)

Before answering with Pond3r-backed data:

1. **Prefer scripts when MCP tools are unavailable**:
   - If `list_datasets`, `get_schema`, `query` are not exposed by the runtime, use the [CLI scripts](#cli-scripts-openclaw--any-runtime) instead.
   - Run `node /opt/pond3r-skill-scripts/list-datasets.mjs` (or workspace path) with `POND3R_API_KEY` in env.
2. **If neither MCP nor scripts work**:
   - Stop and return: `Pond3r unavailable: MCP tools missing and scripts failed (check POND3R_API_KEY in env).`
3. **Do not assume fallback permission**:
   - Do not switch to `web_search`, `web_fetch`, or other sources unless the user explicitly approves fallback.
4. **Return execution evidence**:
   - Include the exact commands run and summarize returned dataset/query output.
   - If a call fails, include the exact error message and next remediation step.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "Pond3r MCP not configured" | Add MCP server in your runtime (Cursor/Claude) with URL + Bearer header. Restart. |
| Tools still missing after config | Restart the app (Cursor/Claude). MCP loads at startup. |
| Agent runs in OpenClaw/Telegram | Use the CLI scripts with `POND3R_API_KEY` in .env. See [CLI Scripts](#cli-scripts-openclaw--any-runtime). |
| Auth/401 errors | Check API key is valid, not expired. Rotate if it was ever exposed. |

## Failure Handling

- If MCP tools are unavailable, provide only:
  - missing tool names
  - required server URL (`https://mcp.pond3r.xyz/mcp`)
  - required auth header format (`Authorization: Bearer <API_KEY>`)
- If SQL is rejected (tier/cost/limits), rewrite with tighter `WHERE`/`LIMIT` and retry.
- If access/auth fails, report `authorization/configuration failure` and request key/server verification.

## Report API (Alternative to MCP)

For scheduled reports and structured JSON delivery, use the REST API:

- **Create report**: `POST https://api.pond3r.xyz/v1/api/reports` with `description`, `schedule`, `delivery_format`
- **Get latest**: `GET https://api.pond3r.xyz/v1/api/reports/{reportId}/latest`
- **Headers**: `x-api-key: <API_KEY>`

Report format includes `executiveSummary`, `analysis`, `opportunities`. For full API details and response structure, see [reference.md](reference.md).

## Security

- Never expose API keys in client-side code or public repositories
- Use environment variables for API keys
- MCP tools are read-only; no writes to Pond3r datasets
- Never print secret values in logs, chat, or command output (only report presence/absence)
- If a secret is accidentally exposed, instruct immediate key rotation before continuing
