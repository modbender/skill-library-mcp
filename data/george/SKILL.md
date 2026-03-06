---
name: george
description: "Automate George online banking (Erste Bank / Sparkasse Austria): login/logout, list accounts, and fetch transactions via Playwright."
summary: "George banking automation: login, accounts, transactions."
version: 1.5.2
homepage: https://github.com/odrobnik/george-skill
metadata:
  openclaw:
    emoji: "🏦"
    requires:
      bins: ["python3", "playwright"]
      python: ["playwright"]
---

# George Banking Automation

Fetch current account balances, stock portfolio, and transactions for all account types (checking, savings, depots) in JSON format for automatic processing. Uses Playwright to automate George (Erste Bank / Sparkasse Austria).

**Entry point:** `{baseDir}/scripts/george.py`

## Setup

See [SETUP.md](SETUP.md) for prerequisites and setup instructions.

## Commands

```bash
python3 {baseDir}/scripts/george.py login
python3 {baseDir}/scripts/george.py logout
python3 {baseDir}/scripts/george.py accounts
python3 {baseDir}/scripts/george.py transactions --account <id|iban> --from YYYY-MM-DD --until YYYY-MM-DD
python3 {baseDir}/scripts/george.py datacarrier-list [--json] [--state OPEN|CLOSED]
python3 {baseDir}/scripts/george.py datacarrier-upload <file> [--type pain.001] [--out <dir>] [--wait-done] [--wait-done-timeout 120]
python3 {baseDir}/scripts/george.py datacarrier-sign <datacarrier_id> [--sign-id <id>] [--out <dir>]
```

## Recommended Flow

```
login → accounts → transactions → portfolio → logout
login → datacarrier-upload → datacarrier-sign → logout
```

Always call `logout` after completing all operations to clear the stored browser session (cookies, local storage, Playwright profile). This minimizes persistent auth state on disk.

## Notes
- Session state stored in `{workspace}/george/` with restrictive permissions (dirs `700`, files `600`).
- Ephemeral exports default to `/tmp/openclaw/george` (override with `OPENCLAW_TMP`).
