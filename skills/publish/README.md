# ClawSync

Backup and restore your OpenClaw workspace to GitHub.

## ⚠️ Important: Do NOT Commit Personal Files

This repo is published to ClawHub. **Do NOT commit** these files:
- `AGENTS.md`, `SOUL.md`, `USER.md`, `TOOLS.md`, `IDENTITY.md`, `HEARTBEAT.md`
- `SITES.md` (contains API keys)
- `MEMORY.md` (sensitive conversation data)

These files are in `.gitignore` for a reason. Personal/workspace-specific configuration should stay on your local machine.

## Quick Start

```bash
git clone https://github.com/your-username/ClawSync.git ~/ClawSync
cp .env.example .env
# Edit .env with your values
bash sync.sh
```

## Auth

Uses gh CLI if available, falls back to token auth.

## Files

- `sync.sh` - Backup
- `restore.sh` - Restore
- `.env.example` - Template
