---
name: clawroam
description: >
  Portable identity vault for OpenClaw. Syncs knowledge, packages, and memory
  across machines like iCloud — automatic, invisible, encrypted. Bring your own
  storage (Google Drive, Dropbox, FTP, Git) or use ClawRoam Cloud.
version: "3.0.1"
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
  - network
requires:
  # Required — skill will not function without these
  - curl        # HTTP requests to ClawRoam Cloud API and providers
  - git         # local vault version history
  - openssl     # AES-256-CBC archive encryption and Ed25519 signing
  - ssh-keygen  # Ed25519 keypair generation and verification
  - python3     # JSON parsing, key derivation, URL encoding
  - rsync       # staging vault files for upload/download
  - tar         # creating and extracting vault archives
  # Optional — skill degrades gracefully without these
  - fswatch     # real-time file watching; falls back to polling without it
  - bc          # billing cost calculations; skipped gracefully without it
network:
  - url: "https://clawroam-api.ovisoftblue.workers.dev"
    description: >
      ClawRoam Cloud managed storage backend (Cloudflare Workers + D1 + R2).
      Only contacted when the built-in 'cloud' provider is selected.
      Not used for BYOS providers (gdrive, dropbox, git, ftp, s3, local, webdav).
    data_sent:
      - email address (signup only)
      - Ed25519 public key (signup and key rotation)
      - encrypted vault archive (AES-256-CBC; server cannot decrypt)
      - file path manifest (filenames and sizes only, not file content)
    data_stored_server_side: >
      Encrypted vault snapshots (up to 10 versions per profile), public keys,
      email address. Private key never leaves the local machine.
---

# ClawRoam — Portable Agent Environment

You are an OpenClaw agent with the **clawroam** skill installed. This skill
gives you automatic, continuous sync of the user's knowledge and environment
across all their machines — like iCloud for AI agents.

## Architecture

ClawRoam works like a combination of iCloud and Git:
- **Auto-sync**: file changes are detected, auto-committed, and pushed
- **Versioned**: every change is a commit — full history, rollback anytime
- **Encrypted**: Ed25519 keypair per installation — private key never leaves the machine
- **Multi-provider**: user picks where their vault lives

## Providers

| Provider | Type | Setup |
|----------|------|-------|
| ClawRoam Cloud | Managed (paid per MB) | One command — `clawroam cloud signup` |
| Google Drive | BYOS (free) | OAuth flow via `clawroam provider gdrive` |
| Dropbox | BYOS (free) | OAuth flow via `clawroam provider dropbox` |
| FTP/SFTP | BYOS (free) | Host + credentials via `clawroam provider ftp` |
| Git | BYOS (free) | Any git remote via `clawroam provider git` |
| S3 | BYOS (free) | Any S3-compatible via `clawroam provider s3` |
| WebDAV | BYOS (free) | Nextcloud etc via `clawroam provider webdav` |
| Local | BYOS (free) | USB/NAS mount via `clawroam provider local` |

"BYOS" = Bring Your Own Storage. Free forever. ClawRoam Cloud is the
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
- **"set up clawroam"** →
  `clawroam.sh init` — creates vault, generates Ed25519 keypair, scans packages
- **"use clawroam cloud"** →
  `clawroam.sh cloud signup` — creates cloud account, auto-configures provider
- **"use google drive for vault"** →
  `clawroam.sh provider gdrive` — OAuth flow for Google Drive
- **"use dropbox for vault"** →
  `clawroam.sh provider dropbox`
- **"use FTP for vault"** →
  `clawroam.sh provider ftp` — asks for host, port, credentials

### Daily Use (mostly invisible)
- **"sync status"** →
  `clawroam.sh status` — show sync state, last push/pull, provider info
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
  `clawroam.sh profile show` — displays current profile name
- **"list profiles"** / **"what profiles exist"** →
  `clawroam.sh profile list` — lists all profiles in the remote storage
- **"rename profile"** →
  `clawroam.sh profile rename <new-name>` — renames this machine's profile
- **"restore from another machine"** / **"pull profile X"** →
  `clawroam.sh profile pull <name>` — restores a specific profile to this machine
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
   `~/.clawroam/keys/` with 600 permissions. The public key is registered
   with the vault provider.

5. **Conflicts:** If remote has changes the user hasn't seen, show a diff
   and let them choose. Auto-merge for non-conflicting changes (like git).

6. **Be transparent about costs.** If using ClawRoam Cloud, show current
   usage and estimated cost when asked. Never surprise the user with charges.

7. **Offline-first.** Everything works locally. Sync happens when connectivity
   is available. Queue changes and push when back online.

8. **Profiles are separate by default.** Each machine pushes to its own named
   profile (default: hostname). Profiles never merge automatically. If the user
   wants data from another machine, they must explicitly pull that profile with
   `clawroam.sh profile pull <name>`.

## ClawRoam Cloud Pricing

When users ask about pricing:
- **First 50 MB free** — enough for most single-user vaults
- **$0.005/MB/month** after that (~$0.50/month for 100 MB extra)
- **No per-instance fees** — connect unlimited machines
- **No bandwidth fees** — sync as often as you want
- Example: typical vault is 10-30 MB → completely free
- Example: power user with 200 MB → $0.75/month
- Example: team vault with 2 GB → ~$10/month
