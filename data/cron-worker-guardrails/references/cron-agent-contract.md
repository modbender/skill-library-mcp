# Cron Agent Contract (Portable Principles; POSIX Examples)

This file is a portable contract you can use for any OpenClaw cron/background worker (especially `sessionTarget="isolated"` + `payload.kind="agentTurn"`).

Goal: make scheduled jobs **reliable**, **low-noise**, and **safe-by-default**.

## 0) Core principles

1) **Scripts-first**
- If the job is more than a single short command, write a small script and have cron run **one command**.

2) **Deterministic working directory**
- Cron environments often start in an unexpected CWD.
- Always `cd` to the repo/work dir (or have the script do it).

3) **No destructive actions without explicit approval**
- Cron jobs must not delete data, patch persistent config, or mutate control-plane settings unless explicitly authorized.

4) **Silent on success**
- If your runtime supports the OpenClaw sentinel `NO_REPLY`, output exactly `NO_REPLY` on success.
- Otherwise: print nothing on success.
- Only emit a short alert when something is wrong.

## 1) Payload design rules

- Keep the cron payload message **short**.
- Avoid multi-line shell with nested quotes.
- Avoid command substitution (`$(...)` and backticks), heredocs (`<<EOF`), and complex pipelines.
- Avoid tool-driven exact-string file edits (they're brittle when whitespace/newlines drift). Prefer scripts-first, anchor-based patching.

If you need parsing, branching, JSON, retries, or file patching -> **use a script**.

## 2) Portable path rules (don't hardcode `/root/...`)

People install OpenClaw on different OSes and with different home/workspace locations.

- Do not hardcode absolute paths tied to your machine.
- Prefer:
  - paths relative to the repo (best)
  - environment variables you document (for example `WORKDIR`, `OPENCLAW_STATE_DIR`, `FINLIFE_DB_URL`)

If you must use an absolute path, make it a **single well-known variable** and document it.

## 3) Recommended execution patterns (POSIX examples)

### Pattern A - One command calling a script (best)

- Put logic in: `tools/<job_name>.py` (or `tools/<job_name>.sh`) inside the repo.
- Cron runs:

```bash
python3 tools/<job_name>.py
```

Your script should:
- validate inputs
- `chdir` to the correct directory if needed
- run subprocess calls with argv arrays (no shell)
- print `NO_REPLY` (or nothing) on success

### Pattern B - Minimal shell wrapper (only if needed)

```bash
bash -lc 'cd <REPO_DIR> && python3 tools/<job_name>.py'
```

Keep it short. If quoting gets tricky, you already crossed the line -> move logic into the script.

## 4) Failure output contract

- Failure: keep it short (<= 6 bullets)
  - what failed
  - where (file/command)
  - next action

## 5) Verification checklist

After changes, confirm:
- the job runs end-to-end without human intervention
- reruns are idempotent (no duplicated writes unless intended)
- success runs are silent
- failures are actionable and short
