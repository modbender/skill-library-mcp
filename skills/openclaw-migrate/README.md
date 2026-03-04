# OpenClaw Migration Tool

Migrate OpenClaw from one host to another via SSH with one command.

## Features

- SSH-based remote migration
- Auto-install OpenClaw on new host
- Full configuration sync
- Skills and memory sync
- Environment variables sync
- Cron jobs sync
- One-command execution

## Quick Start

```bash
# Configure target
openclaw-migrate setup

# Run migration
openclaw-migrate migrate

# Test connection
openclaw-migrate test
```

## What Gets Synced

### Files
- `~/.openclaw/` - Workspace (skills, memory, config)
- `~/.config/openclaw/` - OpenClaw config
- OpenClaw npm package

### Environment Variables
- `HA_URL`, `HA_TOKEN`
- `GITHUB_TOKEN`
- `BRAVE_API_KEY`
- `GOOGLE_API_KEY`
- Any `HA_*` variables

### System
- Cron jobs

## Setup

```bash
$ openclaw-migrate setup
New host IP/hostname: 192.168.1.50
SSH user: crix
SSH key path: ~/.ssh/id_rsa
```

## Usage

```bash
# Configure once
openclaw-migrate setup

# Run migration (one command!)
openclaw-migrate migrate

# Check everything works
openclaw-migrate test
```

## Requirements

- SSH access to target host
- SSH key (recommended)
- NPM on target host

## Error Handling

- Connection issues: Shows helpful error and retry option
- Missing OpenClaw: Auto-installs
- Sync failures: Reports which files failed

## Files

```
openclaw-migrate/
├── SKILL.md        # OpenClaw skill docs
├── README.md       # This file
├── main.js         # Migration CLI
└── config.json    # Saved config
```

## License

MIT
