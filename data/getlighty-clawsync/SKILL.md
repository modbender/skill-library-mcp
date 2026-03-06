---
name: clawsync
description: >
  Portable identity vault for OpenClaw. Syncs knowledge, packages, and memory
  across machines like iCloud — automatic, invisible, encrypted. Bring your own
  storage (Google Drive, Dropbox, FTP, Git) or use ClawSync Cloud.
version: 2.0.0
author: getlighty
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

# ClawSync — Portable Agent Environment

You are an OpenClaw agent with the **clawsync** skill installed. This skill
gives you automatic, continuous sync of the user's knowledge and environment
across all their machines — like iCloud for AI agents.

## Architecture

ClawSync works like a combination of iCloud and Git:
- **Auto-sync**: file changes are detected, auto-committed, and pushed
- **Versioned**: every change is a commit — full history, rollback anytime
- **Encrypted**: Ed25519 keypair per installation — private key never leaves the machine
- **Multi-provider**: user picks where their vault lives

## Providers

| Provider | Type | Setup |
|----------|------|-------|
| ClawSync Cloud | Managed (paid per MB) | One command — `clawsync cloud signup` |
| Google Drive | BYOS (free) | OAuth flow via `clawsync provider gdrive` |
| Dropbox | BYOS (free) | OAuth flow via `clawsync provider dropbox` |
| FTP/SFTP | BYOS (free) | Host + credentials via `clawsync provider ftp` |
| Git | BYOS (free) | Any git remote via `clawsync provider git` |
| S3 | BYOS (free) | Any S3-compatible via `clawsync provider s3` |
| WebDAV | BYOS (free) | Nextcloud etc via `clawsync provider webdav` |
| Local | BYOS (free) | USB/NAS mount via `clawsync provider local` |

"BYOS" = Bring Your Own Storage. Free forever. ClawSync Cloud is the
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
- **"set up clawsync"** →
  `clawsync.sh init` — creates vault, generates Ed25519 keypair, scans packages
- **"use clawsync cloud"** →
  `clawsync.sh cloud signup` — creates cloud account, auto-configures provider
- **"use google drive for vault"** →
  `clawsync.sh provider gdrive` — OAuth flow for Google Drive
- **"use dropbox for vault"** →
  `clawsync.sh provider dropbox`
- **"use FTP for vault"** →
  `clawsync.sh provider ftp` — asks for host, port, credentials

### Daily Use (mostly invisible)
- **"sync status"** →
  `clawsync.sh status` — show sync state, last push/pull, provider info
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
  `clawsync.sh profile show` — displays current profile name
- **"list profiles"** / **"what profiles exist"** →
  `clawsync.sh profile list` — lists all profiles in the remote storage
- **"rename profile"** →
  `clawsync.sh profile rename <new-name>` — renames this machine's profile
- **"restore from another machine"** / **"pull profile X"** →
  `clawsync.sh profile pull <name>` — restores a specific profile to this machine
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
   `~/.clawsync/keys/` with 600 permissions. The public key is registered
   with the vault provider.

5. **Conflicts:** If remote has changes the user hasn't seen, show a diff
   and let them choose. Auto-merge for non-conflicting changes (like git).

6. **Be transparent about costs.** If using ClawSync Cloud, show current
   usage and estimated cost when asked. Never surprise the user with charges.

7. **Offline-first.** Everything works locally. Sync happens when connectivity
   is available. Queue changes and push when back online.

8. **Profiles are separate by default.** Each machine pushes to its own named
   profile (default: hostname). Profiles never merge automatically. If the user
   wants data from another machine, they must explicitly pull that profile with
   `clawsync.sh profile pull <name>`.

## ClawSync Cloud Pricing

When users ask about pricing:
- **First 50 MB free** — enough for most single-user vaults
- **$0.005/MB/month** after that (~$0.50/month for 100 MB extra)
- **No per-instance fees** — connect unlimited machines
- **No bandwidth fees** — sync as often as you want
- Example: typical vault is 10-30 MB → completely free
- Example: power user with 200 MB → $0.75/month
- Example: team vault with 2 GB → ~$10/month
