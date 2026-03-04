---
name: solo-factory
description: Install the full Solo Factory toolkit — 23 startup skills + solograph MCP server for code intelligence, KB search, and web search. Use when user says "install solo factory", "set up solo", "install all solo skills", "startup toolkit", or "solo factory setup". This is the one-command entry point for the entire startup pipeline.
license: MIT
metadata:
  author: fortunto2
  version: "1.1.1"
  openclaw:
    emoji: "🏭"
allowed-tools: Bash, Read, Write, AskUserQuestion
argument-hint: "[--mcp] [--skills-only]"
---

# /factory

One-command setup for the entire Solo Factory startup toolkit.

## What gets installed

**23 skills** — full startup pipeline from idea to shipped product:

| Phase | Skills |
|-------|--------|
| Analysis | research, validate, stream, swarm |
| Development | scaffold, setup, plan, build, deploy, review |
| Promotion | seo-audit, content-gen, community-outreach, video-promo, landing-gen, metrics-track |
| Utilities | init, audit, retro, pipeline, humanize, index-youtube, you2idea-extract |

**MCP server** (optional) — [solograph](https://github.com/fortunto2/solograph) provides 15 tools:
- `kb_search` — semantic search over knowledge base
- `session_search` — search past Claude Code sessions
- `codegraph_query` / `codegraph_explain` / `codegraph_stats` / `codegraph_shared` — code intelligence
- `project_info` / `project_code_search` / `project_code_reindex` — project registry
- `source_search` / `source_list` / `source_tags` / `source_related` — source management
- `web_search` — web search

## Steps

1. **Parse arguments** from `$ARGUMENTS`:
   - `--mcp` — also configure solograph MCP server
   - `--skills-only` — skip MCP setup (default)
   - No args — install skills, ask about MCP

2. **Detect agent and choose install method:**

   ```bash
   # Check what's available
   command -v npx >/dev/null 2>&1 && echo "npx: ok"
   command -v clawhub >/dev/null 2>&1 && echo "clawhub: ok"
   ```

   **Method A (recommended): `npx skills`** — works with any AI agent, installs from GitHub directly.
   **Method B: `clawhub install`** — for OpenClaw users who prefer ClawHub registry.
   **Method C: Claude Code plugin** — if user is on Claude Code, suggest plugin instead.

3. **Install all 23 skills:**

   **Method A — npx skills (recommended, works immediately):**

   ```bash
   npx skills add fortunto2/solo-factory --all
   ```

   This single command installs all skills from GitHub to all detected agents (Claude Code, Cursor, Copilot, Gemini CLI, Codex, etc.). No account or publishing required.

   **Method B — clawhub (OpenClaw users):**

   ```bash
   # Check login
   clawhub whoami 2>/dev/null || echo "Run: clawhub login"

   # Install available skills
   for skill in \
     audit build community-outreach content-gen deploy \
     humanize index-youtube init landing-gen metrics-track \
     pipeline plan research retro review \
     scaffold seo-audit setup stream swarm \
     validate video-promo you2idea-extract; do
     echo -n "Installing solo-$skill... "
     clawhub install "solo-$skill" 2>&1 | tail -1
     sleep 2
   done
   ```

   If some skills are not yet on ClawHub, fall back to Method A for those.

   **Method C — Claude Code plugin (all-in-one):**

   ```bash
   claude plugin marketplace add https://github.com/fortunto2/solo-factory
   claude plugin install solo@solo --scope user
   ```

   This installs all 23 skills + 3 agents + hooks + MCP auto-start in one command.

4. **MCP setup** (if `--mcp` or user agreed):

   Ask: "Set up solograph MCP for code intelligence and KB search?"

   **4a. Check uv/uvx:**
   ```bash
   command -v uvx >/dev/null 2>&1 && echo "uvx: ok" || echo "uvx: missing"
   ```
   If missing: "Install uv first: https://docs.astral.sh/uv/"

   **4b. Configure MCP:**

   For OpenClaw (via mcporter):
   ```bash
   mcporter config add solograph --stdio "uvx solograph"
   ```

   For Claude Code (via .mcp.json):
   ```json
   {
     "mcpServers": {
       "solograph": {
         "command": "uvx",
         "args": ["solograph"]
       }
     }
   }
   ```

   **4c. Verify:**
   ```bash
   uvx solograph --help
   ```

5. **Report results:**

   ```
   ## Solo Factory Setup Complete

   **Install method:** npx skills / clawhub / Claude Code plugin
   **Skills installed:** X/23
   **MCP configured:** yes/no
   **Failed:** [list any failures]

   ### Quick start

   Try these commands:
   - `/solo-research "your startup idea"` — scout the market
   - `/solo-validate "your startup idea"` — score + generate PRD
   - `/solo-stream "should I quit my job"` — decision framework

   ### Full pipeline

   research → validate → scaffold → setup → plan → build → deploy → review

   ### More info

   GitHub: https://github.com/fortunto2/solo-factory
   MCP: https://github.com/fortunto2/solograph
   ```

## Common Issues

### npx skills: command not found
**Fix:** Install Node.js 18+. npx comes with npm.

### clawhub: some skills not found
**Cause:** Not all skills published to ClawHub yet.
**Fix:** Use `npx skills add fortunto2/solo-factory --all` instead.

### uvx: command not found (for MCP)
**Fix:** `curl -LsSf https://astral.sh/uv/install.sh | sh`

### MCP tools not working
**Fix:** Test with `uvx solograph --help`. Check `.mcp.json` or mcporter config.
