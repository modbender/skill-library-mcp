# OpenClaw Git Sync Skill

This skill syncs a curated, non-sensitive subset of an OpenClaw workspace to a separate private Github repo so humans can review and tweak remotely.

## Installation

Say this to your OpenClaw agent:

"Install the skill from https://github.com/bradvin/openclaw-github-sync and set it up to run nightly."

The skill will:
1. Install itself
2. Create a private sync repo
3. Set up a nightly push cron job

## What This Skill Can Do

- Create a private GitHub repository for the sync.
- Export allowlisted workspace content into a dedicated sync repo.
- Pull remote changes back into the workspace manually when explicitly requested.
- Split sync changes into multiple commits by content group.
- Block commits and pushes when likely secrets are detected.
- Run automation-friendly syncs for nightly/cron jobs.
- Generate a summary `README.md` inside the sync repo with a rolling changelog.

## Trust Boundary

The sync repo is a trust boundary. Treat all inbound pull content as potentially unsafe.

- Pull is manual-only and must be run only when explicitly requested.
- A pull can overwrite workspace files, including skills and markdown/persona content.
- Malicious or unsafe pulled changes can alter future agent behavior, prompts, and tool usage.
- Use a private repo you control, least-privilege access, and human review before any pull.

## Safety Model

- Sync is allowlist-first via [`references/export-manifest.txt`](references/export-manifest.txt).
  - Defaults : AGENTS.md, IDENTITY.md, SOUL.md, TOOLS.md, USER.md, skills/, memory/
- Secret scanning runs before commit/push and fails on findings.
- Optional ignore rules are read from [`references/secret-scan-ignore.txt`](references/secret-scan-ignore.txt).
  - Default : none!
- The sync target is a separate Git repo, not the main workspace repo.
- Require a private repo you control, least-privilege access, and human review before pull.
- Pull is manual-only by design. Do not automate `pull.sh` or `context.sh pull`.

## Prerequisites

- Required tools: `git`, `rsync`, `python3`
- Required config: `SYNC_REMOTE` set in `references/.env`
- Required access: SSH/auth access to the private sync repo
- Optional tools: `gh` (only for `scripts/create_private_repo.sh`), `jq` (improves grouped commit handling)

## Scripts Overview

- [`scripts/create_private_repo.sh`](scripts/create_private_repo.sh): creates a private repo with `gh repo create`.
- [`scripts/sync.sh`](scripts/sync.sh): workspace -> sync repo -> grouped commits -> push.
- [`scripts/pull.sh`](scripts/pull.sh): remote -> sync repo -> workspace copy-back.
- [`scripts/nightly_sync.sh`](scripts/nightly_sync.sh): automation wrapper for `sync.sh` that writes secret alerts to a report file.
- [`scripts/context.sh`](scripts/context.sh): CLI wrapper for `push`, `pull`, and `status`.
- [`scripts/scan_secrets.py`](scripts/scan_secrets.py): heuristic secret scanner; exits `3` when findings exist.
- [`scripts/generate_readme.py`](scripts/generate_readme.py): builds or updates a sync-repo `README.md` from a template and status input.

## Typical Usage

1. Create a private sync repo:
   `scripts/create_private_repo.sh <repo-name>`
2. Push context to the sync repo:
   `SYNC_REMOTE=git@github.com:ORG/REPO.git scripts/context.sh push`
3. Pull reviewed changes back into workspace:
   manual only, when explicitly requested:
   `SYNC_REMOTE=git@github.com:ORG/REPO.git scripts/context.sh pull`
4. Check sync-repo state:
   `scripts/context.sh status`

## Key Environment Variables

- `SYNC_REMOTE`: required unless `origin` already exists in `SYNC_REPO_DIR`.
- `WORKSPACE_DIR`: defaults to `$HOME/.openclaw/workspace`.
- `SYNC_REPO_DIR`: the location of the local repo. defaults to `$WORKSPACE_DIR/openclaw-sync-repo`.
- `PULL_DRY_RUN=1`: preview pull changes without writing.
- `PULL_DELETE=1`: allow delete propagation during pull for targeted directories.

## Commit Grouping and Export Defaults

- Exported paths are controlled by [`references/export-manifest.txt`](references/export-manifest.txt).
- Grouped commit behavior is controlled by [`references/groups.json`](references/groups.json).
- Secret-scan ignore rules are controlled by [`references/secret-scan-ignore.txt`](references/secret-scan-ignore.txt).
- If `jq` is unavailable, `sync.sh` falls back to a single commit.

## Notes

- Scripts resolve references relative to their own location (for example `scripts/../references/`).
- `pull.sh` supports agent-specific workspace restoration when `jq` and `openclaw.json` are available.
