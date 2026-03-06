# OpenClaw CLI Cheat Sheet
*Created 2026-02-23. Reference: https://docs.openclaw.ai/cli*

## ⚠️ GOLDEN RULE
**Do NOT edit openclaw.json directly.** Use the CLI commands below. If unsure about a config key, ask Jared.

---

## Telegram Bots / Channels

### Add a new Telegram bot
```bash
openclaw channels add --channel telegram --token <bot-token>
```
Then add a **binding** (routes messages to the right agent):
```bash
openclaw config set bindings '[...existing, {"agentId":"<agent-id>","match":{"channel":"telegram","accountId":"<account-id>"}}]' --strict-json
```

### List channels
```bash
openclaw channels list
openclaw channels status
```

### Remove a channel
```bash
openclaw channels remove --channel telegram --delete
```

### Channel config keys to know
- `dmPolicy`: "open" | "closed"
- `groupPolicy`: "open" | "disabled"
- `groupTrigger`: "all" | "mention" (whether bot responds to all group messages or only @mentions)
- `streaming`: "off" (STRING, not boolean false!)
- `allowFrom`: ["*"] or list of user IDs

**Docs:** https://docs.openclaw.ai/cli/channels

---

## Agents

### List agents
```bash
openclaw agents list
```

### Add a new agent
```bash
openclaw agents add <agent-id> --workspace <path>
```

### Set agent identity
```bash
openclaw agents set-identity --agent <id> --name "Name" --emoji "🏹" --avatar path/to/avatar.png
# Or from IDENTITY.md:
openclaw agents set-identity --workspace <path> --from-identity
```

### Delete an agent
```bash
openclaw agents delete <agent-id>
```

**Docs:** https://docs.openclaw.ai/cli/agents

---

## Models

### Check current model status
```bash
openclaw models status
openclaw models status --agent <id>  # per-agent
openclaw models status --probe       # live auth check (uses tokens!)
```

### Set default model
```bash
openclaw models set <model-or-alias>
# Examples:
openclaw models set anthropic/claude-opus-4-6
openclaw models set minimax/MiniMax-M2.5-Lightning
openclaw models set Minimax  # alias
```

### List available models
```bash
openclaw models list
```

### Manage aliases
```bash
openclaw models aliases list
openclaw models aliases add <alias> <provider/model>
openclaw models aliases remove <alias>
```

### Manage fallbacks
```bash
openclaw models fallbacks list
openclaw models fallbacks add <provider/model>
openclaw models fallbacks remove <provider/model>
openclaw models fallbacks clear
```

### Auth profiles
```bash
openclaw models auth add
openclaw models auth login --provider <id>
openclaw models auth setup-token
openclaw models auth paste-token
```

### Scan for available models
```bash
openclaw models scan
```

**Docs:** https://docs.openclaw.ai/cli/models

---

## Config (get/set/unset)

### Read a value
```bash
openclaw config get agents.defaults.workspace
openclaw config get agents.list[0].id
openclaw config get channels.telegram.accounts
```

### Set a value
```bash
openclaw config set <path> <value>
# JSON values need --strict-json:
openclaw config set agents.defaults.heartbeat.every "2h"
openclaw config set gateway.port 19001 --strict-json
openclaw config set channels.whatsapp.groups '["*"]' --strict-json
```

### Unset a value
```bash
openclaw config unset tools.web.search.apiKey
```

### Agent-specific config (by list index)
```bash
openclaw config get agents.list        # see all agents and their indices
openclaw config set agents.list[1].tools.exec.node "node-id"
```

**Always restart gateway after config edits:**
```bash
openclaw gateway restart
```

**Docs:** https://docs.openclaw.ai/cli/config

---

## Gateway

```bash
openclaw gateway status
openclaw gateway start
openclaw gateway stop
openclaw gateway restart
openclaw gateway health
```

---

## Sessions

```bash
openclaw sessions                  # list all
openclaw sessions --active 120     # active in last 120 min
openclaw sessions --json
```

---

## Other Useful Commands

### Status & diagnostics
```bash
openclaw status
openclaw status --deep
openclaw doctor
openclaw doctor --fix
```

### Security
```bash
openclaw security audit
openclaw security audit --deep
openclaw security audit --fix
```

### Logs
```bash
openclaw logs
openclaw channels logs --channel all
```

### Skills
```bash
openclaw skills list
openclaw skills info <name>
openclaw skills check
```

### Cron
```bash
openclaw cron list
openclaw cron status
openclaw cron add
openclaw cron edit <id>
openclaw cron rm <id>
```

### Memory
```bash
openclaw memory status
openclaw memory index
openclaw memory search "<query>"
```

---

## Key Config Paths (for `config get/set`)

| Path | What it controls |
|------|-----------------|
| `agents.list` | All agent definitions |
| `agents.list[N].id` | Agent ID |
| `agents.list[N].model` | Agent's model |
| `agents.list[N].workspace` | Agent workspace path |
| `agents.list[N].thinking` | Reasoning display ("off"/"on"/"stream") |
| `agents.defaults.model.primary` | Default model for all agents |
| `agents.defaults.model.fallbacks` | Fallback model list |
| `agents.defaults.subagents` | Subagent config (maxConcurrent, maxSpawnDepth, etc.) |
| `agents.defaults.heartbeat.every` | Heartbeat interval |
| `channels.telegram.accounts` | All Telegram bot accounts |
| `bindings` | Agent ↔ channel routing rules |
| `tools.sessions.visibility` | Cross-agent messaging ("all"/"none") |
| `gateway.port` | Gateway port |

---

## Reminders
- **Restart gateway** after any config change
- **Use CLI** for config changes, not direct JSON editing
- Telegram accounts: NO `agent` field inside account config — use `bindings` array
- Telegram `streaming`: must be string `"off"`, not boolean `false`
