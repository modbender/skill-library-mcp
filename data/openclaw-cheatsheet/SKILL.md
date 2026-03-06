---
name: openclaw-cheatsheet
description: Quick reference for every OpenClaw CLI command, sub-command, and flag. Use when the user asks about OpenClaw CLI usage (agent, message, config, gateway, cron, hooks, models, channels, directory, sessions, skills, agents, memory, health, status, doctor, logs), needs command examples, or needs to verify flags before running a command.
---

# OpenClaw Cheatsheet

Primary reference: `references/openclaw-cheatsheet.md`

## When to invoke

- User asks for an OpenClaw command, flag list, or usage example.
- User asks how to send messages, manage cron jobs, configure channels/models, run the gateway, etc.
- Before any operational change (`config set`, `gateway restart`, `cron add/edit`, `channels add/remove`, `models set`, `hooks install/enable`).
- User says "check the cheatsheet" or asks "what flags does X have?"

## Rules

1. Always read `references/openclaw-cheatsheet.md` before answering CLI questions — never guess flags.
2. If the cheatsheet doesn't cover a flag, verify with `openclaw <command> --help`.
3. Never run destructive or state-changing commands (`config set`, `gateway restart`, `cron rm`, `channels remove`, `reset`, `uninstall`) without confirming with the user first.
4. Keep answers concise — surface only the sections relevant to the request.

## Response pattern

1. Pull the relevant section(s) from the cheatsheet.
2. Provide 1-3 copy-paste-ready examples tailored to the user's context.
3. For dangerous operations (restart, update, config change, delete, uninstall), include a warning line before the command.
4. If the user is new, add a one-line explanation of what each flag does.

## Coverage (sections in the cheatsheet)

| Section | Key sub-commands |
|---------|-----------------|
| Global Options | `--dev`, `--profile`, `--no-color`, `-V` |
| Agent | `agent` (run a single agent turn) |
| Message | `send`, `read`, `edit`, `delete`, `search`, `broadcast`, `react`, `reactions`, `thread`, `pin/unpin/pins`, `poll`, `ban/kick/timeout`, `permissions`, `emoji`, `sticker`, `event`, `member`, `role`, `channel`, `voice` |
| Config | `get`, `set`, `unset`, wizard |
| Sessions | `sessions` (list, filter by active/store) |
| Gateway | `run`, `status`, `start/stop/restart`, `install/uninstall`, `discover`, `call`, `probe`, `usage-cost` |
| Daemon | Legacy alias for gateway service management |
| Skills | `list`, `info`, `check` |
| Agents | `list`, `add`, `delete`, `set-identity` |
| Memory | `search`, `index`, `status` |
| Cron | `add`, `edit`, `list`, `rm`, `run`, `runs`, `status`, `enable/disable` |
| Hooks | `list`, `info`, `enable/disable`, `install`, `check`, `update` |
| Models | `list`, `set`, `scan`, `status`, `aliases`, `auth`, `fallbacks/image-fallbacks` |
| Channels | `list`, `add`, `login/logout`, `remove`, `status`, `capabilities`, `resolve`, `logs` |
| Directory | `self`, `peers list`, `groups list`, `groups members` |
| Health / Status / Doctor / Logs | diagnostics and log tailing |
| Obsidian | `create`, `print`, `search`, `search-content`, `delete` |

## Reference

- `references/openclaw-cheatsheet.md` — authoritative, kept up-to-date with OpenClaw 2026.2.17+
