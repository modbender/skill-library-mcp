---
name: tenk-connect
description: Connect your TenK account to your AI assistant. Log practice sessions, check progress, and manage your 10,000-hour journey from chat.
license: MIT
metadata:
  author: OscarCode9
  version: 1.0.0
  homepage: https://github.com/OscarCode9/tenK
  requires: curl, python3
---

# TenK Connect

Manage your TenK account (tenk.oventlabs.com) from your AI assistant.
Log sessions, view skill progress, check stats, and track your path to 10,000 hours.

## Setup

On first use, run:

    bash <SKILL_DIR>/scripts/tenk.sh auth

Opens a browser URL. User logs in with TenK credentials.
CLI polls until approved. Token saved to ~/.config/tenk-connect/token (chmod 600).

## Commands

- tenk.sh auth                         Authenticate via OAuth Device Flow
- tenk.sh whoami                       Show logged-in user
- tenk.sh skills                       List all skills with accumulated hours
- tenk.sh stats                        Total hours and % progress toward 10,000h
- tenk.sh log <skill> <minutes> [note] Log a practice session
- tenk.sh streak                       Last activity per skill
- tenk.sh logout                       Clear saved token

## Usage

Use <SKILL_DIR>/scripts/tenk.sh <command> for all operations.

### Auth check

Before any command, verify authentication:

    bash <SKILL_DIR>/scripts/tenk.sh whoami

If it fails, run auth first and show the user the link and code.

### Logging sessions

When the user says something like "log 45 minutes of guitar":
1. Run tenk.sh skills to find the matching skill (fuzzy match on name)
2. Run tenk.sh log <partial_name> <minutes> [optional note]
3. Confirm with the returned result

### Showing progress

When asked about progress, hours, or stats:
- Run tenk.sh stats for totals
- Run tenk.sh skills for per-skill breakdown

## Notes

- Tokens are valid for 7 days. Re-run auth if expired.
- Skill matching is case-insensitive and fuzzy on skill name.
- Authorize URL: https://tenk.oventlabs.com/#/authorize/<code>
- API base: https://tenk.oventlabs.com/api
- Requires: curl and python3 (standard on macOS/Linux)
