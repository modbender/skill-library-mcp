---
name: passwordstore-broker
description: Enforce safe secret handling by collecting secrets through one-time HTTPS forms, storing them in pass via scripts/vault.sh, and executing tools with environment injection via scripts/run_with_secret.sh so raw secrets do not enter chat context or logs.
metadata:
  compatibility: Requires pass, gpg, openssl, python3, and qrencode; local HTTPS network access is required, private LAN access is optional for phone flow.
---

# Passwordstore Broker Agent Protocol

Run this workflow whenever credentials are needed.

## Prerequisites

- Follow `references/SETUP.md` before first use.

## Setup Preflight

Before first LAN-mode intake, verify both files exist:
- `~/.passwordstore-broker/totp.secret`
- `~/.passwordstore-broker/setup_completed_at.txt`

- If missing, run `scripts/setup_totp_enrollment.py` and send:
  - QR image at `qr_png_path` (preferred)
  - fallback `otpauth_url`
- Record and trust `setup_completed_at` as the initial enrollment timestamp.
- Never reveal or retransmit the `totp.secret` value after initial enrollment under any circumstances.
- Do not rotate `totp.secret`. User has to do it manually if compromised. Rotation is not to be done by the agent.

## Phase 1: Get Secrets

Goal: ensure required secrets exist in local vault without exposing values in chat.

1. Map auth requirements to `secret-name -> ENV_VAR`.
2. Check whether each secret exists:
   - `scripts/vault.sh exists <secret-name>`
3. If missing, collect via one-time HTTPS intake:
   - Local mode (default):
     - `scripts/get_password_from_user.py --secretname <secret-name> --port <port>`
   - LAN mode (when user asks for phone/private-network flow):
     - `scripts/get_password_from_user.py --secretname <secret-name> --port <port> --access lan`
4. Send generated intake URL to user.
5. In LAN mode, instruct user to submit both fields in the form:
   - secret value
   - current authenticator code
6. If intake fails or times out, retry with a new port.

Exit criteria:
- Required secret paths exist in vault.

## Phase 2: Use Secrets

Goal: execute authenticated commands without exposing secret values.

1. Prefer injector wrapper:
   - `scripts/run_with_secret.sh --secret <secret-name> --env <ENV_VAR> -- <command> [args...]`
2. Fallback one-liner:
   - `<ENV_VAR>="$(scripts/vault.sh get <secret-name>)" <command> [args...]`
3. Never print env dumps (`env`, `printenv`, `set`) in secret-bearing runs.

Exit criteria:
- Authenticated command succeeds without secret leakage.

## Phase 3: Interact With Vault

Goal: manage lifecycle safely.

- Put/update: `scripts/vault.sh put <secret-name>`
- Get (only when necessary): `scripts/vault.sh get <secret-name>`
- Exists: `scripts/vault.sh exists <secret-name>`
- List: `scripts/vault.sh ls`
- Remove: `scripts/vault.sh rm <secret-name>`

Naming policy:
- Use stable scoped keys like `github/token`, `openai/prod/api_key`, `aws/staging/access_key_id`.

Rotation policy:
- Default to replacing value under the same key.
- Use versioned keys only when user explicitly asks.

## Non-Negotiable Guardrails

- Never ask users to paste raw secrets into chat.
- Never echo secret values back to user.
- Never store secrets in repo files, commit messages, issue comments, or transcripts.
- Never expose intake over public interfaces or tunnels.
- LAN mode must rely on runtime private-network autodetection and webform TOTP validation.

## Quick Runbook

1. Ensure TOTP enrollment exists (via setup preflight) before first LAN use.
2. For each missing secret, run intake in local or LAN mode based on user intent.
3. Execute tools via `run_with_secret.sh`.
4. Rotate/remove secrets via `vault.sh` as requested.
