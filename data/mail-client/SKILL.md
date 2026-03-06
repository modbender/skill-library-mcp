---
name: mail-client
description: "IMAP/SMTP mail client for OpenClaw agents. Use when: (1) reading or listing emails from a mailbox, (2) searching emails by sender, subject, date or text, (3) sending emails with plain text or HTML body, with optional file attachments, (4) moving, marking, or deleting messages. NOT for: bulk mailing, newsletters, calendar/contacts (use CalDAV), or providers requiring OAuth (use a dedicated skill)."
homepage: https://github.com/Rwx-G/openclaw-skill-mail-client
compatibility: Python 3.9+ - no external dependencies (stdlib only) - network access to IMAP/SMTP server
metadata:
  {
    "openclaw": {
      "emoji": "📧",
      "requires": { "env": ["MAIL_USER", "MAIL_APP_KEY", "MAIL_SMTP_HOST", "MAIL_IMAP_HOST"] },
      "primaryEnv": "MAIL_APP_KEY"
    }
  }
ontology:
  reads: [emails]
  writes: [emails, flags]
---

# mail-client

IMAP read/search + SMTP send for any standard mail server.
Python stdlib only, zero external dependencies.

---

## Trigger phrases

- "check my email"
- "do I have unread messages"
- "read the email from Alice"
- "search emails about invoice"
- "send an email to Bob"
- "move that email to the Archive folder"
- "mark that as read"
- "delete that message"
- "list my mail folders"

---

## Quick Start

```bash
python3 scripts/setup.py   # interactive setup: credentials + permissions
python3 scripts/init.py    # validate all configured capabilities
python3 scripts/mail.py config  # show current config (no secrets)
```

---

## Setup

### 1. Run setup wizard

```bash
python3 scripts/setup.py
```

The wizard collects:
- SMTP host/port, IMAP host/port
- Mail user and app key (application password)
- Which capabilities to enable (all false by default)
- Default folder and max results

### 2. Validate

```bash
python3 scripts/init.py
```

Expected output: all checks OK or SKIP (none FAIL).

### 3. Enable capabilities in config.json

Edit `~/.openclaw/config/mail-client/config.json`:

```json
{
  "allow_send": true,
  "allow_read": true,
  "allow_search": true,
  "allow_delete": false,
  "smtp_port": 587,
  "imap_port": 993,
  "mail_from": "you@example.com",
  "default_folder": "INBOX",
  "max_results": 20
}
```

---

## Storage and credentials

| Path | Written by | Purpose | Contains secrets |
|------|-----------|---------|-----------------|
| `~/.openclaw/secrets/mail_creds` | `setup.py` | SMTP/IMAP credentials + app key | YES - chmod 600, never committed |
| `~/.openclaw/config/mail-client/config.json` | `setup.py` | Behavior restrictions, folder/limit defaults | NO - behavior only, not in skill dir - survives clawhub updates |

### `~/.openclaw/secrets/mail_creds`

Written by `setup.py`, chmod 600, never committed to git. Contains:

```
MAIL_SMTP_HOST=mail.example.com
MAIL_IMAP_HOST=mail.example.com
MAIL_USER=user@example.com
MAIL_APP_KEY=app-password-here
```

Ports (`smtp_port`, `imap_port`) and sender address (`mail_from`) are set in `config.json` - they are configuration, not credentials.

Credentials can also be provided via environment variables (`MAIL_USER`, `MAIL_APP_KEY`, `MAIL_SMTP_HOST`, `MAIL_IMAP_HOST`). Environment variables take precedence over file values. The skill checks env vars first, then falls back to the creds file.

### `~/.openclaw/config/mail-client/config.json`

Written by `setup.py`. Controls behavior restrictions (which capabilities are enabled).
Contains no secrets. Not in the skill directory - survives clawhub updates.
Start from `config.example.json` in the skill dir if you prefer to create it manually.

**Cleanup on uninstall:** `clawhub uninstall mail-client` removes the skill directory. To also remove credentials and config:
```bash
python3 scripts/setup.py --cleanup
```
On reinstall, any existing config at `~/.openclaw/config/mail-client/config.json` is picked up automatically.

