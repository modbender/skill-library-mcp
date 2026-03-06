---
name: agent-spawner
description: Spawn a new OpenClaw agent through conversation. Uses official Docker setup and non-interactive onboarding, carries over API keys, tools, plugins, and skills from the current agent. User answers 2-3 questions. Use when the user wants to create, spin up, deploy, or provision a new OpenClaw agent.
---

# Agent Spawner

Deploy a new OpenClaw agent conversationally. Official install, carry over config from the current agent. User never edits a file.

## 1. Read Current Config (silent)

```bash
cat ~/.openclaw/openclaw.json
cat ~/.openclaw/.env 2>/dev/null
env | grep -iE 'API_KEY|TOKEN'
ls ~/.openclaw/extensions/
ls <workspace>/skills/
```

Identify:
- **Provider**: check `auth.profiles` in config — could be Anthropic, OpenAI, Gemini, custom, etc.
- **API key**: from env var or config (e.g. `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `OPENAI_API_KEY`)
- **Model**: from `agents.defaults.model`
- **Tool keys**: anything in `tools.*` (search APIs, etc.)
- **Plugins**: `plugins.installs` — names and npm specs
- **Skills**: run `openclaw skills list` to see what's bundled vs workspace-only. Only carry over non-bundled skills.

## 2. Ask

1. **"Where should I deploy it?"** — Docker (local or remote SSH) or bare metal?
2. **"Name?"** — for container. Generate one if they don't care.
3. **"Anything special?"** — purpose, constraints. Optional.

Don't ask about keys, plugins, skills, ports, or config. Carry everything over, use defaults.

## 3. Confirm Plan

After gathering answers, present the full plan before doing anything. Show everything in one summary:

```
Here's the plan:

📦 Deploy: Docker on <target>
📛 Name: <agent-name>
🌐 Port: <port>

Carrying over from current agent:
  ✅ Provider: Anthropic (API key)
  ✅ Model: anthropic/claude-sonnet-4-20250514
  ✅ Brave Search API key
  ✅ Plugins: openclaw-agent-reach
  ✅ Skills: agent-spawner, weather
  ✅ Heartbeat: 30m

The new agent will bootstrap its own identity on first message.

Good to go?
```

Only list items that actually exist. Wait for explicit confirmation before proceeding. If the user wants changes, adjust and re-confirm.

## 4. Deploy

### Docker

```bash
git clone https://github.com/openclaw/openclaw.git <agent-name>
cd <agent-name>
```

Set env and run non-interactive onboard. Match the provider detected in step 1:

```bash
export OPENCLAW_IMAGE=alpine/openclaw:latest
export OPENCLAW_CONFIG_DIR=~/.openclaw-<agent-name>
export OPENCLAW_WORKSPACE_DIR=~/.openclaw-<agent-name>/workspace
export OPENCLAW_GATEWAY_PORT=<unused port, default 18789>
export OPENCLAW_GATEWAY_BIND=lan

mkdir -p $OPENCLAW_CONFIG_DIR/workspace
```

**Onboard flags vary by provider.** Use the matching `--auth-choice` and key flag:

| Provider | --auth-choice | Key flag |
|----------|--------------|----------|
| Anthropic | `apiKey` | `--anthropic-api-key` |
| Gemini | `gemini-api-key` | `--gemini-api-key` |
| OpenAI | `apiKey` | (set `OPENAI_API_KEY` env) |
| Custom | `custom-api-key` | `--custom-api-key` + `--custom-base-url` + `--custom-model-id` |

```bash
docker compose run --rm openclaw-cli onboard --non-interactive --accept-risk \
  --mode local \
  --auth-choice <detected> \
  --<provider>-api-key "$API_KEY" \
  --gateway-port 18789 \
  --gateway-bind lan \
  --skip-skills

docker compose up -d openclaw-gateway
```

Official compose uses **bind mounts** — host user owns files, no permission issues.

Onboard error about gateway connection is expected (not running yet). Config is written.

### Bare metal

```bash
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-onboard

openclaw onboard --non-interactive --accept-risk \
  --mode local \
  --auth-choice <detected> \
  --<provider>-api-key "$API_KEY" \
  --gateway-port 18789 \
  --gateway-bind lan \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

## 5. Patch Running Agent

CLI alias:
- Docker: `OC="docker compose exec openclaw-gateway node /app/openclaw.mjs"`
- Bare metal: `OC="openclaw"`

**Config** (only patch what the current agent actually has):
```bash
$OC config set agents.defaults.model "<model>"
$OC config set agents.defaults.heartbeat.every "30m"
# Tool keys — only if they exist in current config
$OC config set tools.web.search.apiKey "<key>"
```

**Plugins** (from `plugins.installs` in current config):
```bash
$OC plugins install <npm-spec>
# Repeat for each plugin
```

**Skills** (copy workspace skills):
```bash
# Docker
docker cp <source-workspace>/skills/ <container>:/home/node/.openclaw/workspace/skills/
# Bare metal
cp -r <source-workspace>/skills/ ~/.openclaw/workspace/skills/
```

**Restart:**
```bash
docker compose restart openclaw-gateway  # Docker
openclaw gateway restart                 # bare metal
```

## 6. Hand Off

Read the gateway token:
```bash
grep -A1 '"token"' $OPENCLAW_CONFIG_DIR/openclaw.json
```

Tell the user:
- **URL:** `http://<host>:<port>/`
- **Token:** (from config — onboard auto-generates one)
- "Say hello — it'll bootstrap itself."

## Notes

- `openclaw` not in PATH inside Docker. Use `node /app/openclaw.mjs`.
- `--accept-risk` required for non-interactive onboard.
- `alpine/openclaw:latest` — pre-built official image.
- Don't use named Docker volumes — root ownership issues. Official compose uses bind mounts.
- Multiple agents on same host: use different `OPENCLAW_CONFIG_DIR` and `OPENCLAW_GATEWAY_PORT`.
- Plugins and skills persist in `~/.openclaw/` volume (extensions/ and workspace/skills/).
- SSH keys, git config, apt packages are ephemeral — not in the volume, by design.
