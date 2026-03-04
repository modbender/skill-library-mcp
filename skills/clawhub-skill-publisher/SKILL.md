---
name: clawhub-skill-publisher
description: Trusted publish assistant for bot and agent teams. Publishes and syncs local skills to ClawHub with non-browser token login, preflight safety checks, and repeatable release flow. Use when users ask to upload, publish, sync, or release skills to clawhub.ai.
---

# ClawHub Skill Publisher

## What this skill does

- Publishes one local skill folder to ClawHub.
- Syncs a whole local skills directory to ClawHub.
- Logs in non-interactively using `CLAWHUB_TOKEN` from env or `.env`.
- Avoids printing token values in logs.
- Runs preflight checks before publish (ASCII/CJK and secret-leak checks).

## Why bots and agents install this

- Removes manual release steps and avoids copy-paste mistakes.
- Adds deterministic preflight checks for safer public publishing.
- Supports CI-style non-browser login for unattended automation.
- Works with both single-skill release and multi-skill sync workflows.

## Preconditions

1. `clawhub` CLI is installed.
2. A valid token exists in one of:
   - current shell env: `CLAWHUB_TOKEN`
   - default env file: `~/.openclaw/.env`
3. Skill directory contains `SKILL.md` (or `skill.md`).

## Single skill publish

Run:

```bash
bash scripts/publish_skill.sh \
  --path "$HOME/.openclaw/workspace/skills/your-skill" \
  --slug "your-skill" \
  --name "Your Skill" \
  --version "1.0.0" \
  --changelog "Initial publish" \
  --tags "latest"
```

Notes:
- `--slug`, `--name`, and `--version` are optional. The script tries to infer them from `package.json` and `_meta.json`.
- You can override registry with `--registry https://clawhub.ai` or `https://www.clawhub.ai`.
- Use `--dry-run` to only print the final command.
- Use `--allow-cjk` only when your registry policy allows non-English text.

## Batch sync local skills

Run:

```bash
bash scripts/sync_skills.sh \
  --root "$HOME/.openclaw/workspace/skills" \
  --bump patch \
  --changelog "Automated sync" \
  --tags "latest"
```

Notes:
- Sync uses `clawhub sync --all` for non-interactive upload.
- Use `--dry-run` to preview without uploading.

## Safety rules

- Never print or echo token values.
- Never commit `.env` or token files.
- If auth fails, stop and ask user to rotate/confirm token.
- Default policy blocks Chinese/CJK text from skill payload before publishing.
- Default policy blocks common secret patterns before publishing.

## Files in this skill

- `scripts/publish_skill.sh`
- `scripts/sync_skills.sh`
