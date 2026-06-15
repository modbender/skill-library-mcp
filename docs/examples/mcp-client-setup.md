---
title: MCP client setup
description: A worked example of wiring Skill Library MCP into Claude Code end to end, confirming the tools appear, and troubleshooting first-run hiccups.
sidebar:
  order: 2
---

This walks through wiring Skill Library MCP into **Claude Code** from nothing, verifying the three tools show up, and using them once. The same shape applies to any MCP client — only the registration command or config file changes (see [Installation](/skill-library-mcp/installation/) for the others).

## 1. Check your Node version

The server needs Node.js 22 or newer. Confirm before you start:

```bash
node --version
# v22.x.x or higher
```

If you're below 22, upgrade Node first — the package won't run otherwise.

## 2. Register the server

Add Skill Library MCP to Claude Code at user scope, so it's available across all your projects:

```bash
claude mcp add skill-library --scope user -- npx -y skill-library-mcp
```

The part after `--` is the command Claude Code will run to start the server: `npx -y skill-library-mcp`. The `-y` lets `npx` fetch the package without an interactive prompt.

:::tip
Prefer even less setup? Install the [Claude Code plugin](/skill-library-mcp/installation/#claude-code-plugin-recommended) instead — it starts the server automatically and you skip this step entirely. Use the plugin **or** this server registration, not both.
:::

## 3. Confirm the server is registered

List your configured MCP servers and check that `skill-library` is there:

```bash
claude mcp list
```

You should see `skill-library` in the output, pointing at `npx -y skill-library-mcp`.

## 4. Confirm the tools appear

Start Claude Code and check that the server's three tools are available:

```bash
claude
```

Inside the session, you can list MCP tools (for example with `/mcp`). You should see all three from `skill-library`:

- `search_skill`
- `load_skill`
- `list_categories`

If they're listed, the handshake succeeded and the index built — you're ready to use it.

## 5. Use it once

Ask in plain language and let the assistant drive the tools:

> "Browse the skill categories, then find and load a skill about writing good commit messages."

Under the hood that's `list_categories` → `search_skill({ query: "writing good commit messages" })` → `load_skill({ name: "<top result>" })`. You'll see the assistant call the tools and bring the skill's content into the conversation. See [Search and load a skill](/skill-library-mcp/examples/search-and-load/) for the raw call-by-call version.

## Troubleshooting

:::caution
**First run is slow, then fast.** The very first time the server starts, `npx` downloads `skill-library-mcp` from the registry before it can launch — so the tools may take a few extra seconds to appear, and the first run needs network access. Subsequent runs use the cached package and start quickly. If startup seems to hang on a fresh machine, give it a moment to finish the download.
:::

A few more things to check if the tools don't show up:

- **"Tools missing or server failed to start"** — re-check your Node version (`node --version` must be ≥ 22). An older Node is the most common cause; the ESM-only package won't load on it.
- **No network on first run** — the initial `npx` fetch needs internet. If you're offline, either run it once while connected to populate the cache, or use the [manual / local build](/skill-library-mcp/installation/#manual--local-build) and point the config at `node dist/index.js`.
- **Server registered but tools absent** — fully restart the client so it re-reads its MCP config and re-spawns the server.

## Next steps

- [Usage](/skill-library-mcp/usage/) — full reference for the three tools.
- [Configuration](/skill-library-mcp/configuration/) — install scopes, plugin vs. server, and the `include_resources` toggle.
