---
name: discord-dual-bot-orchestrator
description: Set up and operate dual Discord bots on one machine with isolated memory, channel allowlists, mention-gated reviewer bot behavior, optional one-way reviewer-to-primary context bridge, and safe backup/rollback. Use when configuring two bots (primary + reviewer), tuning reply rules, or recovering from bad config iterations.
---

# Discord Dual Bot Orchestrator

Use placeholders only. Never store real secrets in this skill.

## Required placeholders
- `BOT_A_NAME`
- `BOT_B_NAME`
- `BOT_A_TOKEN`
- `BOT_B_TOKEN`
- `BOT_A_ID`
- `BOT_B_ID`
- `GUILD_ID`
- `CHANNEL_ID_LIST` (comma-separated)
- `BASE_DIR` (example: `~/.openclaw/bots`)

## Workflow

1. Create isolated workspaces for bot-a and bot-b.
2. Write `.env` files from template using placeholders.
3. Apply channel allowlist policy:
   - Bot-A: primary chat policy
   - Bot-B: `requireMention=true` on allowlisted channels
4. Optional: enable one-way bridge (`bot-b -> bot-a`) for reviewer feedback.
5. Create backup snapshot before each risky iteration.
6. If behavior regresses, rollback snapshot and restart both gateways.

## Commands

### Initialize layout
Run:
```bash
scripts/init_dual_bot.sh
```

### Apply policy (placeholder-safe)
Run:
```bash
scripts/apply_policy.sh
```

### Backup current state
Run:
```bash
scripts/backup_state.sh
```

### Rollback from backup dir
Run:
```bash
scripts/rollback_state.sh <BACKUP_DIR>
```

## Guardrails
- Keep `BOT_B_TOKEN` separate from `BOT_A_TOKEN`.
- Keep bot-b mention-gated in group channels.
- Never enable bidirectional auto-bridge (avoids reply loops).
- Always backup before patching runtime files.
