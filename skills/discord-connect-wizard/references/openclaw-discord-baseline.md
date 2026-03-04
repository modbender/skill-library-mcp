# OpenClaw Discord baseline (official-style)

Core:

```bash
openclaw config set channels.discord.token '"YOUR_BOT_TOKEN"' --json
openclaw config set channels.discord.enabled true --json
openclaw gateway restart
```

Privileged intents (Discord Developer Portal → Bot):
- Message Content Intent (required)
- Server Members Intent (recommended)

Guild workspace baseline (private server):
- `channels.discord.groupPolicy="allowlist"`
- allowlist your guild under `channels.discord.guilds.<guildId>`
- set `requireMention=false` for a private server

Pairing:

```bash
openclaw pairing list discord
openclaw pairing approve discord <CODE>
```

Troubleshooting quick checks:

```bash
openclaw doctor
openclaw channels status --probe
openclaw logs --follow
```
