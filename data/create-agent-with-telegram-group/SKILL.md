---
name: create-agent-with-telegram-group
description: "Create a new OpenClaw agent and bind it to a dedicated Telegram
  group with workspace ~/claw-<agent-name>. Use when the user asks for
  one-agent-one-group setup, Telegram group binding, or repeatable agent
  provisioning. Always ask which model to use, ask for essential initialization
  choices (USER.md/IDENTITY.md/SOUL.md), and set group reply mode to
  no-mention-required. Explicit user confirmation is required before any
  high-privilege actions: modifying openclaw.json, triggering browser
  automation, or restarting the gateway."
---


# Agent Create + Dedicated Telegram Group

Create one dedicated Telegram group per agent, bind the agent to that group, and set an isolated workspace path.

## Script-first Rule

Prefer bundled scripts for deterministic steps (more stable + lower token cost). Only do manual JSON editing when scripts cannot cover a special case.

Use:
- `scripts/provision_config.py` for agent/config/binding/no-mention setup (with automatic backup of `openclaw.json`)
- `scripts/init_workspace.py` for `USER.md` / `IDENTITY.md` / `SOUL.md` initialization

## Access Scope

This skill accesses the following files on the host:
- `~/.openclaw/openclaw.json` — read (model discovery) and write (agent binding)
- `~/.openclaw/cron/jobs.json` — read-only (for job listing if needed)
- `~/claw-<agent-name>/` — workspace directory created by script
- `~/.openclaw/agents/<agent-id>/agent/` — directory created (no auth files copied)

## Config Safety

- `scripts/provision_config.py` reads and writes `~/.openclaw/openclaw.json`.
- By default it creates a backup file: `~/.openclaw/openclaw.json.bak.<timestamp>`.
- It updates only:
  - `agents.list` (add/update target agent) — does NOT copy auth credentials
  - `bindings` (add target telegram group binding)
  - `channels.telegram.groups.<chat_id>.requireMention=false`
  - `gateway.reload.mode` only if missing (sets default `hybrid`)
- The skill does NOT propagate API keys or auth tokens between agents.
- Gateway-level auth is inherited automatically; do not manually copy auth files.

## Inputs

Collect (before executing):
- `agent_name` (required)
- `model` (required): ask user explicitly which model to use; model options must be read live from the user’s `~/.openclaw/openclaw.json` (do not hardcode examples)
- Optional `telegram_group_title` override (custom group name)
- Initialization preferences (required ask):
  - whether to create/update `USER.md`
  - whether to create/update `IDENTITY.md`
  - whether to create/update `SOUL.md`
- If initialization is enabled, collect content fields before writing files:
  - `USER.md`: user name / preferred call name / language / goals / notes
  - `IDENTITY.md`: agent display name / vibe / emoji (optional)
  - `SOUL.md`: role/mission / tone / constraints (short bullet points)

Normalize `agent_name`:
- Keep lowercase letters, digits, and hyphens only.
- Replace spaces/underscores with `-`.
- Use this value in paths and IDs.

Telegram group title rule:
- If user provides `telegram_group_title`, use it directly.
- If not provided, generate default title from agent name in PascalCase.
  - Example: `test-skill` -> `TestSkill`, `bilingual-agent` -> `BilingualAgent`.

## Workflow

1. Read available models from `~/.openclaw/openclaw.json` first, then confirm inputs with user (agent name, model, init-file preferences, optional telegram group title).
2. Build workspace path as `~/claw-<agent-name>` and create it if missing.
3. Resolve group title:
   - custom `telegram_group_title` if provided
   - otherwise PascalCase(agent_name)
4. Create and bind Telegram group (use resolved group title):
   - use browser automation/user-account flow (Telegram bot API cannot reliably create groups)
   - **CONFIRM with user before triggering browser automation** (explicit yes/no required)
   - if browser automation is unavailable, request the minimal manual steps and resume
5. Create/update OpenClaw config via script (preferred):
   - **CONFIRM with user before modifying openclaw.json** (explicit yes/no required)
   - `python3 scripts/provision_config.py --agent-name <agent_name> --model <model> --chat-id <chat_id>`
   - this sets: agent entry, workspace, binding, and `requireMention=false`
6. Apply config and activate it:
   - if hot reload is enabled, verify reload logs show applied changes
   - if reload is off or not applied, **CONFIRM with user before restarting gateway** (explicit yes/no required)
   - restart gateway only after user approval
7. Bootstrap agent runtime files (required for first-run stability):
   - ensure `~/.openclaw/agents/<agent-id>/agent` exists
   - do NOT copy any auth files from other agents (this prevents credential/API key propagation)
   - new agents inherit authentication from the gateway's shared auth context automatically
   - do NOT manually copy or create auth-profiles.json, auth.json, or models.json
8. If initialization is requested, ask user for file content fields first, then write files:
   - collect required values for `USER.md` / `IDENTITY.md` / `SOUL.md`
   - then run: `python3 scripts/init_workspace.py --workspace <workspace> --agent-name <agent_name> [--with-user] [--with-identity] [--with-soul]`
   - if user provided custom text, apply it after script initialization (overwrite placeholders)
9. Ensure routing validity for current schema (no invalid allowFrom entries for groups).
10. Post-provision verification:
   - send a test message in group and ask user to send `ping`
   - confirm agent responds without `@mention`
11. Return completion summary with:
   - agent name
   - model
   - workspace path
   - group title
   - chat_id
   - no-mention reply mode (`enabled`/`disabled`)
   - status and next step (if any)

## Telegram Automation Rules

- Group creation/deletion and member operations should use browser automation (user-account flow).
- For browser flow, prefer Chrome relay profile for existing logged-in Telegram sessions.
- If no connected Chrome tab is available, ask user to attach once, then continue.
- If Telegram shows confirmation/captcha that cannot be automated, request one manual click, then resume.

## OpenClaw Command Discovery

Do not invent OpenClaw commands.

When agent create/update command syntax is unknown:
1. Run `openclaw help`.
2. If needed, run `openclaw <subcommand> --help` for the relevant subcommand.
3. Use only discovered command forms.

## Idempotency

- If `~/claw-<agent-name>` already exists, reuse it.
- If a same-name group already exists, confirm whether to reuse or create a fresh one.
- If agent already exists, update model/binding/workdir instead of duplicating.

## Reliability Checks (must do)

- Verify `requireMention=false` for the bound group.
- Verify gateway config actually applied:
  - check reload mode/status logs (`config hot reload applied`, `restarting telegram channel`)
  - if reload is `off` or not applied, restart gateway and re-check logs.
- Send one bot-originated test message to the new group, then require one live user `ping`.
- Verify agent replies without `@mention`.
- Do not claim success before `ping -> pong` verification passes.

## Failure Handling

If group creation succeeds but binding fails:
- Keep created group.
- Report exact failed step.
- Provide one-command resume instruction for the next run.

If chat_id cannot be resolved automatically:
- Report that as a partial success.
- Provide the shortest fallback step to fetch chat_id, then continue binding.

## Output Template

Return concise status:

- `agent`: <agent-name>
- `model`: <selected-model>
- `workspace`: `~/claw-<agent-name>`
- `telegram_group`: <title>
- `chat_id`: <id or PENDING>
- `binding`: <done|pending>
- `reply_without_mention`: <enabled|disabled>
- `initialized_files`: <USER.md, IDENTITY.md, SOUL.md or subset>
- `verification`: <passed|failed>
- `next_step`: <none or exact minimal action>
