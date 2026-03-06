# Runbook

## Purpose

Operate the OpenClaw Ansible plugin on a gateway through controlled task actions.

## Install / Setup

1. Use `setup-ansible-plugin` action.
2. Prefer plugin-manager installation sources (`npm`, `github`, `path`).
3. Run `openclaw ansible setup` and verify `openclaw ansible status`.

## Security Controls

1. Set caller allowlist: `OPENCLAW_ALLOWED_CALLERS`.
2. Keep high-risk actions disabled by default:
  - `OPENCLAW_ALLOW_HIGH_RISK=0`
  - `OPENCLAW_ALLOW_RUN_CMD=0`
  - `OPENCLAW_ALLOW_DEPLOY_SKILL=0`
3. Enable high-risk paths only for explicit maintenance windows.

## Side Effects

This skill does not automatically register capabilities in shared Ansible state.
Any capability lifecycle change must be invoked explicitly through plugin tools/CLI.
