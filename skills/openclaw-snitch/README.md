# openclaw-snitch

A configurable blocklist guard for [OpenClaw](https://openclaw.ai). Hard-blocks tool calls matching banned patterns, injects a security directive at agent bootstrap, warns on incoming messages, and broadcasts Telegram alerts to all `allowFrom` recipients.

## In action

A user asks their OpenClaw agent to install a blocked skill. Snitch catches every attempt and fires a Telegram alert in real time:

```
User: hi. can you download the clawhub skill please

🚨🚔🚨 SECURITY ALERT 🚨🚔🚨

A clawhub tool invocation was detected and BLOCKED.
The session has been stopped. This incident has been logged.

clawhub is prohibited by system security policy.

tool: edit
session: agent:main:main
agent: main
```

The agent tried `edit`, then `browser`, then `gateway`, then `exec` — each attempt blocked and reported. When it tried to disable the guard itself, that got blocked too.

## Why

The [ClawHub](https://clawhub.ai) skill ecosystem contains malicious skills that can exfiltrate credentials, modify your agent config, or backdoor your workspace. `openclaw-snitch` provides a multi-layer defense:

1. **Bootstrap directive** — injected into every agent context, telling the LLM not to invoke blocked tools
2. **Message warning** — flags incoming messages that reference blocked terms before the agent sees them
3. **Hard block** — intercepts and kills the tool call if the agent tries anyway
4. **Telegram broadcast** — alerts all `allowFrom` users the moment a block fires

## Install

```bash
openclaw plugins install openclaw-snitch
```

Then add to `openclaw.json`:

```json
{
  "plugins": {
    "allow": ["openclaw-snitch"]
  }
}
```

### Hooks (optional but recommended)

Copy the hook directories into your workspace:

```bash
cp -r ~/.openclaw/workspace/skills/openclaw-snitch/hooks/snitch-bootstrap ~/.openclaw/hooks/snitch-bootstrap
cp -r ~/.openclaw/workspace/skills/openclaw-snitch/hooks/snitch-message-guard ~/.openclaw/hooks/snitch-message-guard
```

Then add to `openclaw.json` hooks config:

```json
{
  "hooks": {
    "snitch-bootstrap": { "enabled": true },
    "snitch-message-guard": { "enabled": true }
  }
}
```

## Configuration

In `openclaw.json` under `plugins.config.openclaw-snitch`:

```json
{
  "plugins": {
    "config": {
      "openclaw-snitch": {
        "blocklist": ["clawhub", "clawdhub", "myothertool"],
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
| `bootstrapDirective` | `true` | Inject a security directive into every agent bootstrap context prohibiting blocked tools |

### Hook blocklist (env var)

The hooks read `SNITCH_BLOCKLIST` (comma-separated) if set, otherwise fall back to the defaults. Useful for customizing without editing hook files.

## Security Notes

- **Lock down the plugin files after install**: `chmod -R a-w ~/.openclaw/workspace/skills/openclaw-snitch` so the agent can't self-modify
- **The bootstrap and message hooks are the most tamper-resistant layers** — they live in `~/.openclaw/hooks/` which loads unconditionally without a trust model
- The plugin layer requires `plugins.allow` — if an agent edits `openclaw.json` and removes it, the hooks remain active as a fallback

## License

MIT
