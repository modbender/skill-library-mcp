# Agents Configuration Reference

Full schema for the `agents` block in `openclaw.json`.

---

## Table of Contents
1. [Agents Block Schema](#agents-block-schema)
2. [Defaults](#defaults)
3. [Model Configuration](#model-configuration)
4. [Heartbeat](#heartbeat)
5. [Agent List](#agent-list)
6. [Per-Agent Overrides](#per-agent-overrides)
7. [Agent Identity](#agent-identity)
8. [Workspace Files](#workspace-files)
9. [Agent Routing](#agent-routing)
10. [Agent CLI](#agent-cli)

---

## Agents Block Schema

```json5
agents: {
  defaults: {
    workspace: "~/.openclaw/workspace",
    model: {
      primary: "anthropic/claude-opus-4-6"
    },
    models: {
      "summarization": "openai/gpt-4o-mini",
      "coding": "anthropic/claude-opus-4-6"
    },
    imageMaxDimensionPx: 1200,
    sandbox: { mode: "off" },
    heartbeat: {
      every: "30m",
      activeHours: {
        start: "08:00",
        end: "22:00",
        timezone: "America/New_York"
      }
    },
    maxConcurrent: null
  },
  list: [
    { agentId: "main" },
    { agentId: "work", workspace: "~/.openclaw/workspace-work" }
  ]
}
```

---

## Defaults

Applied to all agents unless overridden in the agent's `list` entry.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `workspace` | string | `"~/.openclaw/workspace"` | Default workspace directory path |
| `model` | object | - | Primary and fallback models |
| `models` | object | - | Per-task model overrides (keyed by task type) |
| `imageMaxDimensionPx` | number | `1200` | Max dimension for images sent to LLM (resized before sending) |
| `sandbox` | object | `{mode: "off"}` | Execution sandbox defaults |
| `heartbeat` | object | - | Proactive check-in schedule |
| `maxConcurrent` | number/null | `null` | Max concurrent requests per agent. `null` = unlimited. |
| `thinkingDefault` | boolean | - | Default thinking mode for agents |
| `verboseDefault` | boolean | - | Default verbose output mode |
| `elevatedDefault` | boolean | - | Default elevated permissions mode |
| `timeoutSeconds` | number | - | Request timeout in seconds |
| `contextTokens` | number | - | Context window size limit |
| `blockStreaming` | boolean | - | Block streaming responses |
| `humanDelay` | object | - | Simulated human-like typing delay |
| `typingMode` | string | - | Typing indicator behavior |

---

## Model Configuration

### Primary Model

```json5
model: {
  primary: "anthropic/claude-opus-4-6"   // Main model for conversation
}
```

The `primary` field accepts model IDs in `provider/model` format. Fallback models are tried in order if the primary fails.

### Per-Task Models

```json5
models: {
  "summarization": "openai/gpt-4o-mini",
  "coding": "anthropic/claude-opus-4-6",
  "vision": "google/gemini-2.0-flash"
}
```

Map task types to specific models. The agent uses the task-appropriate model when available.

### Image Model

```json5
imageModel: "openai/dall-e-3"     // Model for image generation
imageMaxDimensionPx: 1200         // Resize images before vision
```

---

## Heartbeat

Proactive agent wake-ups on a schedule.

```json5
heartbeat: {
  every: "30m",                    // Interval: "30m", "1h", "6h", "1d"
  activeHours: {
    start: "08:00",                // Only run during these hours
    end: "22:00",
    timezone: "America/New_York"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `every` | string | Duration between heartbeats. Supports `m` (minutes), `h` (hours), `d` (days). |
| `activeHours.start` | string | Start time in HH:MM format. |
| `activeHours.end` | string | End time in HH:MM format. |
| `activeHours.timezone` | string | IANA timezone string. |

**Heartbeat behavior:**
1. Agent wakes at configured interval
2. Reads `HEARTBEAT.md` from workspace
3. Executes defined checks
4. If action needed: takes action, sends notification
5. If nothing to do: responds `HEARTBEAT_OK` internally (silent)

**Disable heartbeat:** Set to `null` or omit entirely.

---

## Agent List

```json5
list: [
  {
    agentId: "main",                    // Required: unique identifier
    workspace: "~/.openclaw/workspace"  // Optional: overrides default
  },
  {
    agentId: "work",
    workspace: "~/.openclaw/workspace-work",
    model: { primary: "openai/gpt-4o" } // Override model for this agent
  }
]
```

Each agent in the list requires:
- `agentId` (string): Unique identifier. Used in routing and CLI commands.
- All other fields are optional and inherit from `defaults`.

---

## Per-Agent Overrides

Any field in `defaults` can be overridden per agent:

```json5
list: [
  {
    agentId: "main"
    // Inherits all defaults
  },
  {
    agentId: "work",
    workspace: "~/.openclaw/workspace-work",
    model: { primary: "openai/gpt-4o" },
    heartbeat: { every: "1h" },
    maxConcurrent: 3
  },
  {
    agentId: "research",
    workspace: "~/.openclaw/workspace-research",
    model: { primary: "google/gemini-2.0-flash" },
    maxConcurrent: 5,
    heartbeat: null     // No heartbeat for research agent
  }
]
```

---

## Agent Identity

Per-agent identity customization:

```json5
{
  agentId: "assistant",
  identity: {
    name: "Luna",
    theme: "professional",
    emoji: "🌙",
    avatar: "https://example.com/luna-avatar.png"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `identity.name` | string | Display name for the agent |
| `identity.theme` | string | Visual theme identifier |
| `identity.emoji` | string | Emoji shown in agent listings |
| `identity.avatar` | string | URL to avatar image |

---

## Workspace Files

Each workspace directory contains:

| File | Required | Purpose |
|------|----------|---------|
| `SOUL.md` | Yes | Persona, personality, core instructions |
| `AGENTS.md` | Yes | Agent definitions and routing bindings |
| `TOOLS.md` | No | Available commands reference |
| `IDENTITY.md` | No | Identity settings |
| `USER.md` | No | User context |
| `HEARTBEAT.md` | No | Proactive task definitions |
| `MEMORY.md` | No | Persistent memory store |
| `BOOTSTRAP.md` | No | First-time setup (runs once) |
| `skills/` | No | Per-workspace skills (highest loading priority) |

---

## Agent Routing

Routing determines which agent handles a given message. Priority order:

1. **Exact peer match** - Specific user ID to agent binding
2. **Parent peer match** - Thread inheritance
3. **Guild ID + Discord roles** - Role-based routing
4. **Guild ID alone** - Server-wide routing
5. **Team ID (Slack)** - Workspace-level routing
6. **Channel account ID** - Per-messenger-account routing
7. **Channel-wide match** - All messages on a channel
8. **Fallback to default** - Usually the `main` agent

Routing is configured in `AGENTS.md` and/or per-channel config blocks.

---

## Agent CLI

```bash
openclaw agents list                     # List all configured agents
openclaw agents status                   # Show agent status
openclaw agents status --agent-id work   # Status of specific agent
openclaw agents add --agent-id work --workspace ~/.openclaw/workspace-work
openclaw logs --agent-id main --follow   # View agent logs
openclaw system event --text "..." --mode now --agent-id main  # Manual trigger
```
