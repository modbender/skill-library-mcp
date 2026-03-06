###### WIP Computer
# Universal Installer ... Reference

Sensors/actuators, the interface table, how to build it, the installer, and real examples.

## Sensors and Actuators

Every tool is a sensor, an actuator, or both:

**Sensors** convert state into data:
- Search the web (wip-grok search_web)
- Search X/Twitter (wip-grok search_x, wip-x search_recent)
- Fetch a post (wip-x fetch_post)
- Read bookmarks (wip-x get_bookmarks)
- Check system health (wip-healthcheck)

**Actuators** convert intent into action:
- Generate an image (wip-grok generate_image)
- Post a tweet (wip-x post_tweet)
- Guard a file from edits (wip-file-guard)
- Generate a video (wip-grok generate_video)

## The Universal Interface

Agents don't all speak the same language. Some run shell commands. Some import modules. Some talk MCP. Some read markdown instructions.

So every tool should expose multiple interfaces into the same core logic:

| Interface | What | Who uses it |
|-----------|------|-------------|
| **CLI** | Shell command | Humans, any agent with bash |
| **Module** | ES import | Other tools, scripts |
| **MCP Server** | JSON-RPC over stdio | Claude Code, Cursor, any MCP client |
| **OpenClaw Plugin** | Lifecycle hooks + tools | OpenClaw agents |
| **Skill** | Markdown instructions (SKILL.md) | Any agent that reads files |
| **Claude Code Hook** | PreToolUse/Stop events | Claude Code |

Not every tool needs all six. Build what makes sense. But the more interfaces you expose, the more agents can use your tool.

See [SPEC.md](SPEC.md) for the full specification.

## How to Build It

The architecture is simple. Four files:

```
your-tool/
  core.mjs            <- pure logic, zero deps if possible
  cli.mjs             <- thin CLI wrapper
  mcp-server.mjs      <- MCP server wrapping core as tools
  SKILL.md            <- when/how to use it, for agents
```

`core.mjs` does the work. Everything else is a thin wrapper. CLI parses argv and calls core. MCP server maps tools to core functions. SKILL.md teaches agents when to call what.

This means one codebase, one set of tests, multiple interfaces.

## The Reference Installer

`wip-install` scans any repo, detects which interfaces exist, and installs them all. One command.

```bash
# From GitHub
wip-install wipcomputer/wip-grok

# From a local path
wip-install /path/to/repo

# Detect only (no install)
wip-install --dry-run wipcomputer/wip-x

# Machine-readable output
wip-install --json /path/to/repo
```

### Example Output

```
  Installing: wip-grok
  ────────────────────────────────────────
  Detected 4 interface(s): cli, module, mcp, skill

  ✓ CLI: wip-grok installed globally
  ✓ Module: import from "core.mjs"
  MCP Server detected: mcp-server.mjs
  ✓ Skill: SKILL.md available

  Done. 4 interface(s) processed.
```

### What It Detects

| Pattern | Interface | Install action |
|---------|-----------|---------------|
| `package.json` with `bin` | CLI | `npm install -g` |
| `main` or `exports` in `package.json` | Module | Reports import path |
| `mcp-server.mjs` | MCP | Prints `.mcp.json` config |
| `openclaw.plugin.json` | OpenClaw | Copies to `~/.openclaw/extensions/` |
| `SKILL.md` | Skill | Reports path |
| `guard.mjs` or `claudeCode.hook` | CC Hook | Adds to `~/.claude/settings.json` |

## Real Examples

| Tool | Type | Interfaces | What it does |
|------|------|------------|-------------|
| [wip-grok](https://github.com/wipcomputer/wip-grok) | Sensor + Actuator | CLI + Module + MCP + Skill | xAI Grok API: search web/X, generate images/video |
| [wip-x](https://github.com/wipcomputer/wip-x) | Sensor + Actuator | CLI + Module + MCP + Skill | X Platform API: read/write tweets, bookmarks |
| [wip-file-guard](https://github.com/wipcomputer/wip-file-guard) | Actuator | CLI + OpenClaw + CC Hook | Protect files from AI edits |
| [wip-healthcheck](https://github.com/wipcomputer/wip-healthcheck) | Sensor | CLI + Module | System health monitoring |

## Supported Tools

Works with any AI agent or coding tool that can run shell commands:

| Tool | How |
|------|-----|
| Claude Code | CLI via bash, hooks via settings.json, MCP via .mcp.json |
| OpenAI Codex CLI | CLI via bash, skills via AGENTS.md |
| Cursor | CLI via terminal, MCP via config |
| Windsurf | CLI via terminal, MCP via config |
| OpenClaw | Plugins, skills, MCP |
| Any agent | CLI works everywhere. If it has a shell, it works. |
