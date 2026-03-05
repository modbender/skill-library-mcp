---
name: vps-bootstrap
description: Bootstrap a fresh VPS from zero to a fully operational OpenClaw deployment, with backup/restore and post-recovery verification. Use when setting up OpenClaw on a new VPS, recovering from a failed server, migrating between machines, or automating disaster recovery. Covers system dependencies, Node.js, Chrome, OpenClaw install, security hardening, backup to Google Drive, restore from backup, and full verification suite.
---

# VPS Bootstrap

Full deployment and disaster recovery framework for OpenClaw on Ubuntu VPS.

## Overview

Three scripts handle the complete lifecycle:

1. **`bootstrap.sh`** — Fresh VPS → fully operational OpenClaw (15-20 min)
2. **`restore.sh`** — Restore workspace, config, secrets, and crons from backup
3. **`verify.sh`** — Post-deployment verification (all-green = ready)

## Quick Start

### New VPS setup

```bash
# On fresh Ubuntu 24.04 VPS
bash scripts/bootstrap.sh
```

### Restore from backup

```bash
bash scripts/restore.sh ~/openclaw-backup-*.tar.gz
```

### Verify everything works

```bash
bash scripts/verify.sh
```

## What bootstrap.sh does

Sequential installation with error handling at each step:

1. **System packages** — build-essential, curl, git, jq, unzip, etc.
2. **Node.js** — Latest LTS via NodeSource
3. **Google Chrome** — Stable channel + headless shim for browser tools
4. **OpenClaw** — Global npm install + gateway service setup
5. **Security baseline** — UFW firewall, fail2ban, SSH key-only auth
6. **Service setup** — systemd user service with auto-restart + linger

Each step is idempotent — safe to re-run if interrupted.

## What restore.sh does

Extracts a backup tarball and restores:

- Workspace files (SOUL.md, MEMORY.md, AGENTS.md, memory/, scripts/)
- OpenClaw config (openclaw.json, .env)
- Cron database
- GPG keys + password store (encrypted secrets)
- OAuth credentials (GOG, rclone)
- System config snapshot

## What verify.sh does

Runs 10+ checks and reports pass/fail:

- OpenClaw gateway running and healthy
- Telegram/Discord providers connected
- Browser tools functional
- Backup system operational
- Cron jobs loaded
- SSH security baseline
- Disk space and memory

## Backup Script (Optional)

For automated daily backups, see `references/backup-guide.md`.

## Customization

Edit `scripts/bootstrap.sh` variables at the top:

```bash
OPENCLAW_PORT=18789        # Gateway port
ENABLE_FIREWALL=true       # UFW setup
ENABLE_FAIL2BAN=true       # SSH protection
INSTALL_CHROME=true        # Browser tools support
```

## Requirements

- Ubuntu 22.04+ or Debian 12+
- Root or sudo access
- 2GB+ RAM recommended
- SSH key access configured

## Security Notes

- Scripts never store secrets in plaintext in the skill itself
- GPG keys are backed up encrypted
- SSH is hardened to key-only authentication
- Gateway binds to localhost by default
