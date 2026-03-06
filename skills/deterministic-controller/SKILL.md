---
name: deterministic-controller
description: "Deterministic, evidence-gated controller templates for OpenClaw
  (HEARTBEAT/ACTIVITIES + sprint template + poll cron payload). Docs-only:
  installs no services and makes no config changes by itself."
---


# Deterministic Controller for OpenClaw (Docs-only)

## USE WHEN
- You want a **deterministic**, repeatable orchestration loop for OpenClaw (heartbeat + cron poll + subagents).
- You want **evidence-gated** completion (no DONE without artifact paths).
- You want a **lean portfolio queue** (`ACTIVITIES.md`) with external sprint-plan import via `Plan Path`.

## DON'T USE WHEN
- You want a turnkey, self-modifying installer that patches config / creates cron jobs automatically.
- You need complex runtime code; this skill is **templates + docs**.

## Outputs
- Template files under this skill folder:
  - `templates/HEARTBEAT.md`
  - `templates/ACTIVITIES.md`
  - `templates/SPRINT_TEMPLATE.md`
- Copy/paste prompts:
  - `examples/setup_prompt.md`
  - `examples/project_to_sprint_prompt.md`
- Cron payload text:
  - `docs/poll_cron_payload.txt`
- Config guidance:
  - `docs/openclaw_config_snippets.md`

## How to use
Start with the repo README:
- `README.md`

Then copy templates into your workspace and set:
- `<TELEGRAM_GROUP_ID>` in `HEARTBEAT.md`
- heartbeat prompt + cadence in `openclaw.json` (see `docs/openclaw_config_snippets.md`)

This skill intentionally does not execute commands or change config automatically.
