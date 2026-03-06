---
name: discord-context
description: Sync and cache per-thread context for Discord Forum channels. Use when handling /discord-context commands to poll active threads, list cached context, inspect a thread cache, or link a thread to a memory QMD file.
user-invocable: true
metadata: {"openclaw":{"requires":{"bins":["node"],"env":["DISCORD_TOKEN"]}}}
---

# discord-context

Run `node {baseDir}/scripts/discord-context-cli.js <command> ...`.

## Commands

- `poll [--guild <id>] [--forum <id>] [--workspace <path>]`
  - Pull active threads from Discord and refresh cache for new/updated threads.
  - Requires `DISCORD_TOKEN` plus guild/forum IDs (flags or env vars).

- `context [threadId] [--workspace <path>] [--json]`
  - Without `threadId`: list cached threads.
  - With `threadId`: print cached context and metadata for one thread.

- `link <threadId> <qmdName> [--workspace <path>]`
  - Link a thread to `memory/<qmdName>.md` and refresh cached context text.

## Environment

- `DISCORD_TOKEN` (required for `poll`)
- `DISCORD_GUILD_ID` (default guild id for `poll`)
- `DISCORD_FORUM_CHANNEL_ID` (default forum id for `poll`)
- `OPENCLAW_WORKSPACE` (defaults to `~/.openclaw/workspace`)

## Security Rules

- Never hardcode Discord tokens.
- Accept only numeric thread/guild/forum IDs.
- Accept only `[a-zA-Z0-9_-]+` for `qmdName`.
- Keep all reads/writes inside the workspace `memory/` tree.

## Paths

- Cache metadata: `memory/discord-cache/thread-<id>.json`
- Cache text: `memory/discord-cache/thread-<id>-context.txt`
- Source context files: `memory/*.md`
