---
name: gmail-cleaner
description: Clean and organize Gmail accounts in bulk. Use when asked to clean Gmail, remove spam, trash newsletters/promotional emails, bulk-delete emails by sender, create labels, set up auto-filters, or restore emails from trash. Handles single or multiple Gmail accounts via OAuth token files. Works with any Gmail account using the Gmail API.
---

# Gmail Cleaner

Bulk Gmail cleanup using the Gmail API. Processes 1000 messages per API call.

## Prerequisites

- `google-api-python-client`, `google-auth-oauthlib` Python packages (scripts auto-install if missing)
- OAuth credentials JSON from Google Cloud Console (Desktop app type)
- Token files stored as `.pkl` files per account

## Workflow

### 1. Auth (first time or new account)

```bash
python scripts/auth.py --credentials /path/to/credentials.json --token /path/to/token.pkl --scopes settings
```

- `basic` scopes: read/modify/delete messages + labels  
- `settings` scopes: adds `gmail.settings.basic` (required for creating filters)  
- Default token path: `~/.openclaw/workspace/gmail_token.pkl`
- Default creds path: `~/.openclaw/workspace/gmail_credentials.json`

For a second account, specify a different `--token` path (e.g., `gmail_token_work.pkl`).

### 2. Scan (identify what to clean)

```bash
python scripts/scan.py --token /path/to/token.pkl --sample 500
```

Shows inbox counts by category + top 40 senders. Run this first.

### 3. Clean (bulk trash/delete)

```bash
# Trash specific senders:
python scripts/clean.py --from "spam@example.com,news@example.org"

# Trash by Gmail search query:
python scripts/clean.py --query "category:promotions older_than:30d"

# From a JSON config file (list of {query, label}):
python scripts/clean.py --config senders.json

# Permanently delete instead of trash:
python scripts/clean.py --from "spam@example.com" --delete

# Dry run first:
python scripts/clean.py --from "spam@example.com" --dry-run
```

### 4. Deep Clean (comprehensive)

```bash
# Full deep clean (4 steps: trash promos → archive old → mark read → purge trash):
python scripts/deep_clean.py

# Custom age thresholds:
python scripts/deep_clean.py --promo-days 7 --archive-days 30 --unread-days 14

# Skip trash purge (keep trash for 30-day auto-delete):
python scripts/deep_clean.py --skip-trash-purge
```

### 5. Organize (labels + filters)

```bash
# Apply built-in label set (Business, Banking, Tech, Personal, Trading, Social):
python scripts/organize.py

# Custom labels/rules/filters from JSON:
python scripts/organize.py --config labels.json

# Labels only (no filters):
python scripts/organize.py --skip-filters
```

### 6. Restore (rescue emails from trash)

```bash
# Restore all emails from a sender + apply a label:
python scripts/restore.py --from healthbeat@mail.health.harvard.edu --label "Harvard Health"

# Restore by query:
python scripts/restore.py --query "from:apple.com in:trash" --label "Tech/Apple"
```

## Multiple Accounts

Run each script with a different `--token` path per account:

```bash
python scripts/scan.py    --token ~/.openclaw/workspace/gmail_token_personal.pkl
python scripts/scan.py    --token ~/.openclaw/workspace/gmail_token_work.pkl
python scripts/deep_clean.py --token ~/.openclaw/workspace/gmail_token_work.pkl
```

## Common Patterns

**Full cleanup for one account:**
```bash
python scripts/auth.py --scopes settings
python scripts/scan.py                         # identify top senders
python scripts/clean.py --from "..."          # trash specific senders
python scripts/deep_clean.py                   # clean categories
python scripts/organize.py                     # create labels + filters
```

**Rescue important emails caught in bulk delete:**
```bash
python scripts/restore.py --from important@example.com --label "Important"
```

**Senders config file format** for `clean.py --config`:
```json
[
  {"query": "from:temu@eu.temuemail.com", "label": "Temu"},
  {"query": "category:promotions older_than:7d", "label": "Old Promos"}
]
```

## Notes

- `batchModify` moves to TRASH — Gmail auto-purges after 30 days
- `batchDelete` is permanent and irreversible — always dry-run first
- Gmail filter creation requires `gmail.settings.basic` scope — re-auth with `--scopes settings` if filters fail with 403
- `scan.py` samples N messages; large inboxes may need `--sample 2000` for accuracy
- Credentials JSON comes from Google Cloud Console → APIs & Services → Credentials → OAuth 2.0 → Desktop → Download JSON
