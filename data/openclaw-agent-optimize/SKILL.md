---
name: openclaw-agent-optimize
slug: openclaw-agent-optimize
version: 1.2.0
license: MIT
description: |
  Use when: you want a structured audit -> options -> recommended plan to improve an OpenClaw workspace
  (cost, model routing, context discipline, delegation, reliability).
  Don't use when: you want immediate config/cron mutations without review, or the question is unrelated to OpenClaw ops.
  Output: a prioritized plan with exact change proposals, expected impact, and rollback steps. No persistent changes without explicit approval.
triggers:
  - optimize agent
  - optimizing agent
  - improve OpenClaw setup
  - agent best practices
  - OpenClaw optimization
metadata:
  openclaw:
    emoji: "🧰"
---

# OpenClaw Agent Optimization

Use this skill to tune an OpenClaw workspace for **cost-aware routing**, **parallel-first delegation**, and **lean context**.

## Quick Start (copy/paste)

1) **Full audit (safe, no changes):**
> Audit my OpenClaw setup for cost, reliability, and context bloat. Output a prioritized plan with rollback notes. Do NOT apply changes.

2) **Context bloat / transcript noise:**
> My OpenClaw context is bloating (slow replies / high cost / lots of transcript noise). Identify the top offenders (tools, crons, bootstrap files) and propose the smallest reversible fixes first. Do NOT apply changes.

3) **Model routing / delegation posture:**
> Propose a model routing plan for (a) coding/engineering, (b) short notifications/reminders, (c) reasoning-heavy research/writing. Include an exact config patch + rollback plan, but do NOT apply changes.

## What you will get

- **Executive summary** (what matters + why)
- **Top offenders / drivers**
  - cost drivers
  - context drivers
  - reliability risks
- **Options A/B/C** (tradeoffs made explicit)
- **Recommended plan** (smallest change first)
- **Exact change proposals** (patch snippets) + **rollback**

## Safety Contract (must follow)

- Treat this skill as **advisory by default**, not autonomous control-plane mutation.
- Do not mutate persistent settings (e.g., config patch/apply) without explicit user approval.
- Do not create/update/remove cron jobs without explicit user approval.
- If an optimization reduces monitoring coverage, present options (A/B/C) and require the user to choose.
- Before any approved persistent change, show: (1) exact change, (2) expected impact, (3) rollback plan.

## Notes (skills + context)

- Some runtimes snapshot skills per session. If you install/update skills and don't see changes, start a new session.
- Prefer short `SKILL.md` + `references/` for long runbooks.

## High-ROI optimization levers (typical wins)

### 1) Output discipline for automation

Make maintenance loops **truly silent on success**.

If your runtime supports the OpenClaw sentinel `NO_REPLY`, emit exactly `NO_REPLY` on success. Otherwise, print nothing on success.

### 2) Separate "do the work" from "notify the human"

If you want alerts but want the interactive session lean:
- send a short out-of-band alert (Telegram/Slack/etc.)
- then keep the job output silent

### 3) Prefer isolated runs for unattended work

If a job should execute *without* requiring attention, prefer isolated/background execution (exact config varies by runtime).

### 4) Hardening & guardrails

- Use scripts-first for complex cron jobs (avoid fragile multi-line shell quoting).
- Add circuit breakers / global locks for heavy jobs.

### 5) Ops hygiene checklist

- Snapshot backups: freshness threshold + retention + failure markers.
- Heartbeat coverage: check model auth, disk/snapshot freshness.
- If you rely on ClawHub publishing/installs: check ClawHub auth (for example `npx clawhub whoami`).

## Workflow (concise)

1. Audit rules + memory: ensure rules are modular/short; memory keeps only restart-critical facts.
2. Model routing: confirm tiered routing (light / mid / deep) matches live config.
3. Context discipline: apply progressive disclosure; move large static data to references/scripts.
   - If transcripts are bloating, run `context-clean-up` (audit-only).
4. Delegation protocol: parallelize independent tasks; use isolated workers for long/noisy work.
5. Heartbeat optimization (control-plane only): propose options A/B/C (coverage vs cost).
6. Execution gate: if user approves changes, apply the smallest viable change first, then verify and report.

## References

- `references/optimization-playbook.md`
- `references/model-selection.md`
- `references/context-management.md`
- `references/agent-orchestration.md`
- `references/cron-optimization.md`
- `references/heartbeat-optimization.md`
- `references/memory-patterns.md`
- `references/continuous-learning.md`
- `references/safeguards.md`
