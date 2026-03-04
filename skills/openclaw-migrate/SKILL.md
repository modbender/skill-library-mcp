# OpenClaw Migration Skill

Migrate OpenClaw from one host to another via SSH.

## Skill Metadata

- **Name**: openclaw-migrate
- **Type**: OpenClaw Skill
- **Purpose**: Migrate all OpenClaw config, skills, memory, tokens to new host

## Setup Commands

### Prerequisites

1. SSH access to new host
2. SSH key (recommended for automation)
3. NPM installed on new host

### Configuration

```bash
# Configure migration target
openclaw-migrate setup

# It will ask for:
# - New host IP/hostname (e.g., 192.168.1.50)
# - SSH user (e.g., crix)
# - SSH key path (optional, Enter for default)
```

## Usage Commands

### Main Migration

```bash
# Start migration (one command!)
openclaw-migrate migrate
```

### Other Commands

```bash
# Test SSH connection
openclaw-migrate test

# Show current configuration
openclaw-migrate status

# Reconfigure target
openclaw-migrate setup
```

## What Gets Synced

### Files & Directories

| Source | Destination |
|--------|-------------|
| `~/.openclaw/` | `~/.openclaw/` (skills, memory, config) |
| `~/.config/openclaw/` | `~/.config/openclaw/` |
| OpenClaw npm package | Reinstalled if missing |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `HA_URL` | Home Assistant URL |
| `HA_TOKEN` | Home Assistant token |
| `GITHUB_TOKEN` | GitHub API token |
| `BRAVE_API_KEY` | Brave Search API |
| `GOOGLE_API_KEY` | Google API key |
| Any `HA_*` vars | All HA related vars |

### System Data

- Cron jobs (via crontab)
- OpenClaw gateway configuration

## Migration Flow

```
1. setup → Configure target host
2. test → Verify SSH connection
3. migrate → Full sync and start
   ├─ Check/Install OpenClaw
   ├─ Sync workspace (~/.openclaw/)
   ├─ Sync config
   ├─ Sync environment variables
   ├─ Sync cron jobs
   └─ Start gateway on new host
```

## Error Handling

- SSH connection failed: Show retry option
- OpenClaw not on remote: Offer to install
- Sync failed: Report which files failed
- Config missing: Prompt for setup

## Related Skills

- skillstore (search/install skills)

## Files

```
openclaw-migrate/
├── SKILL.md       # This file
├── README.md      # User docs
├── main.js        # Migration CLI
└── config.json    # Saved target config
```
