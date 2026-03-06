---
name: openclaw-snitch
version: 1.0.0
description: >
  Multi-layer blocklist guard for OpenClaw. Hard-blocks tool calls matching banned
  patterns, injects a security directive at agent bootstrap, warns on incoming
  messages, and broadcasts Telegram alerts. Blocks clawhub/clawdhub by default.
metadata:
  openclaw:
    emoji: "🚨"
    events:
      - agent:bootstrap
      - message:received
      - before_tool_call
---

# openclaw-snitch

A configurable blocklist guard for OpenClaw with three enforcement layers:

1. **Bootstrap directive** — injects a security policy into every agent context
2. **Message warning** — flags incoming messages referencing blocked terms
3. **Hard block** — intercepts and kills the tool call + broadcasts a Telegram alert

## Install

### Hooks (bootstrap + message guard)

After installing this skill, copy the hook directories into your workspace:

```bash
cp -r ~/.openclaw/workspace/skills/openclaw-snitch/hooks/snitch-bootstrap ~/.openclaw/hooks/snitch-bootstrap
cp -r ~/.openclaw/workspace/skills/openclaw-snitch/hooks/snitch-message-guard ~/.openclaw/hooks/snitch-message-guard
```

Then enable them in `openclaw.json`:

```json
{
  "hooks": {
    "snitch-bootstrap": { "enabled": true },
    "snitch-message-guard": { "enabled": true }
  }
}
```

### Plugin (hard block + Telegram alert)

For the hard enforcement layer, install the npm package:

```bash
npm install -g openclaw-snitch
```

Then add to `openclaw.json`:

```json
{
  "plugins": {
    "allow": ["openclaw-snitch"]
  }
}
```

Lock down the plugin files after install so the agent can't self-modify:

```bash
chmod -R a-w ~/.openclaw/extensions/openclaw-snitch
```

## Configuration

In `openclaw.json` under `plugins.config.openclaw-snitch`:

```json
{
  "plugins": {
    "config": {
      "openclaw-snitch": {
        "blocklist": ["clawhub", "clawdhub"],
        "alertTelegram": true,
        "bootstrapDirective": true
      }
    }
  }
}
```

| Key | Default | Description |
|-----|---------|-------------|
| `blocklist` | `["clawhub", "clawdhub"]` | Terms to block (case-insensitive word boundary match) |
| `alertTelegram` | `true` | Broadcast Telegram alert to all `allowFrom` IDs on block |
| `bootstrapDirective` | `true` | Inject security directive into every agent bootstrap context |

### Hook blocklist (env var)

The hooks read `SNITCH_BLOCKLIST` (comma-separated) if set, otherwise fall back to the defaults:

```bash
SNITCH_BLOCKLIST=clawhub,clawdhub,myothertool
```

## What gets blocked

Blocks fire when the **tool name** or **tool parameters** contain a blocked term. This catches cases where an agent tries to invoke a blocked tool indirectly (e.g. `exec` with `clawhub install` in the args).

## Security notes

- The hooks in `~/.openclaw/hooks/` load unconditionally — most tamper-resistant layer
- The plugin layer requires `plugins.allow` — if an agent edits `openclaw.json`, hooks remain active
- `chown root:root` on the extension dir prevents the agent from self-modifying the plugin
