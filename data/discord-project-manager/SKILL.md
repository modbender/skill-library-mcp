---
name: discord-project-manager
description: Discord project collaboration infrastructure for OpenClaw agents. Manage Forum Channels, threads, participant permissions, and mention mode. Supports 3-tier architecture (Forum Channel → Thread → Default Channel) for multi-agent project coordination.
metadata:
  openclaw:
    requires:
      config:
        - path: "~/.openclaw/openclaw.json"
          access: "read/write"
          reason: "Reads bot token and agent account mappings; writes channel permission entries and triggers config reload"
      credentials:
        - name: "Discord bot token"
          source: "channels.discord.accounts.*.token in OpenClaw config"
          reason: "Used for Discord REST API calls (forum channel creation)"
      permissions:
        - "Discord bot: Manage Channels (for forum/thread creation)"
    sideEffects:
      - "Patches ~/.openclaw/openclaw.json (channel permission entries)"
      - "Sends SIGUSR1 to gateway process for config reload (2-5s restart)"
      - "Falls back to 'openclaw gateway restart' if SIGUSR1 fails"
---

# Discord Project Manager

Automated Discord project collaboration for OpenClaw multi-agent teams. Create Forum Channels and threads, manage who can speak where, and control mention-only mode — all from the CLI.

## Prerequisites

- OpenClaw with Discord channel configured
- Discord bot with `Manage Channels` permission in the target guild
- Python 3.8+

## Quick Start

```bash
SKILL_DIR="/path/to/discord-project-manager"

# 1. Initialize (first time only)
python3 "$SKILL_DIR/scripts/discord-pm.py" config init
python3 "$SKILL_DIR/scripts/discord-pm.py" registry init
python3 "$SKILL_DIR/scripts/discord-pm.py" forum-channel set-default <forum_channel_id>

# 2. Create a project thread
python3 "$SKILL_DIR/scripts/discord-pm.py" thread create \
  --name "my-feature" \
  --owner agent-a \
  --participants "agent-a,agent-b"
```

This creates a thread in your default forum, gives `agent-a` free speech (owner), and sets `agent-b` to mention-only mode.

## Commands

### Configuration

```bash
discord-pm.py config init                # Auto-detect guild ID from OpenClaw config
discord-pm.py config get                 # Show current config
discord-pm.py config set-guild <id>      # Set guild ID manually
discord-pm.py config set-forum <id>      # Set default forum channel
```

### Agent Registry

```bash
discord-pm.py registry init             # Auto-collect agent info from OpenClaw config
discord-pm.py registry list             # List all registered agents
```

### Forum Channels

```bash
# Create a new Forum Channel (uses Discord REST API directly)
discord-pm.py forum-channel create <name> [--emoji <emoji>] [--description <text>]

# Manage forum channels
discord-pm.py forum-channel set-default <channel_id>
discord-pm.py forum-channel add <channel_id> <name>    # Register existing channel
discord-pm.py forum-channel remove <name>
discord-pm.py forum-channel list
```

### Threads

```bash
# Create thread (uses default forum unless --forum-channel specified)
discord-pm.py thread create \
  --name <name> \
  --owner <agent> \
  --participants <agent1,agent2,...> \
  [--forum-channel <id>] \
  [--no-mention] \
  [--message <text>]

discord-pm.py thread archive <thread_id>    # Remove all permissions
discord-pm.py thread status <thread_id>     # Show permissions and participants
```

### Permissions

```bash
discord-pm.py permissions add <thread_id> <agent1> [agent2...] [--no-mention]
discord-pm.py permissions remove <thread_id> <agent1> [agent2...]
discord-pm.py permissions mention-mode <thread_id> <on|off> <agents...|--all>
```

### Project Registry

```bash
discord-pm.py project list [--active] [--archived] [--agent <name>]
discord-pm.py project info <thread_id>
discord-pm.py project describe <thread_id> <text>
discord-pm.py project update <thread_id> --next-action <text>
```

Projects are automatically registered when threads are created and updated when participants change or threads are archived. The `--agent` filter shows only projects where the agent is owner or participant, with role labels.

Batch operations: `add` and `remove` accept multiple agent names. A single config patch is applied for all agents, so only one gateway reload happens.

The `--all` flag on `mention-mode` scans the live OpenClaw config to find every account that currently has access to the thread, then sets mention mode for all of them — including accounts not in the agent registry (e.g. manually configured bots).

## Architecture

### 3-Tier Project Structure

| Tier | Use Case | Example |
|------|----------|---------|
| Forum Channel | Large project with sub-teams | 📦-product-launch |
| Thread | Individual task or sub-project | api-refactor |
| Default Channel | Quick tasks, no isolation needed | #dev-ops |

### Permission Model

- **Owner**: `requireMention: false` — speaks freely, drives the conversation
- **Participants**: `requireMention: true` — only responds when @mentioned
- **Non-participants**: no channel access configured

This keeps threads focused: the owner leads, others contribute when asked.

### How It Works

1. **Thread/Forum creation** — threads via `openclaw message` CLI, forums via Discord REST API
2. **Permission management** — patches OpenClaw config (`channels.discord.accounts.<account>.guilds.<guild>.channels.<channel>`)
3. **Config reload** — triggers SIGUSR1 graceful restart (2-5s). Falls back to `openclaw gateway restart` if needed.

## Data Files

```
data/
├── config.json     # Skill config (guild ID, default forum)
├── agents.json     # Agent registry (account IDs, user IDs, channels)
└── projects.json   # Project registry (threads, owners, participants, nextAction)
```

Both auto-generated by `config init` and `registry init`. Excluded from git (user-specific data).

## Security & Permissions

This skill requires access to your OpenClaw configuration:

- **Reads** `~/.openclaw/openclaw.json` to obtain the Discord bot token and agent account mappings
- **Writes** channel permission entries to the same config file (with file locking and atomic writes)
- **Triggers** SIGUSR1 for graceful config reload (falls back to `openclaw gateway restart`)

The bot token is used exclusively for Discord REST API calls (forum channel creation). It is never logged, stored elsewhere, or transmitted to third parties.

**Recommendations:**
- Back up `~/.openclaw/openclaw.json` before first use
- Ensure your Discord bot has only `Manage Channels` permission
- Review the source code if you have concerns about config access

## Troubleshooting

| Problem | Check |
|---------|-------|
| Thread creation fails | Is the default forum set? (`forum-channel set-default`) |
| Mention mode not working | Does the agent have `mentionPatterns` in OpenClaw config? |
| Forum creation 403 | Does the bot have `Manage Channels` permission in the guild? |
| Permission changes delayed | Config reload takes 2-5s. If still not working, run `openclaw gateway restart` |

## Source Structure

```
discord-project-manager/
├── SKILL.md
├── scripts/
│   ├── discord-pm.py     # Unified CLI
│   └── cli.sh            # Bash wrapper
├── lib/
│   ├── discord_api.py    # Discord API (CLI + REST)
│   ├── config.py         # OpenClaw config operations
│   ├── skill_config.py   # Skill-local config
│   ├── registry.py       # Agent registry
│   ├── thread.py         # Thread lifecycle
│   ├── permissions.py    # Permission management
│   ├── forum.py          # Forum channel management
│   ├── projects.py       # Project registry
│   └── validators.py     # Input validation
└── data/                 # Auto-generated, git-ignored
```

---

_Version: 2.2.1_
_Last Updated: 2026-02-27_
