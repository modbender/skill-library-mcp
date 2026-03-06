# The Universal Interface Specification

Every tool is a sensor, an actuator, or both. Every tool should be accessible through multiple interfaces. We call this the Universal Interface.

This is the spec.

## The Six Interfaces

### 1. CLI

A shell command. The most universal interface. If it has a terminal, it works.

**Convention:** `package.json` with a `bin` field.

**Detection:** `pkg.bin` exists.

**Install:** `npm install -g .` or `npm link`.

```json
{
  "bin": {
    "wip-grok": "./cli.mjs"
  }
}
```

### 2. Module

An importable ES module. The programmatic interface. Other tools compose with it.

**Convention:** `package.json` with `main` or `exports` field. File is `core.mjs` by convention.

**Detection:** `pkg.main` or `pkg.exports` exists.

**Install:** `npm install <package>` or import directly from path.

```json
{
  "type": "module",
  "main": "core.mjs",
  "exports": {
    ".": "./core.mjs",
    "./cli": "./cli.mjs"
  }
}
```

### 3. MCP Server

A JSON-RPC server implementing the Model Context Protocol. Any MCP-compatible agent can use it.

**Convention:** `mcp-server.mjs` (or `.js`, `.ts`) at the repo root. Uses `@modelcontextprotocol/sdk`.

**Detection:** One of `mcp-server.mjs`, `mcp-server.js`, `mcp-server.ts`, `dist/mcp-server.js` exists.

**Install:** Add to `.mcp.json`:

```json
{
  "tool-name": {
    "command": "node",
    "args": ["/path/to/mcp-server.mjs"]
  }
}
```

### 4. OpenClaw Plugin

A plugin for OpenClaw agents. Lifecycle hooks, tool registration, settings.

**Convention:** `openclaw.plugin.json` at the repo root.

**Detection:** `openclaw.plugin.json` exists.

**Install:** Copy to `~/.openclaw/extensions/<name>/`, run `npm install --omit=dev`.

### 5. Skill (SKILL.md)

A markdown file that teaches agents when and how to use the tool. The instruction interface.

**Convention:** `SKILL.md` at the repo root. YAML frontmatter with name, version, description, metadata.

**Detection:** `SKILL.md` exists.

**Install:** Referenced by path. Agents read it when they need the tool.

```yaml
---
name: wip-grok
version: 1.0.0
description: xAI Grok API. Search the web, search X, generate images.
metadata:
  category: search,media
  capabilities:
    - web-search
    - image-generation
---
```

### 6. Claude Code Hook

A hook that runs during Claude Code's tool lifecycle (PreToolUse, Stop, etc.).

**Convention:** `guard.mjs` at repo root, or `claudeCode.hook` in `package.json`.

**Detection:** `guard.mjs` exists, or `pkg.claudeCode.hook` is defined.

**Install:** Added to `~/.claude/settings.json` under `hooks`.

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "node /path/to/guard.mjs",
        "timeout": 5
      }]
    }]
  }
}
```

## Architecture

Every repo that follows this spec has the same basic structure:

```
your-tool/
  core.mjs            pure logic, zero or minimal deps
  cli.mjs             thin CLI wrapper around core
  mcp-server.mjs      MCP server wrapping core functions as tools
  SKILL.md            agent instructions with YAML frontmatter
  package.json         name, bin, main, exports, type: module
  README.md            human documentation
```

Not every tool needs all six interfaces. Build the ones that make sense.

The minimum viable agent-native tool has two interfaces: **Module** (importable) and **Skill** (agent instructions). Add CLI for humans. Add MCP for agents that speak MCP. Add OpenClaw/CC Hook for specific platforms.

## The Reference Installer

`wip-install` is the reference implementation. It scans a repo, detects which interfaces exist, and installs them all. One command.

```bash
wip-install /path/to/repo          # local
wip-install org/repo               # from GitHub
wip-install --dry-run /path/to/repo # detect only
wip-install --json /path/to/repo    # JSON output
```

## Examples

| Repo | Interfaces | Type |
|------|------------|------|
| [wip-grok](https://github.com/wipcomputer/wip-grok) | CLI + Module + MCP + Skill | Sensor + Actuator |
| [wip-x](https://github.com/wipcomputer/wip-x) | CLI + Module + MCP + Skill | Sensor + Actuator |
| [wip-file-guard](https://github.com/wipcomputer/wip-file-guard) | CLI + OpenClaw + CC Hook | Actuator |
| [wip-markdown-viewer](https://github.com/wipcomputer/wip-markdown-viewer) | CLI + Module | Actuator |
