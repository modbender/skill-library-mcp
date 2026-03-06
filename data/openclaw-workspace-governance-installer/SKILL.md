---
name: openclaw-workspace-governance-installer
description: Install OpenClaw WORKSPACE_GOVERNANCE in minutes. Get guided setup, upgrade checks, migration, and audit for long-running workspaces.
author: Adam Chan
user-invocable: true
metadata: {"openclaw":{"emoji":"🚀","homepage":"https://github.com/Adamchanadam/OpenClaw-WORKSPACE-GOVERNANCE","requires":{"bins":["openclaw"]}}}
---
# OpenClaw Workspace Governance Installer

Ship safer OpenClaw operations from day one.
This installer gives you a repeatable governance path instead of ad-hoc prompt edits.

## Why this is popular
1. Prevents "edit first, verify later" mistakes.
2. Gives one predictable setup/upgrade/audit flow.
3. Makes changes traceable for review and handover.
4. Works for both beginners and production workspaces.

## 60-second quick start
First-time install:
```bash
# 1) Install plugin (first time only)
openclaw plugins install @adamchanadam/openclaw-workspace-governance@latest

# 2) Enable plugin
openclaw plugins enable openclaw-workspace-governance

# 3) Verify skills
openclaw skills list --eligible
```

In OpenClaw chat:
```text
/gov_help
/gov_setup quick
# if quick output says allowlist is not ready (for example plugins.allow needs alignment):
/gov_openclaw_json
/gov_setup quick
# manual fallback (step-by-step):
/gov_setup install
prompts/governance/OpenClaw_INIT_BOOTSTRAP_WORKSPACE_GOVERNANCE.md
# if this workspace was already active before first governance adoption:
/gov_migrate
/gov_audit
```

Already installed users (upgrade path):
```bash
# Do NOT run install again if plugin already exists
openclaw plugins update openclaw-workspace-governance
openclaw gateway restart
```

Then in OpenClaw chat:
```text
/gov_setup quick
# if quick output says allowlist is not ready (for example plugins.allow needs alignment):
/gov_openclaw_json
/gov_setup quick
/gov_setup upgrade
/gov_migrate
/gov_audit
# manual fallback:
/gov_setup upgrade
/gov_migrate
/gov_audit
```

## What you get
1. `gov_help` — see all commands and recommended entry points at a glance.
2. `gov_setup quick|check|install|upgrade` — deploy, upgrade, or verify governance in one step.
3. `gov_migrate` — align workspace behavior to the latest governance rules after install or upgrade.
4. `gov_audit` — verify 12 integrity checks and catch drift before declaring completion.
5. `gov_uninstall quick|check|uninstall` — clean removal with backup and restore evidence.
6. `gov_openclaw_json` — safely edit platform config (`openclaw.json`) with backup, validation, and rollback. Includes pre-modification config reference verification: scans local workspace docs before changes, falls back to official web docs, and degrades gracefully when neither is available.
7. `gov_brain_audit` — review and harden Brain Docs quality with preview-first approval and rollback.
8. `gov_boot_audit` — scan for recurring issues and generate upgrade proposals (read-only diagnostic).
9. `gov_apply <NN>` — apply a single BOOT upgrade proposal with explicit human approval (**Experimental**, controlled UAT only).

## Feature maturity (important)
1. GA flow for production rollout: `gov_setup -> gov_migrate -> gov_audit`, plus `gov_uninstall`, `gov_openclaw_json`, `gov_brain_audit`, `gov_boot_audit`.
2. Experimental flow: `gov_apply <NN>` (BOOT controlled apply) is included in deterministic runtime regression baseline, but remains controlled-UAT scope.
3. If you use `gov_apply <NN>`, keep it in controlled UAT and always close with `/gov_migrate` then `/gov_audit`.
4. All `/gov_*` command outputs use branded format: `🐾` header, emoji status indicators (✅/⚠️/❌), structured bullets, and `👉` next-step guidance.

## When to use which command (quick map)
1. Need command list fast: `gov_help`
2. Daily default path: `gov_setup quick` (one-click chain)
3. Readiness decision first (manual path): `gov_setup check`
4. First deployment path (manual): `gov_setup install`
5. Existing deployment update (manual): `gov_setup upgrade`
6. Policy alignment after deploy/update: `gov_migrate`
7. Final verification before claiming done: `gov_audit`
8. Cleanup workspace governance artifacts safely: `gov_uninstall quick`
9. Edit OpenClaw platform config safely: `gov_openclaw_json`
10. Review/harden Brain Docs safely: `gov_brain_audit -> gov_brain_audit APPROVE: ... -> gov_brain_audit ROLLBACK (if needed)`
11. Scan for recurring issues and get upgrade proposals: `gov_boot_audit`
12. Apply approved BOOT menu item only (Experimental): `gov_apply <NN>`

