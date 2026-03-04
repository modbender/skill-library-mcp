# TickTick CLI Setup and Auth

## Use this file when

- First-time setup
- `Configuration error` / missing `TICKTICK_*` vars
- Token refresh

## Rules (keep it simple)

- TickTick CLI requires both auth layers:
  - OAuth: `TICKTICK_CLIENT_ID`, `TICKTICK_CLIENT_SECRET`, `TICKTICK_REDIRECT_URI`, `TICKTICK_ACCESS_TOKEN`
  - Session: `TICKTICK_USERNAME`, `TICKTICK_PASSWORD`
- Collect all required values before running task/project reads.
- Do not use ad-hoc SDK/Python token-exchange scripts.

## Required `.env`

```dotenv
TICKTICK_CLIENT_ID=
TICKTICK_CLIENT_SECRET=
TICKTICK_REDIRECT_URI=http://127.0.0.1:8080/callback
TICKTICK_ACCESS_TOKEN=
TICKTICK_USERNAME=
TICKTICK_PASSWORD=
```

## Happy Path

1. Ensure CLI is available.
2. Fill `.env` with all required values except `TICKTICK_ACCESS_TOKEN`.
3. Run OAuth:
   - Desktop: `ticktick auth`
   - Headless/SSH: `ticktick auth --manual`
4. Save returned token to `TICKTICK_ACCESS_TOKEN`.
5. Verify:
   - `ticktick projects list --json`
   - `ticktick tasks today --json`

## Install Recovery (if CLI missing)

- Ask for explicit user permission before install/environment changes.
- Prefer isolated install:
  - Existing virtualenv if active
  - Otherwise local `.venv`:
    - `python3 -m venv .venv`
    - `.venv/bin/python -m pip install --upgrade pip`
    - `.venv/bin/python -m pip install --upgrade ticktick-cli`

## Manual OAuth Reliability

- Start manual auth only when user is ready to approve immediately.
- Paste the auth `code` right away; codes can expire quickly.
- If interactive prompt cannot be kept stable, have user run `ticktick auth --manual` themselves and provide the resulting access token.
