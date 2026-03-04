# SkillsIndex MCP

**Search, score, and submit AI agent tools from [SkillsIndex](https://skillsindex.dev)**

## What this skill does

Gives your AI agent read/write access to the SkillsIndex public directory — 11,000+ MCP servers, Claude skills, GPT actions, and IDE plugins, each scored on security, utility, maintenance, and uniqueness.

## Security & transparency

- **No credentials required** — no API keys, no GitHub tokens, no secrets
- **No local file access** — the skill makes no filesystem operations
- **Network calls only** — all calls go to `skillsindex.dev` (public REST API over HTTPS) and `npmjs.com` (for `npx` to download the package)
- **Read-only by default** — search, get_tool, get_top_rated, check_security are all read-only
- **Write operations** — `submit_tool` POSTs a tool name + URL to `skillsindex.dev/api/mcp/submit` (public endpoint, no auth); `subscribe` POSTs an email to `skillsindex.dev/api/subscribe`
- **Open source** — full source code at `https://github.com/thomasblc/skillsindex` in the `mcp/` directory
- **No data exfiltration** — the skill never reads or transmits your local files, environment variables, or system data

## How it works

The skill runs as a local stdio MCP server via `npx skillsindex-mcp`. It bundles the compiled TypeScript and calls the SkillsIndex public API endpoints. No server is installed permanently — `npx` runs the package on demand.

**Exact network endpoints called:**
| Tool | Endpoint | Method |
|------|----------|--------|
| search_tools | `https://skillsindex.dev` (Supabase REST API, anon key) | GET |
| get_tool | `https://skillsindex.dev` (Supabase REST API, anon key) | GET |
| get_top_rated | `https://skillsindex.dev` (Supabase REST API, anon key) | GET |
| check_security | `https://skillsindex.dev` (Supabase REST API, anon key) | GET |
| submit_tool | `https://skillsindex.dev/api/mcp/submit` | POST |
| subscribe | `https://skillsindex.dev/api/subscribe` | POST |

The Supabase anon key is a **public read-only key** — it only allows reading published tool data. This is the same key embedded in every SkillsIndex web page.

## Tools

### `search_tools`
Search by keyword, ecosystem, or category. Returns tools ranked by overall score.

```
query:      "postgres database MCP server"
ecosystem:  mcp_server | claude_skill | gpt_action | openclaw_skill | plugin
category:   databases-storage | browser-automation | code-execution | ...
limit:      1–20
```

### `get_tool`
Full details for a tool by slug: security score, GitHub stats, pricing, install difficulty.

```
slug:  "filesystem-mcp-server"
```

### `get_top_rated`
Top-scored tools, optionally filtered by ecosystem or category.

### `check_security`
Security audit report: score (0–5), risk flags, audit notes based on static source analysis.

```
slug:  "tool-slug"     (preferred)
name:  "Tool Name"     (fuzzy match)
```

### `submit_tool`
Submit a new tool for indexing. Sends name, URL, description to SkillsIndex review queue.

```
name:         "My MCP Server"
github_url:   "https://github.com/user/repo"
description:  "What the tool does"
ecosystem:    "mcp_server"
category:     "databases-storage"
```

### `subscribe`
Subscribe an email to The Weekly Index — new tools + security alerts every Thursday.

## Installation

No configuration needed. Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "skillsindex": {
      "command": "npx",
      "args": ["skillsindex-mcp"]
    }
  }
}
```

## Data

- 11,000+ tools across 5 ecosystems
- Scoring formula: security (30%) + utility (30%) + maintenance (25%) + uniqueness (15%)
- Refreshed weekly via GitHub API
- Security scores from static analysis of open-source code (no proprietary data)

## Source code

`https://github.com/thomasblc/skillsindex` → `mcp/src/index.ts`

Full source is auditable. The compiled output in `dist/index.js` matches the TypeScript source exactly.

## Links

- Directory: [skillsindex.dev](https://skillsindex.dev)
- npm: [npmjs.com/package/skillsindex-mcp](https://www.npmjs.com/package/skillsindex-mcp)
- Source: [github.com/thomasblc/skillsindex](https://github.com/thomasblc/skillsindex)
- Scoring methodology: [skillsindex.dev/methodology/](https://skillsindex.dev/methodology/)
