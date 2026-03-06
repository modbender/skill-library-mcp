# OpenClaw Config Snippets (starter kit)

These are **snippets**, not a full config. Apply them with `gateway config.patch` (or edit your `openclaw.json`).

## 1) Model allowlist for safe overrides
If you want to spawn subagents with specific models, add them to `agents.defaults.models`:

```json
{
  "agents": {
    "defaults": {
      "models": {
        "openai-codex/gpt-5.2": {},
        "openai-codex/gpt-5.3-codex": {}
      }
    }
  }
}
```

## 2) Heartbeat config (IMPORTANT)
The controller relies on an explicit heartbeat prompt that starts with:
- `TRIGGER=HEARTBEAT_TICK`

If you only set `agents.defaults.heartbeat.every` but do not set the prompt, heartbeats will not execute the controller contract.

Minimal snippet:

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "",
        "target": "last",
        "prompt": "TRIGGER=HEARTBEAT_TICK\nExecute HEARTBEAT.md exactly. Do not use context from prior chats."
      }
    }
  }
}
```

Notes:
- Keep `every: ""` (disabled) until you deliberately arm the system.
- `target: "last"` makes the heartbeat run in the last active session.

## 3) Default model split (example)
Main/orchestrator on an agentic model; coding subagents on a code-optimized model:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "openai-codex/gpt-5.2",
        "fallbacks": ["openai-codex/gpt-5.3-codex"]
      },
      "subagents": {
        "maxConcurrent": 2,
        "model": "openai-codex/gpt-5.3-codex"
      },
      "heartbeat": {
        "model": "openai-codex/gpt-5.2",
        "every": ""
      }
    }
  }
}
```

## 4) Cross-context message sends (optional)
If your control-plane destination is Telegram but you’re chatting somewhere else, you may need:

```json
{
  "tools": {
    "message": {
      "allowCrossContextSend": true,
      "crossContext": {
        "allowWithinProvider": true,
        "allowAcrossProviders": true
      }
    }
  }
}
```

## 5) Telegram group allowlist (optional)
If you run with `channels.telegram.groupPolicy="allowlist"`, you must explicitly allow the group.

```json
{
  "channels": {
    "telegram": {
      "groupPolicy": "allowlist",
      "groups": {
        "<TELEGRAM_GROUP_ID>": {
          "enabled": true,
          "requireMention": false,
          "groupPolicy": "open"
        }
      }
    }
  }
}
```
