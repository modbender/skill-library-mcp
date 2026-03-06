# TickTick CLI Troubleshooting

## 1) Missing CLI

Symptoms:

- `ticktick: command not found`
- `No module named ticktick_cli`

Fix:

1. Ask user permission before install.
2. Install in isolated env (prefer local `.venv`).
3. Retry the same command.

If pip shows `error: externally-managed-environment`:

- Stop system install attempts.
- Use local `.venv` install flow from `references/setup-and-auth.md`.

## 2) Missing credentials (most common)

Symptoms:

- `Configuration incomplete`
- Missing one or more `TICKTICK_*` vars
- `V2 session credentials incomplete`

Fix:

1. Set all required vars, not only OAuth vars:
   - `TICKTICK_CLIENT_ID`
   - `TICKTICK_CLIENT_SECRET`
   - `TICKTICK_REDIRECT_URI`
   - `TICKTICK_ACCESS_TOKEN`
   - `TICKTICK_USERNAME`
   - `TICKTICK_PASSWORD`
2. Re-run:
   - `ticktick projects list --json`
   - then original command

## 3) Manual OAuth expires

Symptoms:

- Auth code fails or prompt times out

Fix:

1. Re-run `ticktick auth --manual`.
2. Approve immediately and paste a fresh `code`.
3. If interactive session is unstable, user runs auth locally and provides token.

## 4) Redirect mismatch

Symptoms:

- Callback fails
- Redirect mismatch error

Fix:

1. Ensure app redirect URI exactly equals `TICKTICK_REDIRECT_URI`.
2. Re-run auth.

## 5) Arg/flag errors

Symptoms:

- `unrecognized arguments`
- required argument errors

Fix:

- Use `ticktick <group> <action> --help` and retry.
