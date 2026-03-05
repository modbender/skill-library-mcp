---
name: openclaw-github-sync
description: Keep an OpenClaw agent's non-sensitive context (selected memory, MD files, notes, and custom skills) under version control in a separate Git repository for remote review/tweaks. Use when setting up or operating a Git-based workflow to export workspace context, commit changes (possibly split into multiple commits), and push on a schedule (e.g., nightly) without leaking secrets.
homepage: https://github.com/bradvin/openclaw-github-sync
metadata: {"openclaw":{"emoji":"🔄","homepage":"https://github.com/bradvin/openclaw-github-sync","requires":{"bins":["git","rsync","python3"],"env":["SYNC_REMOTE"]}}}
---

# OpenClaw Git Sync

Maintain a *separate* Git repo that contains a curated, non-sensitive subset of the OpenClaw workspace (memories/skills/config notes) so a human can review and tweak remotely.

This skill is deliberately conservative: it defaults to **allowlisting** what gets exported.

## Trust Boundary

The sync repo is a trust boundary. Treat all inbound pull content as potentially unsafe.

- Pull is manual-only and must be run only when explicitly requested.
- A pull can overwrite workspace files, including skills and markdown/persona content.
- Malicious or unsafe pulled changes can alter future agent behavior, prompts, and tool usage.
- Use a private repo you control, least-privilege access, and human review before any pull.
- Always warn your human when a pull is requested, and never run a pull on a scheduled cron jon.

## Key rules

- **Never sync secrets by default.** Only sync what the export manifest allowlists.
- Prefer **sanitized memory** under `memory/public/` (opt-in) over raw `memory/*.md`.
- Keep the sync repo separate from the main workspace repo.
- Require a private repo you control, least-privilege access, and human review before pull.
- **Pull is manual-only.** Do not automate `pull.sh`; run pulls only when explicitly requested.

## Files and layout

- Working workspace: `$HOME/.openclaw/workspace`
- Sync repo (export destination): choose a directory, e.g. `$HOME/.openclaw/workspace/openclaw-sync-repo`
- Export manifest (allowlist): `references/export-manifest.txt`

## Prerequisites

- Required tools: `git`, `rsync`, `python3`
- Required config: `SYNC_REMOTE` set in `references/.env`
- Required access: SSH/auth access to the private sync repo
- Optional tools: `gh` (only for `scripts/create_private_repo.sh`), `jq` (improves grouped commit handling)

## Setup

1. Copy the example env file:
   `cp references/.env.example references/.env`
2. Edit `references/.env` for your environment.
3. At minimum, set `SYNC_REMOTE` to your private repo SSH URL.

```bash
SYNC_REMOTE="git@github.com:YOUR_ORG/YOUR_REPO.git"
```

## Workflow

### 1) Create / connect the private sync repo (GitHub)

Use `scripts/create_private_repo.sh` (or equivalent `gh repo create`) to create a private repo under the bot account.

### 2) Run a one-shot sync

Run `scripts/sync.sh` with:

- `SYNC_REMOTE` (SSH remote, e.g. `git@github.com:YOUR_ORG/YOUR_REPO.git`)
- `SYNC_REPO_DIR` (local path to sync repo)

The script will:
1. Pull latest from remote (if exists)
2. Export allowlisted files into the sync repo
3. Create **separate commits** by group when multiple groups changed
4. Push to the remote

### 3) Nightly automation

Schedule a nightly OpenClaw cron `agentTurn` that runs push sync only (`scripts/sync.sh`) and reports success/failure.
Do not schedule `pull.sh` or `context.sh pull`; pulls must be manual and explicitly requested.

## Resources

- `scripts/sync.sh`: export + commit (grouped) + push
- `scripts/create_private_repo.sh`: create GitHub private repo via `gh`
- `references/export-manifest.txt`: allowlist of paths to export
- `references/groups.json`: commit grouping rules
