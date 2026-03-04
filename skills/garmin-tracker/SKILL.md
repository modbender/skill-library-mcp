---
name: garmin-tracker
description: Rebuild and maintain garmin_tracking.json from Garmin web data (activities + training plan) with a fixed schema from 2026-02-01.
metadata: { "openclaw": { "requires": { "bins": ["node", "python3"] } } }
---

# Garmin Tracker

Use this skill when the user asks to sync, rebuild, or validate Garmin training data in `garmin_tracking.json` (workspace root).

## Runtime Prerequisite

- `playwright-core` must be available in the runtime where the skill executes.
- If you get `MODULE_NOT_FOUND: playwright-core`, install it in the active workspace:

```bash
npm install playwright-core
```

## Scope

- This skill is intentionally narrow: goal tracking for Garmin runners/users (training history summary + upcoming training-plan).
- Out of scope by default: deep telemetry scraping (GPS route internals, split arrays, cadence/power/elevation raw series).
- Out of scope: nutrition workflow orchestration or external workflow integration.

## Hard Rules

- Control start date is fixed: `2026-02-01`.
- Keep these top-level fields: `lastUpdate`, `planName`, `currentWeek`, `summary`, `history`, `upcoming`, `recurring_activities`.
- `summary.to` must always be today (`YYYY-MM-DD`).
- Activities must use this canonical shape:
  - `type`
  - `distanceKm`
  - `durationSec`
  - `avgPaceSecPerKm`
  - `avgHrBpm`
  - `calories`
  - `sourceId`

## Browser Flow (Garmin)

1. Open Garmin activities list page and collect activities from `2026-02-01` onward.
2. Open Garmin training plan page (`/app/training-plan`) and refresh `currentWeek` + `upcoming`.
3. Keep extraction objective: list/table fields only. No GPS/splits/cadence/power deep scrape.
4. If browser action fails, do one in-tool recovery sequence first (`tabs` -> `focus` -> fresh `snapshot`) before escalation.

## Session/Auth Contract

- The user signs in locally to Garmin in the browser profile used by OpenClaw.
- If Garmin page indicates signed-out session, ask user to sign in and then rerun.
- Do not store user credentials in the skill files.

## Authentication (Priority Order)

Use this strict order:

1. Logged browser session (preferred): reuse existing authenticated Garmin session.
2. Guided manual login in the controlled browser/profile.
3. Credentials fallback only if browser login is not possible or explicitly rejected by the user.

`sync_training_plan.mjs` supports:

- `--auth-source auto` (default): use existing browser session; if signed out and credentials are available, try credentials login.
- `--auth-source browser`: never use credentials; require manual login.
- `--auth-source credentials`: require credentials and attempt login directly.

## Authentication (User Guidance)

If the user is signed out, guide with explicit steps:

1. Ask for manual sign-in in the controlled browser profile:
`https://connect.garmin.com/signin/` -> `https://connect.garmin.com/app/training-plan` -> rerun sync.
2. If browser sign-in is not possible, request credentials as fallback and run credentials mode.

Notes:

- Authentication policy (browser-first vs credentials-first) may be configured by the operator for each environment.
- In containerized browser setups that expose a remote UI, use the configured noVNC/VNC endpoint to complete login when needed.
- In host-browser mode, sign in directly in the host browser profile configured in OpenClaw.

## Credentials Mode (Fallback)

If browser sign-in is not possible, credentials mode can be used as fallback.

Rules:

1. Ask only what is strictly required (username/email + password, and 2FA code only if prompted).
2. Use credentials only for the login action, then discard from working memory/context when possible.
3. Never write credentials to `MEMORY.md`, `garmin_tracking.json`, logs, or skill files.
4. Never echo credentials back in responses.
5. After login success, continue with normal session-based flow.

## Data Rebuild Flow

1. Read current `garmin_tracking.json`.
2. Preserve `planName` and `recurring_activities`.
3. Rebuild `history` from Garmin activities (>= control start date).
4. Recompute `summary` from rebuilt `history`.
5. Set `summary.to` to today and `lastUpdate` to current timestamp.

## Local Validator/Reconciler Script

Use the bundled script for schema normalization and summary recomputation:

```bash
python3 {baseDir}/scripts/reconcile_tracking.py --file garmin_tracking.json --write
```

Check-only mode:

```bash
python3 {baseDir}/scripts/reconcile_tracking.py --file garmin_tracking.json
```

## Training Plan Sync Script

Use the bundled script to refresh `currentWeek` and `upcoming` from Garmin Training Plan:

```bash
node {baseDir}/scripts/sync_training_plan.mjs --file garmin_tracking.json --write
```

Credentials fallback example (last resort):

```bash
node {baseDir}/scripts/sync_training_plan.mjs \
  --auth-source credentials \
  --garmin-email "user@example.com" \
  --garmin-password "***" \
  --file garmin_tracking.json \
  --write
```

CDP resolution priority:

1. `--cdp-url` (explicit override)
2. OpenClaw config (`browser.defaultProfile` -> `browser.profiles.<profile>.cdpUrl`) from `--config` path
3. fallback to the script default CDP endpoint for local setups (`http://127.0.0.1:<port>`)

Override example:

```bash
node {baseDir}/scripts/sync_training_plan.mjs --config data/config/openclaw.json --url "https://connect.garmin.com/app/training-plan" --file garmin_tracking.json --write
```

## Minimal Parser Tests

Run parser fixtures:

```bash
node --test {baseDir}/scripts/__tests__/training_plan_parser.test.mjs
```

## Final Checks

- File is valid JSON.
- No `nutritionLog` key exists.
- `history[].activities[]` are canonical.
- `summary.to` equals today.
