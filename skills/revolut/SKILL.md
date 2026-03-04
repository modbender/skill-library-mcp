---
name: revolut
description: "Revolut web automation via Playwright: login/logout, list accounts, and fetch transactions."
summary: "Revolut banking automation: login, accounts, transactions, portfolio."
version: 1.3.2
homepage: "https://github.com/odrobnik/revolut-skill"
metadata:
  openclaw:
    emoji: "💳"
    requires:
      bins: ["python3", "playwright"]
      python: ["playwright"]
---

# Revolut Banking Automation

Fetch current account balances, investment portfolio holdings, and transactions for all wallet currencies and depots in JSON format. Uses Playwright to automate Revolut web banking.

**Entry point:** `{baseDir}/scripts/revolut.py`

## Setup

See [SETUP.md](SETUP.md) for prerequisites and setup instructions.

## Commands

```bash
python3 {baseDir}/scripts/revolut.py --user oliver login
python3 {baseDir}/scripts/revolut.py --user oliver accounts
python3 {baseDir}/scripts/revolut.py --user oliver transactions --from YYYY-MM-DD --until YYYY-MM-DD
python3 {baseDir}/scripts/revolut.py --user sylvia portfolio
python3 {baseDir}/scripts/revolut.py --user oliver invest-transactions --from YYYY-MM-DD --until YYYY-MM-DD
```

## Recommended Flow

```
login → accounts → transactions → portfolio → logout
```

Always call `logout` after completing all operations to delete the stored browser session.

## Notes
- Per-user state stored in `{workspace}/revolut/` (deleted by `logout`).
- Output paths (`--out`) are sandboxed to workspace or `/tmp`.
- No `.env` file loading — credentials in config.json only.
