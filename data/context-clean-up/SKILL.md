---
name: context-clean-up
slug: context-clean-up
version: 1.0.5
license: MIT
description: |
  Use when: prompt context is bloating (slow replies, rising cost, noisy transcripts) and you want a ranked offender list + reversible plan.
  Don't use when: you want automatic deletions or unattended config edits.
  Output: an audit-only report (top offenders + 3-8 lowest-risk fixes + rollback notes). No changes are applied automatically.
disable-model-invocation: true
allowed-tools:
  - read
  - exec
  - sessions_list
  - sessions_history
  - session_status
metadata: { "openclaw": { "emoji": "🧹", "requires": { "bins": ["python3"] } } }
---

# Context Clean Up (audit-only)

This skill is a **runbook** to identify what is bloating your prompt context and produce a **safe, reversible plan**.

**Important:** this skill is intentionally **audit-only**.
- It will not delete data, prune sessions, patch config, or modify cron jobs.
- If you ask for changes, it will propose an exact patch + rollback plan and wait for explicit approval.

## Quick start

- `/context-clean-up` -> audit + actionable plan (no changes)

If you can run the bundled audit script, you can also generate a JSON report:

```text
python3 scripts/context_cleanup_audit.py --out context-cleanup-audit.json
```

If your Python executable is not `python3` (common on Windows):

```text
py -3 scripts/context_cleanup_audit.py --out context-cleanup-audit.json
```

## A note on `NO_REPLY`

Some OpenClaw setups use `NO_REPLY` as a sentinel meaning "silent success" (no human notification).

- If your runtime does not support it, interpret this as: print nothing on success.

## Common offenders (what usually causes bloat)

Typical high-impact sources (roughly in descending frequency):

1) Tool result dumps
- large `exec` output pasted back into chat
- big `read` outputs (logs, JSON, lockfiles)
- web fetches that inject long pages

2) Automation transcript noise
- cron jobs that report "OK" every run
- heartbeat outputs that are not strictly alert-only

3) Bootstrap reinjection bloat
- overgrown `AGENTS.md` / `MEMORY.md` / `SOUL.md` / `USER.md`
- large runbooks embedded directly in `SKILL.md` instead of `references/`

4) Repeated summaries that never get trimmed
- summaries that accrete historical detail instead of staying restart-critical

## Negative examples (don't run this skill)

- "Delete old sessions / prune logs / apply fixes now" -> this skill is audit-only.
- "Change my OpenClaw config automatically" -> must ask first.
- "Investigate a specific bug in app code" -> use repo-specific debugging instead.

## Workflow (audit -> plan)

### Step 0 - Determine scope

You need:
- Workspace dir: where your workspace/project files live
- State dir: where the runtime stores sessions/memory (call it `<OPENCLAW_STATE_DIR>`)

Common defaults (may vary by install):
- macOS/Linux: `~/.openclaw`
- Windows: `%USERPROFILE%\.openclaw`

The audit script supports overrides via `--state-dir` or the `OPENCLAW_STATE_DIR` env var.

### Step 1 - Run the audit script

This script prints a short stdout summary and can write a JSON report.

```text
python3 scripts/context_cleanup_audit.py --workspace . --state-dir <OPENCLAW_STATE_DIR> --out context-cleanup-audit.json
```

Interpretation cheatsheet:
- huge tool outputs (exec/read/web_fetch): transcript bloat
- many `System:` / `Cron:` lines: automation bloat
- large bootstrap docs (AGENTS/MEMORY/SOUL/USER): reinjected rules bloat

### Step 2 - Produce a fix plan (lowest-risk first)

Create a short plan with:
- top offenders (largest transcript entries)
- noisiest recurring jobs (cron/heartbeat)
- quick wins (reversible)

Standard levers:

#### Lever A - Make no-op automation truly silent

Goal: maintenance loops should output exactly `NO_REPLY` (or nothing) unless there is an anomaly.

#### Lever B - Keep notifications, avoid transcript injection

If you want alerts but want the interactive session lean:
- send out-of-band (Telegram/Slack/etc.)
- then keep job output silent

See: `references/out-of-band-delivery.md`

#### Lever C - Keep injected bootstrap files small

- keep only restart-critical rules in `MEMORY.md`
- move bulky notes into `references/*.md` or `memory/*.md`

### Step 3 - Verify

After you apply any changes:
- confirm the next cron/heartbeat runs are silent on success
- watch context growth rate (it should flatten)

## References

- `references/out-of-band-delivery.md`
- `references/cron-noise-checklist.md`
