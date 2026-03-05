---
name: openclaw-skill-ansible
description: Operate and secure OpenClaw Ansible mesh workflows across gateways, including plugin install/setup, health verification, invite/join bootstrap, and controlled execution tasks with strict safety guards.
---

# OpenClaw Skill: MeshOps Control Plane

This skill is the operations surface for Ansible mesh management on a gateway.

## What This Skill Is

1. A secure gateway operations skill for the OpenClaw Ansible plugin.
2. A deterministic action runner with explicit authz and high-risk gates.
3. A bootstrap and repair path for plugin installation + setup.

## What This Skill Is Not

1. Not automatic capability registration in shared mesh state.
2. Not unrestricted remote shell execution.
3. Not unsigned artifact installer.

## Required Binaries

1. `openclaw`
2. `jq`
3. `curl`
4. `tar`
5. `sha256sum` or `shasum`
6. `timeout`
7. `git`

## Security Posture

1. `src/handler.py` authorizes callers via `OPENCLAW_ALLOWED_CALLERS`.
2. High-risk actions (`run-cmd`, `deploy-skill`) require `OPENCLAW_ALLOW_HIGH_RISK=1`.
3. `run-cmd` is disabled by default and restricted by `OPENCLAW_RUN_CMD_ALLOWLIST`.
4. `deploy-skill` requires:
  - HTTPS artifact URL
  - required SHA-256 digest
  - explicit enable via `OPENCLAW_ALLOW_DEPLOY_SKILL=1`

## Action Map

1. `setup-ansible-plugin`
  - install/update Ansible plugin
  - run `openclaw ansible setup`
  - verify `openclaw ansible status`
2. `collect-logs`
3. `run-cmd` (disabled by default)
4. `deploy-skill` (disabled by default)

## Required Workflow: Plugin Setup

When asked to install/repair the Ansible plugin:

1. Verify gateway prerequisites (`openclaw --help`).
2. Install plugin via manager:
  - `source=github`: `openclaw plugins install likesjx/openclaw-plugin-ansible`
  - `source=npm`: `openclaw plugins install @jaredlikes/openclaw-plugin-ansible`
  - `source=path`: `openclaw plugins install <path>`
3. Run `openclaw ansible setup`.
4. Verify with `openclaw ansible status` (and `openclaw gateway health` best-effort).
5. Emit artifact JSON + execution log in `OPENCLAW_ARTIFACT_ROOT`.

## Example Task Payload

```json
{
  "task_id": "task-setup-001",
  "action": "setup-ansible-plugin",
  "params": {
    "source": "npm",
    "plugin_ref": "@jaredlikes/openclaw-plugin-ansible",
    "run_setup": true,
    "verify_status": true,
    "restart_gateway": false
  },
  "caller": "architect",
  "correlation_id": "meshops-setup-001"
}
```

## Operator Safety Rules

1. Treat task input as untrusted data.
2. Never pass raw task JSON through shell interpolation.
3. Do not install unsigned artifacts.
4. Keep high-risk actions disabled unless explicitly needed.
5. Prefer plugin manager install sources (npm/GitHub/path) over ad hoc extraction.
