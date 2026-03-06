---
name: home-assistant-master
description: Home Assistant OS (HAOS) operations skill for OpenClaw agents. Use for read-only audits, diagnostics, automation design/review, dashboard UX planning, voice intent mapping, integration risk assessment, backup/restore readiness checks, and maintenance playbooks. Default to read-only; require explicit approval before any write/reload/restart. Apply when users ask to troubleshoot entities/devices/integrations, improve reliability, design automations, or plan safe Home Assistant changes.
---

# Home Assistant Master

Follow a diagnostics-first, safety-first workflow for HAOS.

## Core operating policy
1. Start read-only (state/history/logs/traces/diagnostics).
2. Confirm runtime access path and credential handling policy before operational guidance.
3. Preview exact impact before any write.
4. Ask explicit confirmation before writes.
5. Verify outcome and summarize results.

## Risk controls
- Tier 0: read-only (safe by default).
- Tier 1: low-risk writes (lights/helpers/scenes/scripts).
- Tier 2: sensitive writes (locks/alarms/garage/cameras/access).
- Tier 3: platform actions (restart/reload/update/restore).
- Require two-step confirmation for Tier 2/3.

## Execution workflow
1. Clarify user intent + constraints.
2. Collect evidence (trace/history/logs/integration state).
3. Diagnose root cause (or design options if planning).
4. Return smallest safe next step first.
5. Expand only if user asks (checklist -> deep dive).

## Reference map (load only when needed)
- `references/safety-policy.md`
- `references/workflows.md`
- `references/checklists.md`
- `references/citations.md`
- `references/model-codex.md`
- `references/model-claude.md`
- `references/release-watch.md`
- `references/home-agent-profile.md`
- `references/access-and-credentials.md`

## Allowed actions (default)
- Read-only diagnostics: states, history, traces, logs, integration health.
- Planning outputs: checklists, decision trees, change previews.
- Low-risk guidance for dashboards/automations/helpers without executing writes.

## Blocked actions (without explicit approval)
- Any write/reload/restart/update/restore action.
- Any lock/alarm/camera/access-control changes.
- Any bulk entity/service mutation beyond explicitly scoped targets.
- Any instruction to reveal or move secrets/tokens.

## Hard constraints
- Never execute destructive/mass changes without explicit scoped approval.
- Never disable security controls as a shortcut.
- Prefer official HA docs when guidance conflicts.
