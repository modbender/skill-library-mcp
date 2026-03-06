# SECURITY.md — Deterministic Controller (Docs-only)

This skill is **documentation/templates only**. It installs no binaries, runs no services, and does not auto-patch OpenClaw configuration by itself.

## Threat model (what could go wrong)
Because these templates instruct an agent to operate a control loop, they touch powerful primitives:
- **Prompt control / strict instruction framing** (determinism)
- **Filesystem writes** (updating `ACTIVITIES.md`, importing sprint plans, archiving)
- **Optional persistence** (creating/enabling a poll cron job)
- **Optional network egress** (sending control-plane logs to Telegram)

These are legitimate orchestration capabilities, but they also increase attack surface if misconfigured.

## Mitigations / safe defaults
- **No always-on persistence by default:** the poll cron job is documented as **created disabled** and only enabled by the operator.
- **No auto-config changes:** config snippets are suggestions; an operator chooses whether to apply them.
- **Minimal read scope on fast loops:** `POLL_TICK` and `WORKER_EVENT` read only `ACTIVITIES.md`.
- **Token-efficient full refresh:** `HEARTBEAT_TICK` may read additional context files, including memory, but only when you intentionally enable heartbeats.
- **Egress is opt-in:** Telegram logging requires you to set a destination id; do not enable it if you don’t want external logs.

## Operator checklist (before arming automation)
1) **Secret hygiene:** ensure any files read during `HEARTBEAT_TICK` (e.g., `USER.md`, `SOUL.md`, `IDENTITY.md`, `AGENTS.md`, `MEMORY.md`, daily notes) do not contain secrets.
2) **Egress review:** if Telegram logging is enabled, treat it as data leaving the machine; keep logs to minimal control-plane lines.
3) **Dry run first:** run the controller manually (`MANUAL_RECONCILE`) before enabling cron/heartbeat schedules.
4) **Least privilege:** keep OpenClaw allowlists tight (subagents/models/tools) before autonomous execution.