## First-run status map
After `/gov_setup quick`:
1. if output says allowlist is not ready -> run `/gov_openclaw_json`, then rerun `/gov_setup quick`
2. if output is `PASS` -> lifecycle is aligned
3. if output is `FAIL/BLOCKED` -> follow returned next-step commands
4. manual fallback remains available: `check -> install/upgrade -> migrate -> audit`

## Important update rule
If `openclaw plugins install ...` returns `plugin already exists`, use:
1. `openclaw plugins update openclaw-workspace-governance`
2. `openclaw gateway restart`
3. `/gov_setup check` (if needed, align allowlist via `/gov_openclaw_json`)
4. `/gov_setup quick` (or manual `/gov_setup upgrade` -> `/gov_migrate` -> `/gov_audit`)
5. If `/gov_setup check` says `READY`, that does not cancel an explicitly requested `/gov_setup upgrade` during update flow.

Version check (operator-side):
1. Installed: `openclaw plugins info openclaw-workspace-governance`
2. Latest: `npm view @adamchanadam/openclaw-workspace-governance version`

## Runtime gate behavior (important)
1. Read-only diagnostics/testing commands are allowed and should not be blocked.
2. **Normal writes** (skills/, projects/, code): always advisory — write proceeds with a logged warning, never hard-blocked.
3. **High-risk writes** (Brain Docs, `openclaw.json`, `_control/*`, governance prompts): advisory on 1st-2nd attempt, hard block on 3rd+ without evidence.
4. If blocked by runtime gate, this usually means governance guard worked (not a system crash). Include your plan and list of files read, then retry.
5. If blocked 3+ times: use `/gov_brain_audit force-accept` to clear all gates (with audit trail).
6. All `gov_*` responses use branded output: `🐾` header, emoji status prefix (✅ PASS/READY, ⚠️ WARNING, ❌ BLOCKED/FAIL), structured `•` bullets, `👉` next-step, and `─────` dividers.
7. Tool-exposure root-fix is enabled by default: governance plugin tools require explicit `/gov_*` intent (or `/skill gov_*`) in the current turn window.

## If slash routing is unstable
Use fallback commands:
```text
/skill gov_setup check
/skill gov_setup install
/skill gov_setup upgrade
/skill gov_migrate
/skill gov_audit
/skill gov_uninstall quick
/skill gov_openclaw_json
/skill gov_brain_audit
/skill gov_brain_audit APPROVE: APPLY_ALL_SAFE
/skill gov_brain_audit ROLLBACK
/skill gov_boot_audit
# Experimental only:
/skill gov_apply 01
```

Or natural language:
```text
Please use gov_setup in check mode (read-only) and return workspace root, status, and next action.
```

## Who this is for
1. New OpenClaw users who want a guided install path.
2. Teams operating long-running workspaces.
3. Users who need auditable, low-drift maintenance.

## Learn more (GitHub docs)
1. Main docs: https://github.com/Adamchanadam/OpenClaw-WORKSPACE-GOVERNANCE
2. English README: https://github.com/Adamchanadam/OpenClaw-WORKSPACE-GOVERNANCE/blob/main/README.md
3. 繁體中文版: https://github.com/Adamchanadam/OpenClaw-WORKSPACE-GOVERNANCE/blob/main/README.zh-HK.md
4. Governance handbook (EN): https://github.com/Adamchanadam/OpenClaw-WORKSPACE-GOVERNANCE/blob/main/WORKSPACE_GOVERNANCE_README.en.md
5. Governance handbook (繁中): https://github.com/Adamchanadam/OpenClaw-WORKSPACE-GOVERNANCE/blob/main/WORKSPACE_GOVERNANCE_README.md
6. Positioning (EN): https://github.com/Adamchanadam/OpenClaw-WORKSPACE-GOVERNANCE/blob/main/VALUE_POSITIONING_AND_FACTORY_GAP.en.md
7. Positioning (繁中): https://github.com/Adamchanadam/OpenClaw-WORKSPACE-GOVERNANCE/blob/main/VALUE_POSITIONING_AND_FACTORY_GAP.md
