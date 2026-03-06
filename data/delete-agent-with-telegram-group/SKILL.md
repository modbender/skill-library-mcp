---
name: delete-agent-with-telegram-group
description: Safely and thoroughly delete an OpenClaw agent and its artifacts. Use when user asks to remove an agent completely, including workspace, agent files under ~/.openclaw/agents, bindings, Telegram group routing config, dedicated Telegram group, and related cron jobs. Always run local cleanup via script with dry-run first; if Telegram group deletion is requested, require a separate explicit confirmation before any browser/session control or irreversible group deletion.
---

# Delete Agent (Clean)

Permanently remove an agent and its related local config/files.

## Safety Rules

- This is destructive. Always require explicit user confirmation.
- Enforce 3-step gate:
  1) run `--dry-run`,
  2) explicit confirmation for local deletion,
  3) separate explicit confirmation for Telegram browser/session-controlled group deletion.
- Ask user whether to also delete the dedicated Telegram group.
- Never auto-delete Telegram groups without the separate confirmation.
- Prefer script execution for local cleanup (stable, low token).

## Inputs

Collect:
- `agent_id` (required)
- `delete_workspace` (yes/no)
- `delete_telegram_group_config` (yes/no; usually yes)
- `delete_telegram_group` (yes/no; requires explicit confirmation)
- `delete_cron_jobs` (yes/no; usually yes)

## Script-first Commands

Dry-run:

```bash
python3 scripts/delete_agent.py --agent-id <agent_id> --dry-run
```

Execute (after confirmation):

```bash
python3 scripts/delete_agent.py --agent-id <agent_id> --yes --delete-workspace --delete-telegram-group-config --delete-cron-jobs
```

## Script Safety Guardrails

- `scripts/delete_agent.py` validates `agent_id` format: `[a-z0-9-]+`.
- It refuses deletion when target paths are outside allowed directories.
- Workspace deletion is allowed only when path is under user home and folder name starts with `claw-`.
- It creates backup files before writing config changes.

## What the script removes

- Agent entry in `~/.openclaw/openclaw.json` (`agents.list`)
- Agent bindings (`bindings[]` with matching `agentId`)
- Telegram group routing entries linked by those bindings
  - `channels.telegram.groups.<chat_id>`
- Agent directory:
  - `~/.openclaw/agents/<agent_id>`
- Workspace directory from agent config (if `--delete-workspace`)
- Cron jobs owned by this agent from `~/.openclaw/cron/jobs.json` (if `--delete-cron-jobs`)

## Dedicated Telegram Group Deletion

This skill does not bundle Telegram deletion automation code; it uses external browser automation tooling or manual user actions.

After local script deletion and only if user confirmed `delete_telegram_group=yes`:

1. Require a separate explicit confirmation: user agrees to browser/session control and irreversible group deletion.
2. Identify dedicated group `chat_id` from removed bindings.
3. Use browser automation (Telegram Web) to open the group and run `Delete Group`.
4. In Telegram delete dialog, enable `Delete for all members` when available, then confirm deletion.
5. Report final group status clearly: `deleted` / `left-only` / `pending-manual`.

## Post-step

- Surface backup files created by the script (`openclaw.json.bak.*`, `jobs.json.bak.*`) so user can retain recovery points.
- If gateway reload is available, let hot reload apply.
- If not applied, ask for explicit confirmation before restarting gateway, then verify logs.
- Return concise summary with removed items.
