# OpenClaw Configuration Reference

Reference normalized against:
- `https://docs.openclaw.ai/cli/config`
- `https://docs.openclaw.ai/gateway/configuration`
- Individual CLI pages for models, channels, agents, hooks, cron, security, secrets

Last verified: 2026-02-27.

## Config File Location
Default state directory:
- `~/.openclaw`

Default config file:
- `~/.openclaw/openclaw.json`

Profile-based isolation:
- `--dev` flag → `~/.openclaw-dev`
- `--profile <name>` flag → `~/.openclaw-<name>`

## CLI Config Management
Use CLI sub-commands (not flags) to manage config:

- `openclaw config get <key>`: Read a config value.
- `openclaw config set <key> <value>`: Write a config value.
- `openclaw config unset <key>`: Remove a config value.

Interactive wizard:
- `openclaw configure`: Full interactive config setup.

Gateway RPC config methods:
- `config.apply`: Validate + write config + restart + wake.
- `config.patch`: Merge a partial update + restart + wake.
- `config.get`: Get current config via RPC.
- `update.run`: Run update + restart.

## Strict Validation
When config fails schema validation:
- Gateway does not boot.
- Only diagnostic commands work: `openclaw doctor`, `openclaw logs`, `openclaw health`, `openclaw status`.
- Run `openclaw doctor` to see exact issues.
- Run `openclaw doctor --fix` (or `--yes`) to apply repairs.

## Minimal Config Example
```json
{
  "gateway": {
    "bind": "127.0.0.1",
    "port": 18789,
    "auth": {
      "token": "replace-with-strong-token"
    }
  },
  "channels": {
    "whatsapp": {
      "allowFrom": ["+1234567890"],
      "groups": {
        "*": { "requireMention": true }
      }
    }
  },
  "agents": {
    "defaults": {
      "workspace": "~/.openclaw/workspace",
      "model": {
        "primary": "claude-3-5-sonnet-latest"
      },
      "imageModel": {
        "primary": "gpt-4o"
      }
    }
  },
  "messages": {
    "groupChat": {
      "mentionPatterns": ["@openclaw"]
    }
  }
}
```

## High-impact Keys
- `gateway.bind`: Interface binding. Keep `127.0.0.1` unless remote access is required.
- `gateway.port`: Gateway port (default `18789`).
- `gateway.auth.token`: Required when binding beyond loopback.
- `channels.*`: Channel-specific policy and auth settings.
- `channels.<name>.allowFrom`: Restrict who can message the agent.
- `channels.<name>.groups.*.requireMention`: Require mention in group chats.
- `agents.defaults.workspace`: Base workspace for agent tasks.
- `agents.defaults.model.primary`: Default model used by agents.
- `agents.defaults.imageModel.primary`: Default image model.
- `messages.groupChat.mentionPatterns`: Patterns to trigger agent in group chats.
- `commands.debug`: Enable `/debug` slash command (default `false`).

## Environment Variables

### OpenClaw Runtime Variables
- `OPENCLAW_CONFIG_PATH`: Override config file path.
- `OPENCLAW_STATE_DIR`: Override state directory.
- `OPENCLAW_HOME`: Override OpenClaw home directory.
- `OPENCLAW_GATEWAY_TOKEN`: Gateway token (also set by `--token` flag).
- `OPENCLAW_GATEWAY_PASSWORD`: Gateway password (also set by `--password` flag).
- `OPENCLAW_LOAD_SHELL_ENV=1`: Import shell environment variables at startup.
- `OPENCLAW_AGENT_DIR` / `PI_CODING_AGENT_DIR`: Scope agent context.
- `CLAUDE_WEB_SESSION_KEY` / `CLAUDE_WEB_COOKIE`: Session keys for Claude channel.
- `NO_COLOR=1`: Disable ANSI output styling.

### Wrapper Variable
- `OPENCLAW_WRAPPER_ALLOW_RISKY=1`: Enable high-risk commands in wrapper.

## Env File Loading
- `.env` from CWD (if present)
- `~/.openclaw/.env` (global fallback)

## Inline Environment Variables
Define env vars directly in config:
```json
{
  "env": {
    "OPENROUTER_API_KEY": "sk-or-...",
    "vars": { "GROQ_API_KEY": "gsk-..." }
  }
}
```

## Shell Environment Import
```json
{
  "env": {
    "shellEnv": { "enabled": true, "timeoutMs": 15000 }
  }
}
```
Also activated via `OPENCLAW_LOAD_SHELL_ENV=1`.

## Config Value Substitution
Use `${VAR_NAME}` in config values (uppercase only: `[A-Z_][A-Z0-9_]*`).
- Missing/empty vars throw error at load time.
- Escape with `$${VAR}` for literal output.
- Works inside `$include` files.
- Example: `"${BASE}/v1"` → `"https://api.example.com/v1"`

## Secret Refs
Replace plaintext secrets with structured refs:
```json
{
  "models": { "providers": { "openai": {
    "apiKey": { "source": "env", "provider": "default", "id": "OPENAI_API_KEY" }
  }}},
  "skills": { "entries": { "my-skill": {
    "apiKey": { "source": "file", "provider": "filemain", "id": "/skills/entries/my-skill/apiKey" }
  }}},
  "channels": { "googlechat": {
    "serviceAccountRef": { "source": "exec", "provider": "vault", "id": "channels/googlechat/serviceAccount" }
  }}
}
```
Sources: `env`, `file`, `exec`. Providers defined in `secrets.providers` config.

Use `openclaw secrets configure` to set up providers and map credentials interactively.
Use `openclaw secrets audit` to check for plaintext residues.

## Config Hot Reload
Gateway watches `openclaw.json` for changes.

Reload modes (`gateway.reload.mode`):
- `hybrid` (default): hot-apply safe fields, restart for structural changes.
- `hot`: hot-apply only.
- `restart`: full restart on any change.
- `off`: no auto-reload.

Config:
```json
{ "gateway": { "reload": { "mode": "hybrid", "debounceMs": 300 } } }
```

**Hot-apply fields:** `channels.*`, `web`, `agent`, `agents`, `models`, `routing`, `hooks`, `cron`, `session`, `messages`, `tools`, `browser`, `skills`, `audio`, `talk`, `ui`, `logging`, `identity`, `bindings`.

**Restart-required fields:** `gateway.*`, `discovery`, `canvasHost`, `plugins`, `gateway.reload`, `gateway.remote`.
