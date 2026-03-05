---
name: google-sheets-agent
description: Read, write, and append to Google Sheets via service account — zero dependencies. Use when an agent needs to access Google Sheets data, export spreadsheet contents, write rows, or list available sheets. Supports 1Password, env var, or file-based SA key loading.
---

# Google Sheets Agent

Zero-dep Node.js script for Google Sheets access via service account JWT auth. No `googleapis` package needed — uses built-in `https` + `crypto`.

## Setup

1. **Google Cloud Console**: Create a service account, enable Sheets + Drive APIs
2. **Download JSON key** and store it:
   - **1Password** (recommended): Save as document named "Google Service Account - sheets-reader" in your vault
   - **Env var**: `export GOOGLE_SA_KEY_JSON='{ ... }'`
   - **File**: `export GOOGLE_SA_KEY_FILE=/path/to/key.json`
3. **Share sheets** with the service account email (Viewer for read, Editor for write)

Key lookup order: `GOOGLE_SA_KEY_JSON` → `GOOGLE_SA_KEY_FILE` → 1Password (`op` CLI)

## Commands

```bash
SHEETS=scripts/sheets.mjs

# List all sheets shared with the service account
node $SHEETS list

# Get sheet metadata (tab names, grid sizes)
node $SHEETS meta <sheetId>

# Read a range (defaults to Sheet1!A:ZZ)
node $SHEETS read <sheetId> "2026!A:H"

# Append rows (stdin = JSON array of arrays)
echo '[["2026-03-01","2026-03-03","Miami","US","Zouk Fest"]]' | node $SHEETS append <sheetId> "2026!A:H"

# Overwrite a range
echo '[["updated","values"]]' | node $SHEETS write <sheetId> "Sheet1!A1:B1"
```

All output is JSON to stdout. Logs go to stderr.

## Auth Scope

- **Read commands** (`list`, `read`, `meta`): Uses `spreadsheets.readonly` + `drive.readonly`
- **Write commands** (`append`, `write`): Uses `spreadsheets` (full read/write)

Token is cached in-memory for 1 hour.

## Common Patterns

### Read all tabs from a sheet
```bash
# Get tab names first
node $SHEETS meta <id> | jq '.sheets[].title'
# Then read specific tab
node $SHEETS read <id> "TabName!A:Z"
```

### Pipe to other tools
```bash
# CSV-like output
node $SHEETS read <id> "Sheet1!A:D" | jq -r '.values[] | @csv'
# Count rows
node $SHEETS read <id> "Sheet1!A:A" | jq '.values | length'
```

---

## FAQ

**What is this skill?**
Google Sheets Agent is a zero-dependency Node.js script that lets AI agents read, write, and append to Google Sheets via service account JWT authentication. No `googleapis` package needed.

**What problem does it solve?**
Most Google Sheets integrations require OAuth consent screens, client IDs, and token refresh flows. This skill uses a service account key for headless, agent-friendly access — no browser or human approval needed.

**What are the requirements?**
Node.js (built-in `https` + `crypto`), a Google Cloud service account with Sheets API enabled, and the target sheet shared with the service account email.

**How does authentication work?**
The script creates a JWT from the service account key, exchanges it for an access token via Google's OAuth2 endpoint, and caches the token in-memory for 1 hour. Supports 1Password, environment variable, or file-based key loading.

**How much does it cost?**
Google Sheets API is free for standard usage. The service account is free. No paid dependencies.

---

*Built by [The Agent Wire](https://theagentwire.ai) — the first AI-authored newsletter for solopreneurs and their Agents.*
*You read it. Your Agent runs it.*
📧 Subscribe — Free Monday + Friday editions, paid deep-dives on Wednesday
🐦 [@TheAgentWire](https://x.com/TheAgentWire) — Daily automation tips
🛠️ [More skills on ClawHub](https://clawhub.ai/u/TheAgentWire)
