---
title: Installation
description: Install Skill Library MCP via the Claude Code plugin, as an MCP server, or wired into Claude Desktop, Cursor, Windsurf, or VS Code.
sidebar:
  order: 2
---

Skill Library MCP runs straight from npm with `npx` — there's nothing to build or globally install, and no configuration to write. Pick the install path that matches your tool below.

## Requirements

- **Node.js 22 or newer** (`node --version` to check). The package is ESM-only and targets Node 22.
- An MCP-compatible client (Claude Code, Claude Desktop, Cursor, Windsurf, VS Code, or any other).

:::caution
The **Claude Code plugin** and the **Claude Code MCP server** are two ways to do the *same thing* — both end up running `skill-library-mcp` and exposing the same three tools. Pick **one**, not both. The plugin is the simpler, recommended path; the MCP-server install is there if you'd rather manage the server entry directly.
:::

## Claude Code plugin (recommended)

Add the marketplace source, then install the plugin:

```bash
claude plugin marketplace add https://github.com/modbender/skill-library-mcp.git --scope user
claude plugin install skill-library --scope user
```

The MCP server starts automatically whenever Claude Code launches — there's no separate server entry to manage. That's the whole install.

## Claude Code (MCP server)

If you'd rather register the server yourself instead of using the plugin, add it directly:

```bash
claude mcp add skill-library --scope user -- npx -y skill-library-mcp
```

This registers `skill-library` as an MCP server that Claude Code spawns via `npx`. See [MCP client setup](/skill-library-mcp/examples/mcp-client-setup/) for a worked end-to-end example, including how to verify the tools appear.

## Other MCP clients

Every other client uses the same idea: a small JSON entry that tells the client to run `npx -y skill-library-mcp`. The server key is `skill-library`. Add the snippet below to the config file your client expects.

### Claude Desktop

Add to your `claude_desktop_config.json` ([location varies by OS](https://modelcontextprotocol.io/quickstart/user)):

```json
{
  "mcpServers": {
    "skill-library": {
      "command": "npx",
      "args": ["-y", "skill-library-mcp"]
    }
  }
}
```

### Cursor

Add to `.cursor/mcp.json` (project-scoped) or `~/.cursor/mcp.json` (global):

```json
{
  "mcpServers": {
    "skill-library": {
      "command": "npx",
      "args": ["-y", "skill-library-mcp"]
    }
  }
}
```

### Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "skill-library": {
      "command": "npx",
      "args": ["-y", "skill-library-mcp"]
    }
  }
}
```

### VS Code (Copilot)

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "skill-library": {
      "command": "npx",
      "args": ["-y", "skill-library-mcp"]
    }
  }
}
```

:::caution
VS Code uses the key `"servers"`, not `"mcpServers"` like the other clients. Copy the snippet that matches your client exactly — the wrapper key is the one thing that differs.
:::

## Manual / local build

If you want to run the server from a local checkout — to pin a specific commit, contribute skills, or work offline — clone and build it:

```bash
git clone https://github.com/modbender/skill-library-mcp
cd skill-library-mcp
pnpm install
pnpm build
```

Then point your MCP config at the built entry point instead of `npx`:

```json
{
  "mcpServers": {
    "skill-library": {
      "command": "node",
      "args": ["/path/to/skill-library-mcp/dist/index.js"]
    }
  }
}
```

:::tip
For everyday use, prefer `npx -y skill-library-mcp` — it always fetches the latest published version and needs no checkout. Reach for the manual build only when you specifically need a local copy.
:::

## Next steps

- [Usage](/skill-library-mcp/usage/) — the three tools and the browse → search → load workflow.
- [MCP client setup](/skill-library-mcp/examples/mcp-client-setup/) — wire it into Claude Code end to end and confirm it works.
