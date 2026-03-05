# Authentication Architecture (Youmind Skill)

## Dynamic Cookie Mode (Recommended for OpenClaw Users)

If you run the [OpenClaw](https://openclaw.ai) browser alongside this skill, **you only need to log in once**. After that, cookies are fetched automatically from the running browser — no manual re-authentication required.

### How it works

1. The skill connects to the OpenClaw browser via Chrome DevTools Protocol (CDP) at `http://127.0.0.1:18800`
2. Reads fresh YouMind cookies using `Network.getAllCookies`
3. Caches them locally in `data/cdp_cache.json` with a **5-hour TTL**
4. On cache expiry, silently re-fetches from the browser

### Prerequisites

- OpenClaw browser must be running (it starts automatically with the OpenClaw gateway)
- You must have logged into YouMind **at least once** in the OpenClaw browser

### Check status

```bash
python3 scripts/cdp_auth.py --status
```

### Force refresh cache

```bash
python3 scripts/cdp_auth.py --refresh
```

---

## Fallback: Manual Login (state.json)

If the OpenClaw browser is not available, the skill falls back to `state.json` — a cookie snapshot saved after a one-time manual login:

## Overview

This skill uses a hybrid auth strategy:
1. Persistent browser profile (`user_data_dir`) for stable fingerprint/cache.
2. Explicit `state.json` save/load for robust cookie restoration.

## Why Hybrid

Persistent contexts are reliable for long-lived browser identity, but session-cookie behavior can still vary across browser restarts and product-side session rules. Saving and re-injecting storage state improves recovery consistency for automation.

## Login Flow

1. Launch Chrome persistent context.
2. Open `https://youmind.com/sign-in`.
3. User completes login manually.
4. Wait until URL leaves `sign-in` route.
5. Save `state.json` and `auth_info.json`.

Command:

```bash
python scripts/run.py auth_manager.py setup
```

## Validation Flow

1. Launch persistent context.
2. Navigate to `https://youmind.com/overview`.
3. If redirected to `sign-in`, auth is invalid.

Command:

```bash
python scripts/run.py auth_manager.py validate
```

## Stored Files

```text
data/
├── auth_info.json
└── browser_state/
    ├── state.json
    └── browser_profile/
```

## Clear/Reauth

```bash
python scripts/run.py auth_manager.py clear
python scripts/run.py auth_manager.py reauth
```

`clear` removes local auth state only; it does not delete your Youmind account or cloud data.
