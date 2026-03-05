---
name: claw-agent-creator-archit
description: >
  Create new OpenClaw agents for Arch's multi-agent system. Use this skill when asked to
  create, add, or set up a new OpenClaw agent, or when adding an agent to the system defined
  in ~/.openclaw/. Covers the full lifecycle: directory creation, workspace files (SOUL.md,
  IDENTITY.md, etc.), openclaw.json config, Telegram routing (bindings + groups + mention
  patterns), cron job creation with proper prompt engineering, and gateway restart. Includes
  hard-won lessons from building the Wire (News) agent — the first non-default agent in the
  system. Also use when modifying existing agent configs, adding cron jobs to agents, or
  debugging agent routing issues.
---

# OpenClaw Agent Creator

Create and configure agents for Arch's OpenClaw multi-agent system at `~/.openclaw/`.

## System Context

- **Owner**: Archit (Arch), Linux user `archit`, timezone America/Denver
- **Gateway**: Single process on port 18789 managing all agents
- **Bot**: One Telegram bot shared across all agents — routing determines which agent handles which chat
- **Existing agents**: Check `~/.openclaw/openclaw.json` → `agents.list[]` for current roster
- **Implementation history**: See `~/.openclaw/implementation-docs/` for the Wire agent reference implementation

## Agent Creation Workflow

### 1. Gather Requirements

Before creating anything, clarify with Arch:
- Agent name and ID (lowercase, no spaces for ID)
- Role and responsibilities (specific, not vague)
- Model tier: cheap (Kimi K2.5 only) or full cascade (include Claude Sonnet)
- Whether it needs a Telegram group for Q&A
- Whether it needs cron jobs (what schedule, what tasks)
- Whether heartbeat should be enabled or disabled

### 2. Stop the Gateway

```bash
openclaw gateway stop
```

**MANDATORY** before editing `openclaw.json` or `cron/jobs.json`. The gateway actively writes to `jobs.json` (updating job state after each cron run). Editing while the gateway runs causes race conditions and data loss.

### 3. Backup Config

```bash
cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup.$(date +%Y%m%d%H%M%S)
```

### 4. Create Directories

```bash
mkdir -p ~/.openclaw/workspace-<agent_id>/memory
mkdir -p ~/.openclaw/agents/<agent_id>/agent
```

**NEVER** reuse `agentDir` across agents — causes auth/session collisions.

### 5. Write Workspace Files

Use templates from `assets/templates/` as starting points. Every agent needs:

| File | Purpose | Required |
|------|---------|----------|
| `SOUL.md` | Personality, role, responsibilities, behavioral modes | Yes |
| `IDENTITY.md` | Quick-reference card (name, role, emoji) | Yes |
| `USER.md` | About Arch (copy from any existing agent workspace) | Yes |
| `AGENTS.md` | Workspace rules (boot sequence, memory, safety) | Yes |
| `HEARTBEAT.md` | Periodic task checklist (or comment if disabled) | Yes |

**SOUL.md is the most important file.** Be specific about responsibilities. Include behavioral modes if the agent operates differently in different contexts (e.g., briefing mode vs chat mode).

### 6. Edit openclaw.json — Agent Entry

Add to `agents.list[]`. See [references/config-schema.md](references/config-schema.md) for all valid fields.

Minimal entry:
```json
{
  "id": "<agent_id>",
  "name": "<Display Name>",
  "workspace": "/home/archit/.openclaw/workspace-<agent_id>",
  "agentDir": "/home/archit/.openclaw/agents/<agent_id>/agent",
  "identity": { "name": "<Display Name>" }
}
```

Common additions:
- `"model"` — Override the default model cascade. Exclude expensive models for worker agents.
- `"heartbeat": { "every": "0" }` — Disable heartbeat for cron-only agents.
- `"groupChat": { "mentionPatterns": ["@<id>", "@<Name>"] }` — Enable @mentions in groups.

**Only ONE agent** should have `"default": true` (currently Fossil). The default agent receives all unrouted messages.

### 7. Edit openclaw.json — Telegram Routing (if needed)

**THREE separate config changes are required.** Missing any one causes silent failures. See [references/telegram-routing.md](references/telegram-routing.md) for the full explanation.

1. **Group config** in `channels.telegram.groups`:
   ```json
   "-100XXXXXXXXXX": { "requireMention": false }
   ```

2. **Binding** in `bindings[]`:
   ```json
   { "agentId": "<id>", "match": { "channel": "telegram", "peer": { "kind": "group", "id": "-100XXXXXXXXXX" } } }
   ```

3. **Mention patterns** on the agent entry (already done in step 6 if `groupChat` was added).

### 8. Create Cron Jobs (if needed)

Edit `cron/jobs.json`. Every cron job prompt MUST include:
- **Dynamic group ID resolution preamble** (NEVER hardcode Telegram group IDs):
  ```
  FIRST: Resolve your Telegram group ID by running:
  jq -r '.bindings[] | select(.agentId == "<agent_id>") | .match.peer.id' ~/.openclaw/openclaw.json
  Use the output as the target for all Telegram messages in this task.
  ```
- **Date injection**: `$(date '+%A, %B %d, %Y')` after the preamble
- **Explicit constraints**: source allowlists, recency rules, format templates
- **Delivery instructions**: use `target='<AGENT_GROUP_ID>'` placeholder (resolved by the preamble)

This self-healing pattern ensures cron jobs survive Telegram group ID migrations. See [references/prompt-patterns.md](references/prompt-patterns.md) for full patterns and [references/telegram-routing.md](references/telegram-routing.md) for why this matters.

**Critical**: If copying files or prompts from another agent's workspace, **grep for hardcoded paths** and update them.

### 9. Restart Gateway and Verify

```bash
openclaw gateway start
```

Verify in logs:
- Agent registered: `agent registered: <id>`
- Messages route correctly: `lane enqueue: lane=session:agent:<id>:...`

If messages to a Telegram group show `skip: no-mention`, the `channels.telegram.groups` config is missing (see [references/bugs-and-pitfalls.md](references/bugs-and-pitfalls.md)).

## Reference Files

| File | When to Read |
|------|-------------|
| [references/config-schema.md](references/config-schema.md) | When writing agent config or cron jobs |
| [references/telegram-routing.md](references/telegram-routing.md) | When setting up Telegram group routing |
| [references/prompt-patterns.md](references/prompt-patterns.md) | When writing cron job prompts |
| [references/bugs-and-pitfalls.md](references/bugs-and-pitfalls.md) | When debugging issues or before any config edit |

## Template Files

Starter templates for workspace files are in `assets/templates/`. Copy and customize per agent.
