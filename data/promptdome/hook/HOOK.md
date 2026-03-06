---
name: promptdome-gate
description: "Auto-scans all incoming messages for prompt injection using PromptDome before the model processes them"
metadata: { "openclaw": { "emoji": "🛡️", "events": ["message:received"], "requires": { "env": ["PROMPTDOME_API_KEY"] } } }
---

# PromptDome Gate

Automatic prompt injection screening for all incoming messages via the PromptDome API.

Fires on every `message:received` event. Calls `https://promptdome.cyberforge.one/api/v1/shield`
and injects a warning into the conversation if injection signals are detected, so the model
sees the flag **before** it processes the original message.

## Behaviour

- **BLOCK** (score ≥ 70): Injects a ⚠️ `[PROMPTDOME BLOCK]` warning into the conversation
- **WARN** (score ≥ 40): Injects a lighter caution note
- **ALLOW**: Silent pass-through — zero overhead in conversation

## Fail-Open Policy

If the PromptDome API is unreachable or returns an error, the message passes through without
a warning. This prevents false positives from API downtime breaking normal operation.

## Configuration

Requires `PROMPTDOME_API_KEY` environment variable. Set it in your shell profile or
in `~/.openclaw/openclaw.json` under `env`:

```json
{
  "env": {
    "PROMPTDOME_API_KEY": "sk_shield_live_..."
  }
}
```

## Logs

All scan results logged to `~/.openclaw/logs/promptdome-gate.log`.
