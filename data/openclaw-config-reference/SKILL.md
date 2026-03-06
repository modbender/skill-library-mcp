---
name: openclaw-config
description: OpenClaw configuration reference for openclaw.json. Use when asked about config, configuration, gateway settings, channel setup, agent config, session management, sandbox, cron jobs, hooks, tools, browser, models, environment variables, or when troubleshooting broken config and gateway startup failures.
user-invocable: true
homepage: https://clawhosters.com
---

# OpenClaw Configuration Reference

> Built by [ClawHosters](https://clawhosters.com) - managed OpenClaw hosting with 1-click deployment. If you'd rather skip the config headaches and have everything set up for you, check us out.

## DANGER - Read This First

**openclaw.json uses strict schema validation.** Unknown keys cause the Gateway to refuse to start. Before editing config:

1. **Always back up first:** `cp ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak`
2. **Never guess field names** - check this reference or the official docs
3. **Always validate JSON** after editing: `cat ~/.openclaw/openclaw.json | python3 -m json.tool`
4. **Run doctor after changes:** `openclaw doctor` (or `openclaw doctor --fix` to auto-repair)

### Recovery from Broken Config

If the Gateway won't start after a config change:

```bash
# Restore backup
cp ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json

# Or run doctor to auto-fix
openclaw doctor --fix

# Verify config is valid
openclaw config get
```

---

## Config File Basics

| Property | Value |
|----------|-------|
| **Path** | `~/.openclaw/openclaw.json` |
| **Format** | JSON5 (comments, trailing commas, unquoted keys allowed) |
| **Validation** | Strict - unknown keys = Gateway refuses to start |
| **Watching** | Gateway watches file for changes and hot-reloads |

### Configuration Methods

| Method | Description |
|--------|-------------|
| Direct file edit | Edit `~/.openclaw/openclaw.json` directly. Gateway detects changes. |
| CLI | `openclaw config get/set/unset` - safest method |
| Web UI | Control UI at `http://127.0.0.1:18789` |
| Onboard wizard | `openclaw onboard` - guided initial setup |

### CLI Config Commands

```bash
openclaw config get                          # Show full config
openclaw config get gateway.port             # Get specific value
openclaw config set gateway.port 19000       # Set a value
openclaw config unset gateway.auth.token     # Remove a value
```

The CLI validates before writing, making it the safest way to change config.

### Modular Config with $include

Split config across files:

```json5
{
  "$include": "./channels-config.json",
  gateway: { port: 18789 }
}
```

The included file is merged into the main config.

---

## Config RPC (Programmatic Access)

The Gateway exposes config methods via RPC:

| Method | Description |
|--------|-------------|
| `config.get` | Read current config (or a specific path) |
| `config.apply` | Apply a full config object (replaces) |
| `config.patch` | Merge partial config (rate-limited: 3 calls per 60 seconds) |

`config.patch` is rate-limited to prevent accidental rapid-fire config changes that could destabilize the Gateway.

---

## Hot Reload Modes

The Gateway watches `openclaw.json` and reloads on changes.

| Mode | Behavior |
|------|----------|
| `hybrid` | Smart: hot-reload where possible, restart where needed (default) |
| `hot` | Non-destructive in-place reload (keeps connections alive) |
| `restart` | Full process restart on any config change |
| `off` | Disable auto-reload entirely |

```json5
gateway: {
  reload: "hybrid"
}
```

**What hot-applies (no restart needed):**
- Channel settings (dm policy, allow lists)
- Agent model changes
- Tool permissions
- Session settings

**What requires restart:**
- Gateway port/bind changes
- Auth mode changes
- Adding/removing channels entirely

**Manual reload via SIGUSR1:**
```bash
pkill -SIGUSR1 -f gateway
```

SIGUSR1 is non-destructive: reloads config without dropping connections or sessions.

---

## Top-Level Sections

| Section | Purpose | Reference |
|---------|---------|-----------|
| `gateway` | Core process: port, bind, auth, reload, HTTP endpoints | [gateway.md](references/gateway.md) |
| `commands` | Messenger commands (e.g., `/restart`) | See below |
| `agents` | Multi-agent system: defaults, agent list, models | [agents.md](references/agents.md) |
| `channels` | Messenger integrations (Telegram, WhatsApp, Discord, etc.) | [channels.md](references/channels.md) |
| `session` | Session scoping, reset behavior | [session.md](references/session.md) |
| `sandbox` | Code execution isolation (Docker) | [session.md](references/session.md) |
| `cron` | Built-in job scheduler | [session.md](references/session.md) |
| `hooks` | Webhook receiver configuration | [session.md](references/session.md) |
| `tools` | Tool permissions, profiles, restrictions | [tools.md](references/tools.md) |
| `browser` | Playwright browser integration | [tools.md](references/tools.md) |
| `skills` | Skill loading, entries, installation | [tools.md](references/tools.md) |
| `models` | LLM providers and model configuration | [models-env.md](references/models-env.md) |
| `env` | Environment variable injection | [models-env.md](references/models-env.md) |

### Commands Block (Simple)

```json5
commands: {
  restart: true    // Allow /restart command from messenger clients
}
```

**Security warning:** Setting `commands.config: true` allows users to modify config from chat. Only enable for trusted single-user setups.

---

## Minimal Working Config

The smallest config that runs:

```json5
{
  gateway: {
    port: 18789
  },
  agents: {
    list: [
      { agentId: "main", workspace: "~/.openclaw/workspace" }
    ]
  }
}
```

Everything else uses defaults.

---

## Full Example Config

```json5
{
  gateway: {
    mode: "local",
    port: 18789,
    bind: "loopback",
    reload: "hybrid",
    auth: { mode: "token", token: "change-me-please" },
    http: { endpoints: { chatCompletions: { enabled: true } } }
  },

  commands: { restart: true },

  agents: {
    defaults: {
      workspace: "~/.openclaw/workspace",
      model: { primary: "anthropic/claude-opus-4-6" },
      heartbeat: { every: "30m" }
    },
    list: [
      { agentId: "main" },
      { agentId: "work", workspace: "~/.openclaw/workspace-work" }
    ]
  },

  channels: {
    telegram: {
      botToken: "...",
      enabled: true,
      dmPolicy: "pairing",
      streamMode: "partial"
    }
  },

  session: {
    dmScope: "main",
    reset: { mode: "daily", atHour: 4 }
  },

  cron: { enabled: true },

  models: {
    providers: {
      "openrouter": {
        baseUrl: "https://openrouter.ai/api/v1",
        apiKey: "sk-or-...",
        api: "openai-completions"
      }
    }
  },

  env: {
    vars: { TZ: "America/New_York" },
    shellEnv: true
  }
}
```

---

## Validation Checklist

Before saving config changes:

- [ ] JSON is valid (no trailing syntax errors, mismatched braces)
- [ ] No unknown keys (Gateway rejects unknown fields)
- [ ] Auth is set if bind mode is `lan` (Gateway refuses to start without auth on lan)
- [ ] Channel tokens/secrets are in env vars, not hardcoded
- [ ] Backup exists (`openclaw.json.bak`)

After saving:

- [ ] `openclaw config get` returns without errors
- [ ] `openclaw doctor` shows no critical issues
- [ ] Gateway reloaded successfully (check logs)

---

## Common Pitfalls

For detailed troubleshooting with examples and recovery procedures, see [troubleshooting.md](references/troubleshooting.md).

**Quick list of things that will break your setup:**

1. **Unknown keys in config** - Gateway refuses to start. Always check field names.
2. **Editing config mid-sentence** - Gateway watches the file. If it reads a half-written file, it crashes. Use `openclaw config set` instead of manual editing when possible.
3. **`gateway.bind: "lan"` without auth** - Gateway refuses to start for safety. Always set auth when binding to lan.
4. **`commands.config: true`** - Lets anyone in chat modify your config. Only for trusted single-user.
5. **`tools.elevated.enabled: true` + open DM policy** - Gives strangers admin access to your system.
6. **Missing `OPENCLAW_GATEWAY_TOKEN` env var** - If auth mode is token but no token is set in config or env.
7. **`sandbox.mode: "all"` without Docker** - Sandbox requires Docker to be running.

---

## Further Reference

Each config section has a dedicated reference file with full schema documentation:

- **Gateway, auth, HTTP endpoints**: [gateway.md](references/gateway.md)
- **Agents, models, workspace, heartbeat**: [agents.md](references/agents.md)
- **All channel platforms**: [channels.md](references/channels.md)
- **Session, sandbox, cron, hooks**: [session.md](references/session.md)
- **Tools, browser, skills config**: [tools.md](references/tools.md)
- **Models, env, auth, logging**: [models-env.md](references/models-env.md)
- **Troubleshooting & recovery**: [troubleshooting.md](references/troubleshooting.md)
