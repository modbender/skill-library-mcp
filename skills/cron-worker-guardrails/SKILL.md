---
name: cron-worker-guardrails
slug: cron-worker-guardrails
version: 1.0.5
license: MIT
description: |
  Use when: hardening OpenClaw cron/background workers (POSIX shells: bash/sh) against brittle quoting,
  cwd/env drift, and false pipeline failures (SIGPIPE, pipefail + head).
  Don't use when: the issue is application logic rather than execution-wrapper reliability.
  Output: a scripts-first hardening checklist + safe patterns (silent-on-success, deterministic cwd/env, rollback-friendly).
metadata:
  openclaw:
    emoji: "🧯"
---

# Cron Worker Guardrails (POSIX)

A reliability-first checklist for **OpenClaw cron workers** and any unattended automation.

## Scope (important)

- This skill is **POSIX-focused** (bash/sh examples).
- The *principles* are portable, but if you're on Windows/PowerShell you'll need equivalent patterns.

## The `NO_REPLY` convention

Many OpenClaw setups treat emitting exactly `NO_REPLY` as "silent success" (no human notification).

- If your runtime does not support `NO_REPLY`, interpret it as: **print nothing on success**.

## Quick Start

1) **Scripts-first:** move logic into a repo script (recommended: `tools/<job>.py` or `tools/<job>.sh`).
2) **One command in cron:** cron should run *one short command* (no multi-line `bash -lc '...'`).
3) **Deterministic cwd/env:** `cd` to the repo (or have the script do it), and document required env vars.
4) **Silent on success:** print nothing (or exactly `NO_REPLY`) when OK; only emit a short alert when broken.

Also see:
- `references/cron-agent-contract.md`
- `references/pitfalls.md`

## Why this skill exists

Cron failures are rarely "logic bugs". In practice they're often:
- brittle shell quoting (`bash -lc '...'` nested quotes)
- command substitution surprises (`$(...)`)
- one-liners that hide escaping bugs (`python -c "..."`)
- cwd/env drift ("works locally, fails in cron")
- pipelines that fail for the wrong reason (`pipefail` + `head` / SIGPIPE)

The fix is boring but effective: **scripts-first + deterministic execution + silent-on-success**.

## Portability rules (still apply)

Even on POSIX, do **not** hardcode deployment-specific absolute paths tied to one machine.

Prefer:
- repo-relative paths
- environment variables you document
- minimal wrappers that `cd` into the repo

## Common failure patterns -> fixes

### 1) `unexpected EOF while looking for matching ')'`

Likely causes:
- unclosed `$(...)` from command substitution
- broken nested quotes in `bash -lc ' ... '`

Fix pattern:
- Replace the whole multi-line shell block with a script.
- Cron calls exactly one short command, for example:
  - `python3 tools/<job>.py`

### 2) False failure from `pipefail` + `head` (SIGPIPE)

Symptom:
- command exits non-zero even though the output you wanted is fine

Fix pattern:
- avoid `pipefail` when piping into `head`
- or better: do the filtering in a script (read only what you need)

### 3) "Works locally, fails in cron"

Common causes:
- wrong working directory
- missing env vars
- different PATH

Fix pattern:
- `cd` into the repo (or have the script do it)
- keep dependencies explicit and documented

## Git footgun: `git push` rejected (non-fast-forward)

Symptom:
- `! [rejected] ... (non-fast-forward)` when automation pushes to a **long-lived PR/feature branch**.

Conservative fix (no force-push):
- On rejection, fetch the remote branch, transplant your new local commits onto it (cherry-pick), then retry push once.

## Copy/paste hardening header (portable)

Use this near the top of a cron prompt (2 lines, low-noise):

- **Hardening (MUST):** follow `references/cron-agent-contract.md` (scripts-first, deterministic cwd, silent-on-success).
- Also apply the `cron-worker-guardrails` skill. If parsing/multi-step logic is needed, write/run a small `tools/*.py` script.
