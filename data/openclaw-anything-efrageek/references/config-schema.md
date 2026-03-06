# OpenClaw Configuration Reference

Reference normalized against:
- `https://docs.openclaw.ai/cli/config`
- `https://docs.openclaw.ai/gateway/configuration`

Last verified: 2026-02-17.

## Config File Location
Default state directory:
- `~/.openclaw`

Default config file:
- `~/.openclaw/openclaw.json5`

## CLI-first Config Management
Use CLI first to avoid manual syntax errors:

- `openclaw config --list`
- `openclaw config --get gateway.bind`
- `openclaw config --set gateway.bind=127.0.0.1`
- `openclaw config --set gateway.port=18789`

## Minimal Config Example
```json5
{
  gateway: {
    bind: "127.0.0.1",
    port: 18789,
    auth: {
      token: "replace-with-strong-token"
    }
  },
  channels: {
    whatsapp: {
      allowFrom: ["+1234567890"],
      groups: {
        "*": { requireMention: true }
      }
    }
  },
  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace"
    }
  },
  models: {
    default: "claude-3-5-sonnet-latest"
  }
}
```

## High-impact Keys
- `gateway.bind`: Interface binding. Keep `127.0.0.1` unless remote access is required.
- `gateway.port`: Gateway port (default `18789`).
- `gateway.auth.token`: Required when binding beyond loopback.
- `channels.*`: Channel-specific policy and auth settings.
- `agents.defaults.workspace`: Base workspace for agent tasks.
- `models.default`: Default model used by agents.

## Environment Variables
- `OPENCLAW_CONFIG_PATH`: Override config file path.
- `OPENCLAW_STATE_DIR`: Override state directory.
- `OPENCLAW_HOME`: Override OpenClaw home directory.