---

## Module usage

Import `MailClient` directly in Python:

```python
from scripts.mail import MailClient

client = MailClient()

# List 5 unread messages
msgs = client.list_messages(limit=5, unseen_only=True)
for m in msgs:
    print(m["from"], m["subject"])

# Read a message
msg = client.read_message("42")
print(msg["body"])

# Send a message
result = client.send(
    to="alice@example.com",
    subject="Hello",
    body="Hi Alice, how are you?",
)
print(result)

# Send with attachments
result = client.send(
    to="alice@example.com",
    subject="Report Q1",
    body="Please find attached the Q1 report.",
    attachments=["report.pdf", "data.xlsx"],
)
print(result)

# Search
found = client.search_messages(from_addr="bob@example.com", unseen_only=True)
```

---

## CLI reference

```
python3 scripts/mail.py <subcommand> [options]
```

| Subcommand | Requires | Description |
|------------|---------|-------------|
| `list` | allow_read | List messages (newest first) |
| `read <uid>` | allow_read | Read a full message by UID |
| `search` | allow_search | Search with filters |
| `send` | allow_send | Send an email (with optional `--attachment`) |
| `move <uid> <folder>` | allow_delete | Move message to folder |
| `mark-read <uid>` | allow_read | Mark as read |
| `mark-unread <uid>` | allow_read | Mark as unread |
| `delete <uid>` | allow_delete | Delete a message |
| `folders` | allow_read | List IMAP folders |
| `quota` | none | Get mailbox quota |
| `config` | none | Show current config |

### Examples

```bash
# List last 10 messages
python3 scripts/mail.py list --limit 10

# List unread only
python3 scripts/mail.py list --unseen

# Read message UID 42
python3 scripts/mail.py read 42

# Search from a sender since a date
python3 scripts/mail.py search --from-addr alice@example.com --since 01-Jan-2026

# Search by subject containing "invoice"
python3 scripts/mail.py search --subject "invoice"

# Send with CC
python3 scripts/mail.py send \
  --to recipient@example.com \
  --subject "Report" \
  --body "Please find attached." \
  --cc manager@example.com

# Send with attachments
python3 scripts/mail.py send \
  --to recipient@example.com \
  --subject "Report Q1" \
  --body "See attached." \
  --attachment report.pdf data.xlsx

# Move UID 42 to Archive
python3 scripts/mail.py move 42 Archive

# Mark as unread
python3 scripts/mail.py mark-unread 42

# Delete UID 42
python3 scripts/mail.py delete 42

# List folders
python3 scripts/mail.py folders

# Check quota
python3 scripts/mail.py quota
```

---

## Templates

### Agent: check and summarize unread emails

```python
from scripts.mail import MailClient

client = MailClient()
msgs = client.list_messages(unseen_only=True, limit=10)
if not msgs:
    print("No unread messages.")
else:
    for m in msgs:
        print(f"[{m['uid']}] From: {m['from']} | {m['subject']}")
```

### Agent: send a notification email

```python
from scripts.mail import MailClient

client = MailClient()
client.send(
    to="admin@example.com",
    subject="Alert: disk usage high",
    body="Disk usage has exceeded 90% on server prod-01.",
)
```

### Agent: search and archive old invoices

```python
from scripts.mail import MailClient

client = MailClient()
invoices = client.search_messages(subject="invoice", since="01-Jan-2025")
for msg in invoices:
    client.move_message(msg["uid"], "Archive/Invoices")
```

---

## Ideas

- Daily digest: list unread messages each morning and summarize senders + subjects
- Auto-archive: move messages matching certain criteria to archive folders
- Send alerts from monitoring scripts (disk, backups, errors)
- Draft-style send: compose body via LLM then send via this skill
- Combined with calendar skill: send meeting summaries by email

---

## Combine with

- `nextcloud-files` - attach or save email attachments to Nextcloud
- `ghost-admin` - email notification when a Ghost post is published
- Any monitoring or automation skill for alert delivery

---

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) for:
- Connection refused
- Authentication failed
- IMAP folder not found
- SMTP relay rejected
- Self-signed certificate workaround (local servers only)
