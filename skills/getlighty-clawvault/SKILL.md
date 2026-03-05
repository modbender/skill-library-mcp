---
name: clawvault
description: >
  Portable identity vault for OpenClaw. Syncs knowledge, packages, and memory
  across machines like iCloud — automatic, invisible, encrypted. Bring your own
  storage (Google Drive, Dropbox, FTP, Git) or use ClawVault Cloud.
version: 2.0.0
author: clawvault
license: MIT
tags:
  - sync
  - identity
  - migration
  - packages
  - backup
  - roaming
triggers:
  - vault
  - sync
  - migrate
  - packages
  - roam
  - backup
  - restore
  - cloud
tools:
  - exec
  - file
---

# ClawVault — Portable Agent Environment

You are an OpenClaw agent with the **clawvault** skill installed. This skill
gives you automatic, continuous sync of the user's knowledge and environment
across all their machines — like iCloud for AI agents.

## Architecture

ClawVault works like a combination of iCloud and Git:
- **Auto-sync**: file changes are detected, auto-committed, and pushed
- **Versioned**: every change is a commit — full history, rollback anytime
- **Encrypted**: Ed25519 keypair per installation — private key never leaves the machine
- **Multi-provider**: user picks where their vault lives

## Providers

| Provider | Type | Setup |
|----------|------|-------|
| ClawVault Cloud | Managed (paid per MB) | One command — `clawvault cloud signup` |
| Google Drive | BYOS (free) | OAuth flow via `clawvault provider gdrive` |
| Dropbox | BYOS (free) | OAuth flow via `clawvault provider dropbox` |
| FTP/SFTP | BYOS (free) | Host + credentials via `clawvault provider ftp` |
| Git | BYOS (free) | Any git remote via `clawvault provider git` |
| S3 | BYOS (free) | Any S3-compatible via `clawvault provider s3` |
| WebDAV | BYOS (free) | Nextcloud etc via `clawvault provider webdav` |
| Local | BYOS (free) | USB/NAS mount via `clawvault provider local` |

"BYOS" = Bring Your Own Storage. Free forever. ClawVault Cloud is the
convenience option for people who don't want to manage storage.

## What Syncs

```
ALWAYS SYNCED (shared knowledge pool):
  identity/USER.md          Who you are
  knowledge/MEMORY.md       Long-term memory
  knowledge/projects/       Project context
  requirements.yaml         System packages
  skills-manifest.yaml      Installed skills list

NEVER AUTO-SYNCED (per-instance):
  local/SOUL.md             This agent's personality
  local/IDENTITY.md         This agent's identity
  local/config-override     Local config tweaks

OPT-IN SYNC:
  openclaw config.json      Gateway/model config
  credentials/              Channel auth (encrypted separately)
```

## Commands

When the user asks about vault operations, use these:

### First-Time Setup
- **"set up clawvault"** →
  `clawvault.sh init` — creates vault, generates Ed25519 keypair, scans packages
- **"use clawvault cloud"** →
  `clawvault.sh cloud signup` — creates cloud account, auto-configures provider
- **"use google drive for vault"** →
  `clawvault.sh provider gdrive` — OAuth flow for Google Drive
- **"use dropbox for vault"** →
  `clawvault.sh provider dropbox`
- **"use FTP for vault"** →
  `clawvault.sh provider ftp` — asks for host, port, credentials

### Daily Use (mostly invisible)
- **"sync status"** →
  `clawvault.sh status` — show sync state, last push/pull, provider info
- **"sync now"** →
  `sync-engine.sh push` — force immediate sync
- **"show vault history"** →
  `sync-engine.sh log` — show commit history (like `git log`)
- **"rollback vault"** →
  `sync-engine.sh rollback` — revert to previous state
- **"what changed"** →
  `sync-engine.sh diff` — show pending changes

### Packages
- **"scan packages"** →
  `track-packages.sh scan`
- **"what's different from vault"** →
  `track-packages.sh diff`
- **"install missing packages"** →
  `track-packages.sh install` — shows commands, asks before running

### Migration
- **"migrate to this machine"** / **"pull from vault"** →
  `migrate.sh pull` — interactive restore wizard
- **"push my soul to vault"** →
  `migrate.sh push-identity` — explicit opt-in only

### Profiles
Each machine backs up to its own named profile (default: hostname).
Profiles are separate — different machines can have different knowledge,
memory, and packages without interfering with each other.

- **"show profile"** / **"what profile am I on"** →
  `clawvault.sh profile show` — displays current profile name
- **"list profiles"** / **"what profiles exist"** →
  `clawvault.sh profile list` — lists all profiles in the remote storage
- **"rename profile"** →
  `clawvault.sh profile rename <new-name>` — renames this machine's profile
- **"restore from another machine"** / **"pull profile X"** →
  `clawvault.sh profile pull <name>` — restores a specific profile to this machine
  (overwrites local vault with that profile's data, does NOT affect the source)

### Key Management
- **"show my vault key"** →
  `keypair.sh show-public` — display public key (for adding to providers)
- **"regenerate vault key"** →
  `keypair.sh rotate` — generates new keypair, re-registers with provider

## Behavior Rules

1. **Auto-sync is ON by default** after setup — like iCloud. The user should
   not have to think about syncing. Changes are pushed within 30 seconds.

2. **Never sync SOUL.md or IDENTITY.md without explicit permission.**

3. **Always confirm before installing packages.** Show the diff, let them pick.

4. **Private key never leaves the machine.** It's stored in
   `~/.clawvault/keys/` with 600 permissions. The public key is registered
   with the vault provider.

5. **Conflicts:** If remote has changes the user hasn't seen, show a diff
   and let them choose. Auto-merge for non-conflicting changes (like git).

6. **Be transparent about costs.** If using ClawVault Cloud, show current
   usage and estimated cost when asked. Never surprise the user with charges.

7. **Offline-first.** Everything works locally. Sync happens when connectivity
   is available. Queue changes and push when back online.

8. **Profiles are separate by default.** Each machine pushes to its own named
   profile (default: hostname). Profiles never merge automatically. If the user
   wants data from another machine, they must explicitly pull that profile with
   `clawvault.sh profile pull <name>`.

## ClawVault Cloud Pricing

When users ask about pricing:
- **First 50 MB free** — enough for most single-user vaults
- **$0.005/MB/month** after that (~$0.50/month for 100 MB extra)
- **No per-instance fees** — connect unlimited machines
- **No bandwidth fees** — sync as often as you want
- Example: typical vault is 10-30 MB → completely free
- Example: power user with 200 MB → $0.75/month
- Example: team vault with 2 GB → ~$10/month
