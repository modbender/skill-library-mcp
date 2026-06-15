---
title: Configuration
description: Skill Library MCP is zero-config — there are no environment variables. What you do choose is the install scope, plugin vs. server, and one behavioral toggle.
sidebar:
  order: 4
---

Skill Library MCP is **zero-config**. There are no environment variables, no API keys, no config file of its own, and no runtime knobs to tune. Run `npx -y skill-library-mcp` and it indexes its bundled skills on startup and serves them — that's it.

So this page isn't a list of settings. It's an honest rundown of the few decisions you actually make: *where* you install it, *how* you install it, and the one toggle that changes behavior at call time.

:::tip
If you came here looking for env vars to set, there aren't any. The server is intentionally self-contained: the skill data ships inside the package and is loaded from disk at launch.
:::

## Install scope: user vs. project

When you install through Claude Code, you choose a scope. This decides *who* sees the server, not how it behaves:

- **`--scope user`** — available across all your projects on this machine. This is what the install commands use by default, and it's the right choice for a general-purpose skill library you'll want everywhere.
- **Project scope** — limited to a single project (for example, Cursor's `.cursor/mcp.json` or VS Code's `.vscode/mcp.json` checked into a repo). Use this when you want the server tied to one codebase, or shared with a team via version control.

Both run the identical server and expose the same three tools — scope only controls where it's registered.

## Plugin vs. MCP server

There are two install shapes for Claude Code, and they're functionally equivalent:

| | Claude Code plugin | MCP server |
| --- | --- | --- |
| Install | `claude plugin install skill-library` | `claude mcp add skill-library -- npx -y skill-library-mcp` |
| Server lifecycle | Starts automatically with Claude Code | Registered as a managed MCP server |
| Tools exposed | `search_skill`, `load_skill`, `list_categories` | Same three |
| When to pick it | The simple, recommended default | You want to manage the server entry directly |

They do the same thing under the hood. Pick one — installing both just gives you two registrations of the same server. See [Installation](/skill-library-mcp/installation/) for the exact commands.

## The one behavioral toggle: `include_resources`

The only thing that changes the server's *behavior* at runtime is a parameter on `load_skill`, not a config setting:

- **`include_resources: false`** (the default) — `load_skill` returns just the skill's main `SKILL.md` content.
- **`include_resources: true`** — it also appends the skill's `resources/*.md` files, for the full deep-dive.

This is a per-call choice your assistant makes each time it loads a skill — there's no global default to flip. See [Usage](/skill-library-mcp/usage/#load_skill) for details.

## Where the skill data lives

You don't manage the skill data — it's bundled with the package. A skill is simply a directory containing:

- a **`SKILL.md`** file with YAML frontmatter (`name` and `description` are required), plus the skill's instructions, and
- an optional **`resources/`** directory of extra `.md` files that `load_skill` appends when `include_resources: true`.

When you run via `npx`, this data ships inside the published package; nothing is written to your project. If you want to add or modify skills, that's a [manual / local build](/skill-library-mcp/installation/#manual--local-build) and a contribution to the source repository, not a configuration step.

## Next steps

- [Usage](/skill-library-mcp/usage/) — the three tools and the recommended workflow.
- [MCP client setup](/skill-library-mcp/examples/mcp-client-setup/) — verify the install and troubleshoot.
