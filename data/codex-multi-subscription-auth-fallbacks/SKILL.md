---
name: codex-auth-fallback
description: Set up OpenClaw multi-provider auth with OpenAI Codex OAuth fallback profiles and automatic model switching. Use when configuring multiple OpenAI Codex accounts for rate-limit failover, adding new Codex OAuth profiles via device flow, or setting up a cron job to auto-switch models when a provider hits cooldown.
requires:
  - codex  # OpenAI Codex CLI (npm i -g @openai/codex) — also provides node
files_read:
  - ~/.codex/auth.json                              # Reads OAuth tokens after device-flow login
files_write:
  - ~/.codex/auth.json                              # Temporarily cleared to force fresh login, then restored from backup
  - ~/.openclaw/agents/main/agent/auth-profiles.json # Writes imported OAuth profile tokens
---

# Codex Auth Fallback

Multi-provider auth setup for OpenClaw with automatic failover between Anthropic and multiple OpenAI Codex OAuth sessions.

## Overview

OpenClaw supports multiple auth profiles per provider. When one profile hits a rate limit, the platform can fail over to another. This skill covers:

1. **Adding Codex OAuth profiles** via device-flow login
2. **Configuring `openclaw.json`** for provider fallback order
3. **Setting up `auth-profiles.json`** with multiple profiles
4. **Deploying a cron job** to auto-switch models on cooldown

## Prerequisites

- OpenClaw instance running
- `codex` CLI installed (`npm i -g @openai/codex`) — this also ensures `node` is available
- One or more OpenAI accounts with Codex access

## Security & Safety

**What this skill accesses:**

| File | Access | Purpose |
|------|--------|---------|
| `~/.codex/auth.json` | Read + Temporary Write | Temporarily cleared to force a fresh device-flow login, then restored from backup. Original tokens are never deleted — a timestamped backup is created first. |
| `~/.openclaw/agents/main/agent/auth-profiles.json` | Read + Write | Imported OAuth tokens (access + refresh) are written here. A timestamped backup is created before any modification. |

**Important safety notes:**

- **Tokens stay local.** No tokens are sent to any external endpoint. The script reads tokens from the local Codex CLI auth file and writes them to the local OpenClaw auth-profiles file.
- **Backups are always created.** Both files are backed up with timestamps before any modification. If login fails or the script is interrupted, a trap handler restores the original Codex CLI auth automatically.
- **Interactive confirmation.** The script prompts for confirmation before clearing the Codex CLI auth file, so you can abort if needed.
- **No elevated privileges.** The script runs as your user and does not require sudo or any special permissions.
- **Back up manually first.** Despite the automatic backups, it is recommended to manually back up `~/.codex/auth.json` and your OpenClaw configs before running, especially on first use.
- **Test with a non-production account.** For initial testing, consider using a throwaway or non-production OpenAI account.

## Step 1: Add Codex OAuth Profiles

Run the bundled script for each OpenAI account:

```bash
./scripts/codex-add-profile.sh <profile-name>
```

The script:
1. Backs up `~/.codex/auth.json` and `auth-profiles.json`
2. Clears Codex CLI auth to force fresh device-flow login
3. Runs `codex auth login` (opens browser for OAuth)
4. Extracts tokens and imports them into OpenClaw's `auth-profiles.json`
5. Restores the original Codex CLI auth

Repeat for each account. Profile names should be short identifiers (e.g., the OpenAI username).

## Step 2: Configure openclaw.json

Add auth profile declarations and fallback model config. See `references/config-templates.md` for the exact JSON blocks to add to `openclaw.json`.

Key sections:
- **`auth.profiles`** — Declare each profile with provider and mode
- **`auth.order`** — Set failover priority per provider
- **`agents.defaults.model`** — Set primary model + fallbacks

## Step 3: Auth Profiles JSON Structure

OpenClaw stores live tokens in `agents/main/agent/auth-profiles.json`. See `references/config-templates.md` for the schema.

Each Codex profile contains:
- `type`: `"oauth"`
- `provider`: `"openai-codex"`
- `access`: JWT access token (auto-populated by the add-profile script)
- `refresh`: Refresh token (auto-populated)
- `expires`: Token expiry in ms (parsed from JWT)
- `accountId`: OpenAI account ID (parsed from JWT)

The `order` object controls which profile is tried first per provider. The `usageStats` object tracks rate limits and cooldowns automatically.

## Step 4: Model Cooldown Auto-Switch Cron (Optional)

> **This step is entirely optional.** The auth profiles from Steps 1-3 work on their own with OpenClaw's built-in failover. This cron job adds automatic model switching, which means your active model may change without manual intervention. Only enable it if you understand and want this behavior.

Deploy a cron job that checks cooldown state every 10 minutes and switches the active model. See `references/config-templates.md` for the full cron job definition.

The cron job:
1. Runs `openclaw models status` to check cooldown state
2. Picks the best available model (priority: opus > codex profiles in order)
3. Updates the session model override if needed
4. Logs state to a local memory file; only notifies on change

**Before enabling:**
- Test manually first: run `openclaw models status` to verify your profiles are working
- Review the cron job template in `references/config-templates.md` — the job only runs local commands and writes to a local state file
- The job runs in an isolated session and does not affect your main chat unless a model switch occurs

Add the job to `cron/jobs.json` using the template in the references.

## File Layout

```
codex-auth-fallback/
├── SKILL.md                    # This file
├── scripts/
│   └── codex-add-profile.sh    # Device-flow profile importer
└── references/
    └── config-templates.md     # openclaw.json, auth-profiles, cron templates
```
