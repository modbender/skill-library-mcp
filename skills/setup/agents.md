# Agent Configuration

## Core Settings

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/clawd",
      "model": {
        "primary": "anthropic/claude-sonnet-4-20250514",
        "fallbacks": ["openai/gpt-4o"]
      }
    }
  }
}
```

---

## Model Configuration

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-sonnet-4-20250514",
        "fallbacks": [
          "anthropic/claude-3-5-sonnet-20241022",
          "openai/gpt-4o"
        ]
      },
      "imageModel": {
        "primary": "anthropic/claude-sonnet-4-20250514"
      }
    }
  }
}
```

**Model format:** `provider/model-id`

**Providers:**
- `anthropic` — Claude models
- `openai` — GPT models
- `google` — Gemini models
- `openrouter` — Any model via OpenRouter

---

## Heartbeat (Proactive Check-ins)

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m",
        "target": "telegram",
        "to": "YOUR_USER_ID",
        "activeHours": {
          "start": "08:00",
          "end": "23:00",
          "timezone": "America/New_York"
        },
        "prompt": "Check HEARTBEAT.md and respond accordingly."
      }
    }
  }
}
```

**every:** Duration string (`30m`, `1h`, `2h30m`)
**target:** Channel to deliver to (`telegram`, `whatsapp`, `last`, `none`)

---

## Sub-agent Settings

```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "maxConcurrent": 5,
        "archiveAfterMinutes": 30,
        "model": "anthropic/claude-sonnet-4-20250514",
        "thinking": "low"
      }
    }
  }
}
```

**thinking levels:** `off`, `minimal`, `low`, `medium`, `high`

---

## Workspace Files

OpenClaw looks for these in your workspace:

| File | Purpose |
|------|---------|
| `AGENTS.md` | Instructions for the agent |
| `SOUL.md` | Persona and tone |
| `USER.md` | Info about you |
| `MEMORY.md` | Long-term memory |
| `HEARTBEAT.md` | Heartbeat task list |
| `TOOLS.md` | Tool usage guidance |
| `memory/*.md` | Additional memory files |

---

## Context and Memory

```json
{
  "agents": {
    "defaults": {
      "contextTokens": 128000,
      "bootstrapMaxChars": 20000,
      "memorySearch": {
        "enabled": true,
        "provider": "openai",
        "sources": ["memory", "sessions"]
      }
    }
  }
}
```

**memorySearch.provider:** `openai`, `gemini`, `voyage`, `local`

---

## Context Pruning

Automatically manage context length:

```json
{
  "agents": {
    "defaults": {
      "contextPruning": {
        "mode": "cache-ttl",
        "ttl": "2h",
        "keepLastAssistants": 3
      }
    }
  }
}
```

---

## Compaction (Memory Flush)

When context gets full, flush to memory:

```json
{
  "agents": {
    "defaults": {
      "compaction": {
        "memoryFlush": {
          "enabled": true,
          "softThresholdTokens": 100000
        }
      }
    }
  }
}
```

---

## Multiple Agents

Define different agents for different purposes:

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "default": true,
        "workspace": "~/clawd",
        "model": { "primary": "anthropic/claude-opus-4-5-20251101" }
      },
      {
        "id": "coding",
        "workspace": "~/projects/myapp",
        "model": { "primary": "anthropic/claude-sonnet-4-20250514" },
        "skills": ["github", "coding"]
      }
    ]
  }
}
```

---

## Agent Bindings

Route specific channels/groups to specific agents:

```json
{
  "bindings": [
    {
      "agentId": "coding",
      "match": {
        "channel": "telegram",
        "peer": { "kind": "group", "id": "-100GROUPID" }
      }
    }
  ]
}
```

---

## Sandbox Mode

Isolate sub-agents in Docker:

```json
{
  "agents": {
    "defaults": {
      "sandbox": {
        "mode": "non-main",
        "workspaceAccess": "ro",
        "docker": {
          "image": "node:20-slim",
          "memory": "2g",
          "cpus": 2
        }
      }
    }
  }
}
```

**mode:** `off`, `non-main` (sub-agents only), `all`
