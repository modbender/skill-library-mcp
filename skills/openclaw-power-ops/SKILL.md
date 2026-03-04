---
name: openclaw-ops
description: Operate and maintain OpenClaw installations — CLI commands, config management, channel/agent/model setup, security auditing, troubleshooting, and gateway administration. Use when adding Telegram bots, managing agents, changing models, editing config, running security audits, debugging gateway issues, rotating logs, managing cron, or any OpenClaw administrative task. Also use when asked to "set up OpenClaw," "add a channel," "fix the gateway," "audit security," or "check OpenClaw status."
---

# OpenClaw Operations

Comprehensive reference for administering OpenClaw via CLI. Covers channels, agents, models, config, gateway, security, and maintenance.

## Golden Rules

1. **Never edit `openclaw.json` directly.** Use `openclaw config set/get/unset` or dedicated subcommands.
2. **Always restart gateway after config changes:** `openclaw gateway restart`
3. **Telegram accounts: NO `agent` field inside account config.** Route via `bindings` array instead.
4. **Telegram `streaming`: must be string `"off"`, not boolean `false`.**
5. **JSON values in `config set` need `--strict-json`.**
6. **Verify after every change.** Run `openclaw status` or the relevant status command.

## Quick Diagnostics

```bash
openclaw status              # overview
openclaw status --deep       # detailed
openclaw doctor              # find problems
openclaw doctor --fix        # auto-fix what it can
openclaw gateway health      # gateway health check
openclaw security audit      # security scan
openclaw security audit --deep --fix  # deep scan + auto-fix
```

## Deep Audit with Claude Code

Load the docs *before* turning it loose — the difference is night and day.

```bash
cd ~/.openclaw
claude
# "Read https://docs.openclaw.ai/cli — the full CLI reference.
#  Now read the config and architecture pages too."
# Then: "Audit this workspace for security issues."
```

## CLI Reference

For the full CLI cheatsheet covering all commands, config paths, and examples:
→ Read [references/cli-cheatsheet.md](references/cli-cheatsheet.md)

## Security Audit Reference

For security findings, applied fixes, and remaining remediation items:
→ Read [references/security-audit.md](references/security-audit.md)

## Common Pitfalls

| Mistake | Fix |
|---------|-----|
| Put `agent` field in Telegram account config | Use `bindings` array at top level |
| Set `streaming: false` (boolean) | Must be `streaming: "off"` (string) |
| Edited openclaw.json directly | Use CLI commands; `openclaw config set` |
| Forgot gateway restart after config | Always `openclaw gateway restart` |
| Used `jared@` for VPS SSH | Must use `root@clawdbot` |
| Set `dmPolicy: "open"` with `allowFrom: ["*"]` | Use `"pairing"` or explicit user IDs |
| Set `controlUi.allowedOrigins: ["*"]` | Restrict to `["http://localhost:PORT"]` |

## Online Docs

- Full docs: https://docs.openclaw.ai
- CLI: https://docs.openclaw.ai/cli
- Channels: https://docs.openclaw.ai/cli/channels
- Agents: https://docs.openclaw.ai/cli/agents
- Models: https://docs.openclaw.ai/cli/models
- Config: https://docs.openclaw.ai/cli/config
