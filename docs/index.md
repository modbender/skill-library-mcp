---
title: Skill Library MCP
description: An MCP server that indexes 15,000+ curated skills and serves only the ones relevant to your task, keeping your AI assistant's context window lean.
sidebar:
  order: 1
---

Loading a skill into an AI coding assistant usually means pasting a long instruction document into your system prompt — and then doing it again for the next task, and the next, until your context window is full of guidance you mostly aren't using right now. Skill Library MCP flips that around.

It's an [MCP](https://modelcontextprotocol.io/) server that indexes **15,000+ curated skills** and serves them on demand. Instead of cramming every skill you *might* need into every conversation, your assistant searches the library, pulls in only the one or two skills relevant to the task at hand, and leaves the rest on disk. Your context window stays lean, and your assistant stays focused.

It runs with a single `npx` command, needs zero configuration, and works with any MCP-compatible client — Claude Code, Claude Desktop, Cursor, Windsurf, and VS Code.

## The problem it solves

A "skill" is a focused instruction document — how to debug a memory leak, how to set up Terraform, how to write a good React component. They're enormously useful, but they're expensive to keep loaded:

- Paste them all into your system prompt and you burn context (and money) on guidance the model isn't using for the current task.
- Paste them one at a time and you spend your day hunting for the right document and copying it in by hand.

Skill Library MCP makes skills a **searchable, on-demand resource**. The skills live in the server; your assistant asks for the one it needs, when it needs it. The only thing that ever enters your context is the skill that's actually relevant right now.

## Key features

- **15,000+ curated skills** — covering frontend, backend, DevOps, security, testing, databases, AI/LLM, automation, and more.
- **On-demand loading** — skills are fetched only when needed, never crammed into every conversation.
- **Smart, IDF-weighted search** — finds the right skill even from a natural-language query like *"help me debug a memory leak"*, not just exact keywords.
- **Browse by category** — 13 categories to discover skills you didn't know existed.
- **Works with any MCP client** — Claude Code, Claude Desktop, Cursor, Windsurf, VS Code, and others.
- **Zero config** — run it with `npx`, no setup, no API keys, no environment variables.

## A 30-second taste

Add the server to Claude Code:

```bash
claude mcp add skill-library --scope user -- npx -y skill-library-mcp
```

Now your assistant can reach for skills in plain language. Behind the scenes, that's two tool calls — one to find a skill, one to load it:

```text
search_skill({ query: "react performance" })
→ a ranked list of matching skills, e.g.
  - **react-performance** (react-performance) [+resources] — Profiling and optimizing React renders…

load_skill({ name: "react-performance" })
→ the full SKILL.md content, ready for the assistant to apply
```

That's the whole loop: **search**, then **load**. You usually don't type these yourself — you describe what you want, and the assistant calls the tools for you.

## Compatibility

| | Requirement |
| --- | --- |
| Node.js | 22 or newer |
| Package | `skill-library-mcp` (npm) |
| Transport | stdio (ESM-only) |
| Clients | Any MCP-compatible tool |

:::tip
There's nothing to configure. The server bundles its skill data and starts indexing on launch, so `npx -y skill-library-mcp` is all it takes to get running.
:::

## Where to next

- [Installation](/skill-library-mcp/installation/) — every install path: the Claude Code plugin, the MCP server, and the other clients.
- [Usage](/skill-library-mcp/usage/) — the three tools in depth, with the recommended browse → search → load workflow.
- [Configuration](/skill-library-mcp/configuration/) — install scopes, plugin vs. server, and the one behavioral toggle.
- [Search and load a skill](/skill-library-mcp/examples/search-and-load/) — a full end-to-end walkthrough.
