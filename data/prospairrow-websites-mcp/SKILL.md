---
name: prospairrow-websites-mcp
description: Generate more revenue with high-quality leads. Give your AI agent direct access to Prospairrow — extract prospects, enrich with deep company insights, discover competitors, and generate content marketing. Fuel your sales pipeline with enriched firmographics, tech stacks, and key contacts so your team can build a pipeline that closes faster.
metadata: {"openclaw":{"requires":{"bins":["bash","node"],"config":["skills.entries.mcporter.config.servers.websites-mcp.url"],"env":["PROSPAIRROW_API_KEY"]},"primaryEnv":"PROSPAIRROW_API_KEY"}}
---

# Prospairrow Websites MCP

Give your AI agent direct access to Prospairrow's AI-powered prospecting platform.

Move beyond basic information. This skill delivers deep company insights — enriched firmographics, tech stacks, key contacts, competitor intelligence, and content marketing — so your sales team can stop wasting time on bad-fit prospects and build a pipeline that closes faster.

Use this skill when the user asks to run Prospairrow actions through MCP/API.

## Runtime

The full runtime source is maintained in this repository. Install copies repository source locally and runs `npm install --ignore-scripts` to fetch npm dependencies (including Playwright, which downloads browser binaries on first use).

```bash
bash {baseDir}/scripts/install-runtime.sh
```

## Business value

- **Close deals faster** — unlock detailed firmographics, tech stacks, and key contacts to craft personalized pitches that resonate with decision-makers
- **Hyper-target your outreach** — stop wasting time on bad-fit prospects; enrich company data to maximize sales opportunities
- **Discover competitors** — automatically surface competitor intelligence for any prospect
- **Generate content marketing** — produce positioning-driven content directly from your prospect data
- **No external git clone** — runtime source ships with the skill; npm deps fetched from registry at install time

## Supported tasks

- `extract_prospects` (READ_ONLY)
- `list_icp_qualified_companies` (READ_ONLY)
- `get_icp_score` (READ_ONLY)
- `get_company_score` (READ_ONLY)
- `apollo_enrich` (WRITE)
- `add_prospects` (WRITE)
- `enrich_prospects` (WRITE)
- `get_prospect_detail` (READ_ONLY)
- `generate_content_marketing` (WRITE)
- `generate_position_solution` (WRITE; runs `POST /api/v1/prospects/{id}/position-solution`, accepts `prospect_id`, `company`, or `website`)
- `discover_competitors` (READ_ONLY; pass `prospect_id`, `company`, or `website` — resolves ID by search if not provided directly)

## Install runtime

```bash
bash {baseDir}/scripts/install-runtime.sh
```

Runtime install path:

- `$HOME/.openclaw/runtime/websites-mcp`

## OpenClaw config

Set in `~/.openclaw/openclaw.json`:

- `skills.entries.mcporter.config.defaultServer = "websites-mcp"`
- `skills.entries.mcporter.config.servers.websites-mcp.url = "http://127.0.0.1:8799"`

Why `mcporter` here: this key stores MCP server routing/config. This is separate from the Prospairrow skill key used for API credentials.

## API key resolution order

1. Request headers (`Authorization` / `X-API-Key`)
2. Process env fallback: `PROSPAIRROW_API_KEY`
3. Optional OpenClaw skill config (disabled by default; set `WEBSITES_ALLOW_OPENCLAW_CONFIG_API_KEY=1`):
   - `skills.entries.prospairrow-websites-mcp.apiKey`
   - `skills.entries.prospairrow-websites-mcp.env.PROSPAIRROW_API_KEY`

## Security toggles

- `WEBSITES_ALLOW_OPENCLAW_CONFIG_API_KEY=1`: allow reading `~/.openclaw/openclaw.json` for API key fallback.
- `WEBSITES_LOG_INVOCATIONS=1`: enable writing `logs/task-invocations.log` (off by default).
- `WEBSITES_DISABLE_STORAGE_STATE_WRITE=1`: disable writing browser storage state to `secrets/<site>/auth.json`.

## MCP request shape

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "websites.run_task",
  "params": {
    "siteId": "prospairrow",
    "taskId": "generate_content_marketing",
    "params": {
      "positioning_intensity": 6
    }
  }
}
```

## Preconditions

- `websites-mcp` listener is reachable (default `127.0.0.1:8799`).
- WRITE tasks require write-enabled runtime mode.
- Runtime must have API key available via config or env.
