---
name: stdio-skill
description: "Stdin/stdout file inbox/outbox bridge for passing files to/from Clawdbot using an MCP stdio server. Use when you want a simple filesystem-backed dropbox: accept files into an inbox, move to tmp for processing, and emit deliverables to an outbox (or a specified path)."
---

# stdio-skill

Implement and use a local MCP **stdio** server that provides a simple inbox/outbox workflow backed by directories on disk.

Paths (workspace-relative):
- `stdio/inbox/` — user drops inputs here
- `stdio/tmp/` — scratch area (move/copy inputs here for processing)
- `stdio/outbox/` — put deliverables here for pickup

## Start the MCP server (via mcporter)

This repo config should include an MCP server named `stdio-skill`.

- List tools:
  - `mcporter list stdio-skill --schema --timeout 120000 --json`

## Tooling model

Prefer:
1) `stdio-skill.stdio_list` to see what’s waiting.
2) `stdio-skill.stdio_read` (base64) to pull file contents.
3) `stdio-skill.stdio_move` to move an item to `tmp` once you’ve claimed it.
4) Write outputs with `stdio-skill.stdio_write` (base64) into `outbox` unless the user provided an explicit destination path.

No deprecated aliases: use the `stdio_*` tools only.

## Notes

- This skill is intentionally dumb/simple: it does not interpret file formats.
- It is safe-by-default: operations are restricted to the three directories above.
- For large files: prefer passing by path + moving files, not embedding giant base64 blobs in chat.
