---
name: coala-client
description: How to use the coala-client CLI for chat with LLMs, MCP servers, and skills. Use when the user asks how to use coala, run coala chat, add MCP servers, import CWL toolsets, list or call MCP tools, import or load skills, or use the sandbox run_command tool.
homepage: https://github.com/coala-info/coala_client
metadata: {"clawdbot":{"emoji":"🧬","requires":{"bins":["coala-client"]},"install":[{"id":"uv","kind":"uv","package":"coala-client","bins":["coala-client"],"label":"Install coala-client (uv)"}]}}
---

# Coala Client

Part of the coala ecosystem. CLI for chat with OpenAI-compatible LLMs (OpenAI, Gemini, Ollama) and MCP (Model Context Protocol) servers. Supports importing CWL toolsets as MCP servers, importing skills, and an optional sandbox to run shell commands.

## Config paths

- MCP config and toolsets: `~/.config/coala/mcps/`  
  - `mcp_servers.json` — server definitions  
  - `<toolset>/` — per-toolset dirs with `run_mcp.py` and CWL files  
- Skills: `~/.config/coala/skills/` (one subfolder per imported source)  
- Env: `~/.config/coala/env` (optional; key=value for providers and MCP env)

## Quick start

1. **Init (first time)**  
   `coala init` — creates `~/.config/coala/mcps/mcp_servers.json` and `env`.

2. **Set API key**  
   e.g. `export OPENAI_API_KEY=...` or `export GEMINI_API_KEY=...`. Ollama needs no key.

3. **Chat**  
   `coala` or `coala chat` — interactive chat with MCP tools.  
   `coala ask "question"` — single prompt with MCP.

4. **Options**  
   `-p, --provider` (openai|gemini|ollama|custom), `-m, --model`, `--no-mcp`, `--sandbox`.

## MCP: CWL toolsets

No API key needed for MCP import, list, or call — only for chat/ask with an LLM.

- **Import** (creates toolset under `~/.config/coala/mcps/<TOOLSET>/` and registers server):  
  `coala mcp-import <TOOLSET> <SOURCES...>` or alias `coala mcp ...`  
  SOURCES: local `.cwl` files, a `.zip`, or http(s) URLs to a .cwl or .zip.  
  Requires the `coala` package where the MCP server runs (for `run_mcp.py`).

- **List**  
  `coala mcp-list` — list server names.  
  `coala mcp-list <SERVER_NAME>` — print each tool’s schema (name, description, inputSchema).

- **Call**  
  `coala mcp-call <SERVER>.<TOOL> --args '<JSON>'`  
  Example: `coala mcp-call gene-variant.ncbi_datasets_gene --args '{"data": [{"gene": "TP53", "taxon": "human"}]}'`

## Skills

- **Import** (into `~/.config/coala/skills/`, one subfolder per source):  
  `coala skill <SOURCES...>`  
  SOURCES: GitHub tree URL (e.g. `https://github.com/owner/repo/tree/main/skills`), zip URL, or local zip/dir.

- **In chat**  
  `/skill` — list installed skills.  
  `/skill <name>` — load skill from `~/.config/coala/skills/<name>/` (e.g. SKILL.md) into context.


## Chat commands

- `/help`, `/exit`, `/quit`, `/clear`  
- `/tools` — list MCP tools  
- `/servers` — list connected MCP servers  
- `/skill` — list skills; `/skill <name>` — load a skill  
- `/model` — show model info  
- `/switch <provider>` — switch provider  

## MCP on/off

- **All off:** `coala --no-mcp` (or `coala ask "..." --no-mcp`).  
- **One server off:** remove its entry from `~/.config/coala/mcps/mcp_servers.json`.  
- **On:** default when `--no-mcp` is not used; add or restore servers in `mcp_servers.json`.

## Providers and env

Set provider via `-p` or env `PROVIDER`. Set keys and URLs per provider (e.g. `OPENAI_API_KEY`, `GEMINI_API_KEY`, `OLLAMA_BASE_URL`). Optional: put vars in `~/.config/coala/env`.  
`coala config` — print current config paths and provider/model info.
