# Setup Guide

Complete step-by-step instructions for setting up a debate moderator on your Discord server
using OpenClaw.

---

## Prerequisites

- An OpenClaw gateway running with Discord configured
- A Discord bot token with the required permissions
- Admin access to the target Discord server

---

## Step 1: Create or Choose a Discord Server

**New server:**
1. Open Discord → click the "+" button in the server list
2. Choose "Create My Own" → "For me and my friends" (or a club/community)
3. Name it whatever you like (e.g., "The Debate Hall")

**Existing server:**
- You can add the debate moderator to any server. Dedicated channels will be created.
- Ensure the bot has permissions in the channels it needs.

---

## Step 2: Get Your Guild ID

1. In Discord, go to Settings → Advanced → Enable **Developer Mode**
2. Right-click your server icon → **Copy Server ID**
3. Save this — you'll need it for the config.

---

## Step 3: Required Bot Permissions

Your Discord bot needs these OAuth2 scopes and permissions:

### OAuth2 Scopes
- `bot`
- `applications.commands` (optional, for future slash commands)

### Bot Permissions
- **General:** Read Messages/View Channels, Manage Channels
- **Text:** Send Messages, Send Messages in Threads, Create Public Threads, Manage Messages, Embed Links, Attach Files, Read Message History, Add Reactions, Use External Emoji
- **Advanced:** Manage Roles (if you want the bot to assign debate roles)

**Permission integer:** `328565073936`

If your bot is already in the server with sufficient permissions, skip the invite step.

### Invite URL Template
```
https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=328565073936&scope=bot%20applications.commands
```

Replace `YOUR_CLIENT_ID` with your bot's application ID.

---

## Step 4: Security — Separate Agent Configuration

**CRITICAL:** The debate moderator should run as a **separate OpenClaw agent**, isolated
from your personal assistant. This means:

### Why Isolation Matters
- The debate server is (semi-)public — participants are not just you
- The moderator should NOT have access to your personal files, messages, or data
- If someone discovers a prompt injection, the blast radius is limited to the debate skill
- The moderator only needs Discord messaging — no email, calendar, files, or home automation

### What to Restrict
The debate agent should have:
- ✅ Discord message sending/reading (in configured channels only)
- ✅ Access to its own workspace (`skills/debate-moderator/`)
- ✅ Ability to run scoreboard scripts
- ❌ No access to personal files or other workspaces
- ❌ No email, calendar, or contacts access
- ❌ No home automation
- ❌ No iMessage or SMS
- ❌ No web browsing (optional — enable if you want the moderator to fact-check)

### How Isolation Works in OpenClaw
OpenClaw supports multiple agents, each with their own:
- AGENTS.md (instructions)
- Workspace (filesystem root)
- Channel bindings (which Discord channels they respond in)
- Tool permissions

The debate agent gets its own agent ID, its own AGENTS.md (generated from
`references/agents-template.md`), and is bound only to the debate channels.

---

## Step 5: Gateway Config

Use `config.patch` to add the debate agent to your OpenClaw gateway configuration.

### Config Patch Template

**Important:** `agents.list` and `bindings` are arrays. A config.patch **replaces**
arrays entirely. You must include ALL your existing agents and bindings alongside the
new debate entries. Use `config.get` first to retrieve your current config.

The agent that triggers this skill should handle this automatically — building the
full patch from the current config plus the debate additions.

**Debate agent entry** (add to `agents.list`):
```json
{
  "id": "debate",
  "name": "Debate Moderator",
  "workspace": "/absolute/path/to/debate/workspace",
  "model": {
    "primary": "anthropic/claude-sonnet-4-6"
  },
  "tools": {
    "profile": "messaging",
    "deny": [
      "exec", "process", "nodes", "cron", "gateway", "browser",
      "canvas", "sessions_spawn", "sessions_send", "sessions_list",
      "sessions_history", "subagents", "session_status", "agents_list",
      "tts", "image", "memory_search", "memory_get"
    ],
    "exec": { "security": "deny" },
    "fs": { "workspaceOnly": true }
  }
}
```

**Binding entry** (add to `bindings` BEFORE any catch-all Discord binding):
```json
{
  "agentId": "debate",
  "match": {
    "channel": "discord",
    "guildId": "YOUR_GUILD_ID"
  }
}
```

**Guild entry** (add to `channels.discord.guilds`):
```json
{
  "channels": {
    "discord": {
      "guilds": {
        "YOUR_GUILD_ID": {
          "requireMention": false,
          "channels": {
            "*": { "allow": true }
          }
        }
      }
    }
  }
}
```

