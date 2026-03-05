---
name: auto-updater
description: OpenClaw auto-update checker and safe applier. Checks for new versions, compares changelogs, and applies updates with rollback safety. Designed to run as a cron job for hands-free maintenance. Use for keeping OpenClaw up to date automatically.
homepage: https://www.agxntsix.ai
license: MIT
compatibility: OpenClaw gateway, git
metadata: {"openclaw": {"emoji": "\ud83d\udd04", "requires": {"bins": ["git"]}, "homepage": "https://www.agxntsix.ai"}}
---

# Auto-Updater 🔄

**Keep OpenClaw up to date automatically and safely.**

Checks for new OpenClaw versions via git tags, compares with your current version, shows what's new, and optionally applies the update with safe rollback support.

## Quick Start

```bash
# Check for updates (safe, read-only)
bash {baseDir}/scripts/check_update.sh

# Check and apply if available
bash {baseDir}/scripts/check_update.sh --apply

# JSON output (for cron/automation)
bash {baseDir}/scripts/check_update.sh --json

# Check + apply + JSON
bash {baseDir}/scripts/check_update.sh --apply --json
```

## Setting Up as a Cron Job

### Via OpenClaw Cron
Add to your cron jobs to check daily:

```json
{
  "name": "auto-update-check",
  "schedule": "0 1 * * *",
  "command": "bash skills/auto-updater/{baseDir}/scripts/check_update.sh --json",
  "description": "Daily OpenClaw update check at 1 AM"
}
```

### Via System Crontab
```bash
# Check daily at 1 AM, log results
0 1 * * * cd /root/.openclaw/workspace && bash skills/auto-updater/{baseDir}/scripts/check_update.sh >> /var/log/openclaw-updates.log 2>&1
```

## How It Works

1. **Fetch** — `git fetch --tags` from the OpenClaw repo
2. **Compare** — Current version vs latest git tag (semver sorted)
3. **Report** — Shows version diff and changelog/commits between versions
4. **Apply** (optional) — Checkout new tag → pnpm install → pnpm build → docker build → docker compose up -d
5. **Verify** — Checks gateway starts successfully after update

## Safe Update Practices

- **Always** runs `git fetch` before comparing (fresh data)
- **Shows** what changed before applying
- **Records** the previous version for rollback
- **Verifies** gateway health after update
- **Never** force-pushes or modifies git history

## Rollback Procedure

If an update breaks something:

```bash
# 1. See recent tags
cd /host/openclaw && git tag --sort=-v:refname | head -5

# 2. Checkout previous version
git checkout <previous-tag>

# 3. Rebuild
pnpm install && pnpm build
docker build -t openclaw:latest .
docker compose up -d

# 4. Verify
docker compose logs --tail=20
```

The script outputs rollback instructions automatically when applying updates.

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
