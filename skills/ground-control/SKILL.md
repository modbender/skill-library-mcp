---
name: ground-control
description: Post-upgrade verification system for OpenClaw. Defines a model/cron/channel ground truth file and a 5-phase automated verification flow (config integrity, API key liveness, cron integrity, session smoke test, channel liveness) with auto-repair for config and cron drift.
version: "0.2.2"
metadata:
  author: JonathanJing
  tags: [ops, verification, upgrade, config, cron, health]
  license: MIT
  credentials:
    mode: user-declared
    source: MODEL_GROUND_TRUTH.md → non_llm_providers[].env_var
    note: >
      This skill reads env vars that the USER declares in their MODEL_GROUND_TRUTH.md file.
      The set of env vars is not known at publish time — it depends on which providers
      the user configures. Common examples: BRAVE_API_KEY, NOTION_TOKEN.
      Credentials are only sent to HTTPS endpoints whose hostname exactly matches
      the user-declared allowed_domain. See SKILL.md Permissions section for full policy.
---

# ground-control

Post-upgrade verification for OpenClaw. Keeps your system honest after every upgrade.

## Permissions & Privileges

This skill requires the following OpenClaw capabilities:
- **`gateway config.get`** — read current config (all phases)
- **`gateway config.patch`** — auto-fix config drift (Phase 1 only)
- **`cron list` / `cron update`** — verify and auto-fix cron jobs (Phase 3)
- **`sessions_spawn`** — smoke test sessions (Phase 2, 4, 5)
- **`message send`** — channel liveness test + summary report (Phase 5)

**Auto-fix behavior:** Phases 1 and 3 will automatically patch config/cron to match GROUND_TRUTH. Use `--dry-run` to disable auto-fix and get a report-only run.

**Environment variables:** Phase 2 tests non-LLM provider keys (e.g., Brave, Notion). Security model:
- Only env vars explicitly named in `MODEL_GROUND_TRUTH.md` → `non_llm_providers[].env_var` are read
- Credentials are ONLY sent to HTTPS endpoints whose hostname exactly matches the entry's `allowed_domain`
- Endpoint validation is mandatory before every curl — hostname mismatch = skip + report ❌
- The skill never enumerates, dumps, or logs environment variable values
- If no `non_llm_providers` section exists in GROUND_TRUTH, non-LLM checks are skipped entirely

## When to use

- After running `openclaw update` or `npm install -g openclaw@latest`
- When you suspect config drift (model changed, cron broken, channel down)
- Periodic health check via `/verify` command

## Setup

1. Copy `templates/MODEL_GROUND_TRUTH.md` to your workspace root
2. Fill in your actual config values (models, cron jobs, channels)
3. Add the GROUND_TRUTH sync rule to your AGENTS.md (see README)
4. Run `/verify` to test

## Files

- `templates/MODEL_GROUND_TRUTH.md` — Ground truth template (copy to workspace root)
- `scripts/post-upgrade-verify.md` — Agent execution prompt for 5-phase verification
- `scripts/UPGRADE_SOP.md` — Upgrade standard operating procedure