The guild entry merges safely with `config.patch` since it's an object keyed by
guild ID. The `agents.list` and `bindings` arrays must be patched as complete arrays.

### Configuration Notes

- **Model:** `anthropic/claude-sonnet-4-6` is recommended for cost-effectiveness. Use `anthropic/claude-opus-4-6` for highest quality moderation.
- **requireMention per channel:**
  - `the-arena` defaults to `false` so the moderator sees all debate messages
  - All other channels default to `true` (respond only when @mentioned)
  - Set `the-arena` to `true` if you want cheaper, on-demand-only moderation
- **Workspace:** Points to the skill directory. The agent can only access files here.

### Cost Implications

| Setting | Behavior | Relative Cost |
|---------|----------|---------------|
| All channels `requireMention: true` | Moderator only responds when pinged | $ (lowest) |
| Arena `false`, others `true` | Active in debates, passive elsewhere | $$ (moderate) |
| All channels `requireMention: false` | Moderator sees and may respond to everything | $$$ (highest) |

A typical debate (Campfire format, ~20 messages per side) with active moderation costs
roughly 50k–100k tokens depending on the model and persona verbosity.

---

## Step 6: Create the AGENTS.md

Generate the debate agent's AGENTS.md from the template:

**Option A — Use the setup script:**
```bash
./scripts/setup.sh
```
This walks you through all options and generates the AGENTS.md automatically.

**Option B — Manual:**
1. Copy `references/agents-template.md` to your agent's AGENTS.md location
2. Replace all `[CONFIGURE: ...]` placeholders with your choices
3. Save as the file referenced in your agent config's `systemPrompt`

---

## Step 7: Create Channels

Create the following channels in your Discord server. You can use the bot itself
or create them manually.

| Channel | Description | Category (suggested) |
|---------|-------------|---------------------|
| `#rules` | Server rules, debate formats, commands | Debate Hall |
| `#propose-a-topic` | Topic proposals and interest gauging | Debate Hall |
| `#the-arena` | Where debates happen | Debate Hall |
| `#hall-of-records` | Verdicts, scoreboard, debate history | Debate Hall |
| `#the-bar` | Off-topic, casual chat, post-debate debrief | Lounge |

After creating channels, update the config patch with the actual channel IDs.

---

## Step 8: Post Welcome Messages

Post the welcome messages from `assets/welcome-messages.md` in each channel.
The setup script can do this automatically, or you can copy-paste them manually.

---

## Step 9: Initialize the Scoreboard

If scoreboard is enabled:
```bash
cd skills/debate-moderator
./scripts/scoreboard.sh init
```

This creates the SQLite database at `./data/scoreboard.db` (or wherever
`$DEBATE_SCOREBOARD_DB` points).

---

## Step 10: Testing Checklist

Before going live, verify:

- [ ] Bot is in the server with correct permissions
- [ ] Gateway config is applied (`config.patch`)
- [ ] Agent responds when @mentioned in `#rules`
- [ ] Agent responds to messages (without mention) in `#the-arena`
- [ ] Welcome messages are posted in all channels
- [ ] Scoreboard initializes without errors
- [ ] Run a test debate:
  - [ ] Propose a topic in `#propose-a-topic`
  - [ ] Start a debate in `#the-arena`
  - [ ] Verify moderator interjects appropriately
  - [ ] Call "I rest my case" and verify ready check
  - [ ] Verify verdict is posted in both `#the-arena` and `#hall-of-records`
  - [ ] Verify scoreboard is updated
- [ ] Test each persona (optional — change in AGENTS.md and restart)
- [ ] Test requireMention behavior in each channel

---

## Troubleshooting

### Bot doesn't respond
1. Check gateway logs: `openclaw gateway logs`
2. Verify the agent ID matches in config
3. Verify channel IDs are correct
4. Check that the bot has Read Messages permission in the channel

### Bot responds in wrong channels
1. Verify channel bindings in the guild config
2. Ensure only the debate agent is bound to debate channels

### Scoreboard errors
1. Ensure `data/` directory exists: `mkdir -p data`
2. Check permissions: `ls -la data/scoreboard.db`
3. Re-initialize: `./scripts/scoreboard.sh init`

### High token usage
1. Set all channels to `requireMention: true`
2. Use `anthropic/claude-sonnet-4-6` instead of Opus
3. Choose Brief verdict style
4. Reduce moderator interjection frequency in AGENTS.md

---

## Upgrading

To update the skill:
1. Pull the latest skill files
2. Review changelog for breaking changes
3. Re-run `./scripts/setup.sh` if configuration options have changed
4. Apply any config patches
5. Restart the gateway: `openclaw gateway restart`
