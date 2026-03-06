# OpenClaw Agent Config Schema

All agent configuration lives in `~/.openclaw/openclaw.json`.

## agents.list[] Entry

### Required Fields

```json
{
  "id": "wire",
  "name": "Wire",
  "workspace": "/home/archit/.openclaw/workspace-wire",
  "agentDir": "/home/archit/.openclaw/agents/wire/agent",
  "identity": { "name": "Wire" }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique agent ID (lowercase, no spaces). Used in cron jobs, bindings, logs. |
| `name` | string | Display name. Shown in Telegram, logs, UI. |
| `workspace` | string | Absolute path to workspace directory. Must be unique per agent. |
| `agentDir` | string | Absolute path to agent runtime directory. Must be unique per agent. |
| `identity.name` | string | Name the agent uses to identify itself. Usually matches `name`. |

### Optional Fields

```json
{
  "default": true,
  "model": {
    "primary": "moonshot/kimi-k2.5",
    "fallbacks": ["openrouter/deepseek/deepseek-v3.2"]
  },
  "groupChat": {
    "mentionPatterns": ["@wire", "@Wire"]
  },
  "heartbeat": { "every": "0" }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `default` | boolean | If `true`, receives all unrouted messages. Exactly ONE agent should be default. |
| `model.primary` | string | Primary model ID. Format: `provider/model-id`. |
| `model.fallbacks` | string[] | Fallback models tried in order when primary fails. |
| `groupChat.mentionPatterns` | string[] | Patterns that trigger this agent in group chats. |
| `heartbeat.every` | string | Heartbeat interval (e.g., `"30m"`, `"1h"`). `"0"` to disable. |

### Invalid Fields (Do NOT Use)

| Invalid | Causes | Use Instead |
|---------|--------|-------------|
| `heartbeat.enabled` | Config validation error | `heartbeat.every: "0"` |

## bindings[]

Route messages to specific agents.

```json
{
  "agentId": "wire",
  "match": {
    "channel": "telegram",
    "peer": { "kind": "group", "id": "-1003872746089" }
  }
}
```

| Field | Type | Values |
|-------|------|--------|
| `match.channel` | string | `"telegram"`, `"whatsapp"` |
| `match.peer.kind` | string | `"group"` or `"direct"` |
| `match.peer.id` | string | Group/chat ID (groups start with `-100`) |

Most-specific binding wins. No match → default agent.

## channels.telegram.groups

Per-group settings. **Presence in this object IS the allowlist.**

```json
"groups": {
  "-1003872746089": { "requireMention": false }
}
```

| Invalid | Use Instead |
|---------|-------------|
| `allowGroups` | List group in `groups` object |

## cron/jobs.json Entry

```json
{
  "id": "uuid-here",
  "agentId": "wire",
  "name": "Morning Briefing - AI",
  "enabled": true,
  "schedule": { "kind": "cron", "expr": "0 9 * * *", "tz": "America/Denver" },
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "The prompt text",
    "timeoutSeconds": 90
  },
  "delivery": { "mode": "none" }
}
```

| Field | Description |
|-------|-------------|
| `schedule.kind` | `"cron"` (cron expr) or `"every"` (interval via `everyMs` in ms) |
| `payload.message` | Prompt sent to agent. `$(...)` shell substitution works. |
| `payload.timeoutSeconds` | Max execution time. 90s for briefings, 120s for complex tasks. |
| `sessionTarget` | `"isolated"` for fresh session each run. Omit for shared session. |

### Session Isolation Decision

| Use `sessionTarget: "isolated"` | Omit (shared session) |
|---------------------------------|----------------------|
| Utility tasks (health reports) | Briefings that build context over time |
| One-shot tasks | Agents with Q&A groups needing cron context |

## Model IDs

| Model ID | Alias | Cost (in/out per M tokens) | Context |
|----------|-------|---------------------------|---------|
| `moonshot/kimi-k2.5` | kimi | $0.60 / $2.50 | 256K |
| `openrouter/deepseek/deepseek-v3.2` | deepseek | $0.24 / $0.38 | 164K |
| `anthropic/claude-sonnet-4-5-20250929` | sonnet | $3.00 / $15.00 | — |

Worker agents should exclude Claude Sonnet to save cost.
