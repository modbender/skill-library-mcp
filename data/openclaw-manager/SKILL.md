---
name: openclaw-manager
description: Deploy, harden, and operate OpenClaw across local and hosted environments (Fly.io, Render, Railway, Hetzner, GCP) with secure defaults, channel setup guidance, integration onboarding, and troubleshooting workflows grounded in official OpenClaw documentation. Use when users need install/deploy help, migration support, runtime hardening, memory/agent operations tuning, or incident response.
runtime_metadata:
  deployment_modes:
    - local
    - hosted
  supported_providers:
    - local
    - fly
    - render
    - railway
    - hetzner
    - gcp
  supported_operating_systems:
    - macos
    - linux
    - windows-wsl2
  supported_channels:
    - telegram
    - discord
    - slack
  supported_integrations:
    - email
    - calendar
  security_gates:
    - env_validation_passed
    - security_checklist_passed
    - rollback_plan_documented
    - ledger_updated
  privileged_operations:
    - provider_secret_writes
    - public_network_exposure
    - persistent_state_changes
  required_env_vars:
    - OPENCLAW_GATEWAY_TOKEN
---

# OpenClaw Manager

## Overview
Build and operate OpenClaw with production-safe defaults across both local and hosted environments. This skill is optimized for operators with limited platform expertise and enforces hard security gates before rollout completion.

Primary references:
- Docs map: `references/openclaw-doc-map.md`
- Security gates checklist: `references/openclaw-security-checklist.md`
- Mode matrix: `references/openclaw-mode-matrix.md`
- OS matrix: `references/openclaw-os-matrix.md`
- Integrations playbook: `references/openclaw-integrations-playbook.md`
- Ops ledger schema: `references/openclaw-ops-ledger-schema.md`

Automation helpers:
- `scripts/plan_openclaw_rollout.py`
- `scripts/validate_openclaw_env.py`
- `scripts/update_openclaw_ops_ledger.py`

Default ops ledger path:
- `./openclaw-manager-operations-ledger.md` (or operator specified)

## Hard-Stop Rules (Never Bypass)
Stop and block deployment/install progression if any condition is true:
1. Required secrets profile fails validation.
2. Security checklist mandatory gates are not all passing.
3. Rollback path is not documented and owned.
4. Ops ledger was not updated for the current phase.
5. Public exposure requested without auth boundary and token controls.

## Workflow

### 1) Intake and Scope Lock
Collect and confirm:
- `mode`: `local` or `hosted`
- `provider`: `local`, `fly`, `render`, `railway`, `hetzner`, `gcp`
- `os`: `macos`, `linux`, `windows-wsl2`
- `channels`: subset of `telegram`, `discord`, `slack`
- `integrations`: subset of `email`, `calendar`
- `environment`: `dev`, `staging`, `prod`
- `exposure`: `private` or `public`

Before proceeding, write a `scope_lock` ledger entry:

```bash
python3 scripts/update_openclaw_ops_ledger.py \
  --ledger-file ./openclaw-manager-operations-ledger.md \
  --event scope_lock \
  --operator codex \
  --mode hosted \
  --provider fly \
  --os linux \
  --environment prod \
  --secrets-profile hosted-fly \
  --channels telegram,slack \
  --integrations email,calendar \
  --security-status pending \
  --rollback-tested no \
  --blocking-issues "none" \
  --next-owner operator \
  --next-action-date 2026-02-20
```

### 2) Generate a Decision-Complete Plan
Always generate a plan first:

```bash
python3 scripts/plan_openclaw_rollout.py \
  --mode hosted \
  --provider fly \
  --os linux \
  --channels telegram,slack \
  --integrations email,calendar \
  --environment prod \
  --exposure public \
  --ledger-file ./openclaw-manager-operations-ledger.md \
  --output /tmp/openclaw-rollout.md
```

The plan output is the execution contract. Do not skip sections.

### 3) Validate Secrets and Config Profile Before Any Infra Change
Validate environment using profile-aware gates:

```bash
python3 scripts/validate_openclaw_env.py \
  --env-file .env \
  --profile hosted-fly \
  --json
```

Validation enforces:
- required keys by profile
- required provider/model alternatives
- malformed and duplicate env keys
- placeholder values
- weak gateway/setup tokens
- legacy alias warnings

Write a `predeploy_validation` ledger entry immediately after validation.

### 4) Execute Mode Branch

#### Branch A: Local install (`mode=local`)
1. Use official install/onboarding docs for local setup.
2. Apply OS-specific commands from `references/openclaw-os-matrix.md`.
3. Validate startup, persistence path, and local auth boundaries.
4. If local public exposure is requested, apply gateway hardening gates from security checklist first.

#### Branch B: Hosted clone + deploy (`mode=hosted`)
1. Clone the selected OpenClaw source repo.
2. Follow provider playbook from `references/openclaw-doc-map.md`.
3. Configure persistent storage before production traffic.
4. Configure ingress/auth, secrets, and health checks.
5. Verify runtime logs for startup/auth errors and secret leakage.

Write a `deploy_complete` ledger entry once deployment/install is complete.

### 5) Configure Channels and Integrations Safely
For each selected channel/integration:
- inject credentials via secret manager/env only
- run a minimal smoke test
- verify auth boundaries and error logging safety

Track each item as:
- `configured`
- `pending_credentials`
- `blocked`

Use `references/openclaw-integrations-playbook.md` for email/calendar specifics.

### 6) Agent + Memory Baseline
Document and validate:
- memory persistence strategy
- retention expectations
- restart and recovery behavior
- agent behavior boundaries

Update ledger with operational baseline decisions.

### 7) Mandatory Security Gate
Run `references/openclaw-security-checklist.md` and produce pass/fail per gate.

No go-live if any mandatory gate fails.

Write a `security_gate` ledger entry with explicit blockers (if any).

### 8) Handover and Incident Readiness
Produce:
- provider status summary
- channel + integration matrix
- security gate table
- rollback and escalation ownership
- follow-up actions by risk order

Write `handover` ledger entry. For incidents/troubleshooting, append `incident` entries as events happen.

## Output Contract
Always return:
1. Mode/provider/OS/environment status summary
2. Security gate results (hard pass/fail)
3. Channel + integration matrix
4. Agent + memory configuration summary
5. Ops ledger update confirmation (event names written)
6. Follow-up actions ordered by risk
