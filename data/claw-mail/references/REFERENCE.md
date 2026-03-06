# clawMail Skill — API Reference

## Script Interface

All scripts live in `scripts/` and are invoked via `python3 scripts/<name>.py`.
They accept CLI flags, read/write JSON (default) or produce CLI-formatted output
(`--format cli`), and exit 0 on success or non-zero on failure.
Errors are written to stderr as `{"error": "..."}`.

### Common Flag: `--config`

All scripts accept `--config <path>`. When omitted, scripts automatically look for
`config.yaml` in the skill root directory (one level above `scripts/`).
Passwords passed via `--imap-pass` or `--smtp-pass` are resolved through
`credential_store.resolve()`, so `op://`, `keychain://`, and `env://` URIs
work everywhere.

### Common Flag: `--account`

Every script accepts `--account <name>` to target a specific account profile.
If omitted, the `default_account` from the config file is used.

---

## fetch_mail.py

Fetch emails from an IMAP folder.

### Arguments

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--account` | string | default | Account profile name |
| `--folder` | string | `INBOX` | Folder to fetch from |
| `--limit` | int | config | Max messages (0 = use config) |
| `--unread-only` | flag | off | Only unread messages |
| `--mark-read` | flag | off | Mark fetched messages as read |
| `--format` | `json\|cli` | `json` | Output format |
| `--from-stdin` | flag | off | Read JSON messages from stdin |
| `--imap-host` | string | | Direct IMAP host (bypass config) |
| `--imap-port` | int | `993` | IMAP port |
| `--imap-user` | string | | IMAP username |
| `--imap-pass` | string | | IMAP password |
| `--imap-no-ssl` | flag | off | Disable SSL |
| `--config` | string | | YAML config file path |

### Output (JSON)

```json
{
  "account": "work",
  "folder": "INBOX",
  "count": 2,
  "messages": [{ "message_id": "...", "subject": "...", "account": "work", ... }]
}
```

---

## read_mail.py

Read and render a specific email by Message-ID. Optionally save attachments.

### Arguments

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--account` | string | default | Account profile name |
| `--message-id` | string | | Message-ID header value |
| `--folder` | string | `INBOX` | Folder to search in |
| `--save-attachments` | string | | Directory to save attachments to |
| `--format` | `json\|cli` | `json` | Output format |
| `--from-stdin` | flag | off | Read message JSON from stdin |
| IMAP flags | | | Same as fetch_mail.py |
| `--config` | string | | YAML config file |

### CLI Format

Renders the full email with headers (including account), body text, and
attachment list for terminal display.

### Saving Attachments

When `--save-attachments <dir>` is provided, all attachments are written to
the given directory. Existing files are not overwritten (a `_1`, `_2` suffix
is added). Progress is printed to stderr.

---

## send_mail.py

Send a rich HTML email via SMTP with automatic fallback.

When using `--config`, the system tries the account's SMTP server first,
then automatically falls back to the configured `smtp_fallback` relay if
the primary SMTP fails.

### Arguments

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--account` | string | default | Account profile name |
| `--to` | string (repeatable) | | Recipient address |
| `--cc` | string (repeatable) | | CC address |
| `--bcc` | string (repeatable) | | BCC address |
| `--subject` | string | | Email subject |
| `--body` | string | | Body content (HTML ok) |
| `--sender` | string | | Sender (auto from account if omitted) |
| `--template` | `default\|minimal\|digest` | `default` | Template |
| `--greeting` | string | | Greeting text |
| `--sign-off` | string | | Sign-off text |
| `--smtp-host` | string | | Direct SMTP host (bypass config) |
| `--smtp-port` | int | `587` | SMTP port |
| `--smtp-user` | string | | SMTP username |
| `--smtp-pass` | string | | SMTP password |
| `--attach` | string (repeatable) | | File path to attach |
| `--smtp-no-tls` | flag | off | Disable TLS |
| `--from-stdin` | flag | off | Read message JSON from stdin |
| `--config` | string | | YAML config file |

### Output

When using `--config`, messages are sent via the IMAP Outbox pattern:

```json
{
  "success": true,
  "transport": "smtp",
  "account": "work",
  "fallback_used": false,
  "staged_in_outbox": true,
  "subject": "...",
  "recipients": [...]
}
```

When SMTP fails but staging succeeds, `staged_in_outbox` is `true` and a `note`
field says `"Message is staged in Outbox for retry"`.

---

## compose_mail.py

Compose an email as JSON without sending. Pipe to `send_mail.py --from-stdin`.

Same arguments as `send_mail.py` minus SMTP/account flags, plus:

| Flag | Type | Description |
|------|------|-------------|
| `--items` | JSON string | Array of row dicts for digest template |
| `--columns` | JSON string | Array of column names for digest |
| `--summary` | string | Summary text for digest header |
| `--attach` | string (repeatable) | File path to attach |

---

## process_mail.py

Process emails through the rule pipeline.

### Arguments

| Flag | Type | Description |
|------|------|-------------|
| `--account` | string | Account name (loads per-account + global rules) |
| `--input` | string | JSON file path, or reads stdin |
| `--rules` | JSON string | Inline rules array |
| `--rules-file` | string | YAML/JSON rules file |
| `--config` | string | YAML config file |
| `--format` | `json\|cli` | Output format |

When using `--config --account work`, rules are loaded from the account's
`rules` list plus the top-level `rules` list (global rules), merged by priority.

---

## manage_folders.py

List, create, delete, rename, and move IMAP folders.

### Arguments

| Flag | Type | Description |
|------|------|-------------|
| `--account` | string | Account profile name |
| `--action` | `list\|create\|delete\|rename\|move` | **Required** |
| `--folder` | string | Folder name |
| `--new-name` | string | New name (for rename) |
| `--new-parent` | string | New parent (for move) |
| `--format` | `json\|cli` | Output format |
| IMAP flags | | Same as fetch_mail.py |
| `--config` | string | YAML config file |

### Actions

- **`list`**: List all folders with message/unseen/recent counts
- **`create`**: Create a new folder (and subscribe)
- **`delete`**: Delete a folder (and unsubscribe)
- **`rename`**: Rename a folder
- **`move`**: Move a folder under a new parent (delimiter-aware RENAME)

### Output (list, JSON)

```json
{
  "account": "work",
  "folders": [
    {"name": "INBOX", "delimiter": "/", "messages": 150, "unseen": 3, "recent": 1}
  ]
}
```

---

## move_mail.py

Move emails between IMAP folders (supports batch operations).

### Arguments

| Flag | Type | Description |
|------|------|-------------|
| `--account` | string | Account profile name |
| `--message-id` | string (repeatable) | Message-ID to move |
| `--from` | string | Source folder (default: INBOX) |
| `--to` | string | **Required.** Destination folder |
| `--create-folder` | flag | Create destination if missing |
| `--from-stdin` | flag | Read message IDs from stdin JSON |
| `--format` | `json\|cli` | Output format |
| IMAP flags | | Same as fetch_mail.py |
| `--config` | string | YAML config file |

### Output (JSON)

```json
{"account": "work", "from": "INBOX", "to": "Archive", "moved": 3, "failed": 0, "results": [...]}
```

---

## search_mail.py

Search emails using IMAP SEARCH criteria.

### Arguments

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--account` | string | default | Account profile name |
| `--folder` | string | `INBOX` | Folder to search |
| `--limit` | int | `50` | Max results |
| `--subject` | string | | Search in subject |
| `--from` | string | | Search by sender |
| `--to` | string | | Search by recipient |
| `--body` | string | | Search in body text |
| `--text` | string | | Full-text search (subject + body) |
| `--since` | string | | Messages since date (YYYY-MM-DD) |
| `--before` | string | | Messages before date (YYYY-MM-DD) |
| `--unseen` | flag | off | Unread messages only |
| `--flagged` | flag | off | Flagged messages only |
| `--criteria` | string | | Raw IMAP SEARCH string (overrides all other flags) |
| `--format` | `json\|cli` | `json` | Output format |
| IMAP flags | | | Same as fetch_mail.py |
| `--config` | string | | YAML config file |

### Output (JSON)

```json
{
  "account": "work",
  "folder": "INBOX",
  "criteria": "(SUBJECT \"invoice\" UNSEEN)",
  "count": 5,
  "messages": [...]
}
```

---

## reply_mail.py

Reply to an email with original-message quoting.

### Arguments

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--account` | string | default | Account profile name |
| `--message-id` | string | | Message-ID to reply to |
| `--folder` | string | `INBOX` | Folder to find message in |
| `--body` | string | **Required** | Reply body (HTML or plain) |
| `--sender` | string | | Sender address override |
| `--reply-all` | flag | off | CC all original recipients |
| `--no-quote` | flag | off | Do not quote the original message |
| `--template` | `default\|minimal\|digest` | `minimal` | Template |
| `--from-stdin` | flag | off | Read original message JSON from stdin |
| SMTP/IMAP flags | | | Same as send_mail.py / fetch_mail.py |
| `--config` | string | | YAML config file |

---

## forward_mail.py

Forward an existing email to new recipients.

### Arguments

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--account` | string | default | Account profile name |
| `--message-id` | string | | Message-ID to forward |
| `--folder` | string | `INBOX` | Folder to find message in |
| `--to` | string (repeatable) | **Required** | Forward recipient |
| `--body` | string | | Additional message body |
| `--sender` | string | | Sender address override |
| `--include-attachments` | flag | off | Carry over original attachments |
| `--from-stdin` | flag | off | Read original message JSON from stdin |
| SMTP/IMAP flags | | | Same as send_mail.py / fetch_mail.py |
| `--config` | string | | YAML config file |

---

## draft_mail.py

Save, list, resume, or send drafts via the IMAP Drafts folder.

### Arguments

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--account` | string | default | Account profile name |
| `--action` | `save\|list\|resume\|send` | **Required** | Action to perform |
| `--drafts-folder` | string | `Drafts` | IMAP drafts folder name |
| `--message-id` | string | | Message-ID for resume/send |
| `--limit` | int | `20` | Max drafts to list |
| `--to` | string (repeatable) | | Recipient (for save without stdin) |
| `--subject` | string | | Subject (for save without stdin) |
| `--body` | string | | Body (for save without stdin) |
| `--from-stdin` | flag | off | Read composed message JSON from stdin |
| `--format` | `json\|cli` | `json` | Output format |
| `--config` | string | auto | YAML config file |

### Actions

- **`save`**: Compose a message and append it to the Drafts folder
- **`list`**: List all messages in the Drafts folder
- **`resume`**: Fetch a draft by Message-ID and output as JSON
- **`send`**: Fetch a draft, send it via SMTP, and delete from Drafts

---

## heartbeat.py

Full heartbeat cycle across all accounts: fetch + process + act.
Includes message deduplication when a state file is provided.

### Arguments

| Flag | Type | Description |
|------|------|-------------|
| `--config` | string | YAML config file (auto-detected from skill root) |
| `--account` | string | Process only this account (default: all) |
| `--state-file` | string | Shared state JSON for multi-agent coordination |
| `--format` | `json\|summary` | Output format |

### Multi-Account Behavior

- When `--account` is omitted, iterates over ALL configured accounts
- Each account's mailboxes are fetched independently
- Per-account rules + global rules are applied per account
- Actions (flag, move, forward, reply) use the correct account's IMAP/SMTP
- State file is account-namespaced

### Deduplication

When `--state-file` is provided, the heartbeat tracks processed Message-IDs
in `email_seen_ids`. Messages already in the set are skipped, preventing
double-processing across heartbeat cycles. The set is capped at 10,000 entries.

### Output (JSON)

```json
{
  "timestamp": "2026-02-17T12:00:00",
  "accounts_processed": ["work", "personal"],
  "total_messages_fetched": 15,
  "duration_seconds": 3.2,
  "errors": [],
  "accounts": [
    {"account": "work", "mailboxes_checked": ["INBOX"], "messages_fetched": 10, ...},
    {"account": "personal", "mailboxes_checked": ["INBOX"], "messages_fetched": 5, ...}
  ]
}
```

---

## IMAPClient API (lib/imap_client.py)

### Custom Flags

```python
client.set_custom_flag(message_id, "$Processed", mailbox)
client.remove_custom_flag(message_id, "$Processed", mailbox)
client.set_flags_batch(["<id1>", "<id2>"], "\\Flagged", mailbox)
```

### Batch Operations

```python
# Move multiple messages in one SELECT
results = client.move_messages_batch(message_ids, "INBOX", "Archive")
# Returns: {"<id1>": True, "<id2>": False, ...}

# Flag multiple messages in one SELECT
results = client.set_flags_batch(message_ids, "\\Seen", "INBOX")
```

### Folder Move

```python
# Move "Projects" under "Archive" → "Archive/Projects"
client.move_folder("Projects", "Archive")
```

### IMAP SEARCH

```python
# Flexible search using IMAP SEARCH criteria
results = client.search(mailbox="INBOX", criteria='(FROM "alice" SUBJECT "invoice")', limit=50)
```

### Draft Support

```python
# Save a composed message to Drafts
from lib.smtp_client import build_mime
mime_msg = build_mime(message)
client.append_message(mime_msg.as_bytes(), mailbox="Drafts")
```

### OAuth2 Authentication

```python
from lib.oauth2 import OAuth2Manager
oauth2 = OAuth2Manager({"client_id": "...", "refresh_token": "...", "token_uri": "..."})
client = IMAPClient(host="imap.gmail.com", username="user@gmail.com", oauth2_manager=oauth2)
client.connect()  # Uses XOAUTH2 AUTHENTICATE instead of LOGIN
```

### IMAP IDLE (Push Notifications)

```python
# Enter IDLE mode
client.idle_start("INBOX", timeout=29*60)

# Poll for new mail events
responses = client.idle_check(timeout=30.0)
for seq_num, event_type in responses:
    if event_type == b"EXISTS":
        print("New mail!")

# Leave IDLE mode
client.idle_done()
```

### Robustness

- `_select_robust()`: Retries SELECT up to 3 times with reconnect on transient errors
- `_decode_header()`: Falls back to latin-1 for unknown charsets (fixes `unknown-8bit` LookupError)

---

## ConnectionPool (lib/pool.py)

Caches and reuses IMAP connections across operations.

```python
from lib.pool import ConnectionPool
from lib.account_manager import AccountManager

mgr = AccountManager.from_yaml("config.yaml")
with ConnectionPool(mgr, max_age=300) as pool:
    client = pool.get_imap("work")   # connects on first call
    client = pool.get_imap("work")   # returns cached connection
    smtp = pool.get_smtp("work")     # fresh SMTP per call
# close_all() called automatically on exit
```

---

## Outbox (lib/outbox.py)

IMAP-based Outbox for reliable email delivery (Apple Mail pattern).
Messages are staged in a temporary "Outbox" IMAP folder before SMTP delivery.
If SMTP fails, the message remains for later retry. When the Outbox is
drained empty, the folder is automatically removed.

```python
from lib.outbox import Outbox

outbox = Outbox(imap_client)

# Stage a message
outbox.stage(message)

# Drain all pending (send each message)
result = outbox.drain(send_fn, limit=50)
# result.sent, result.failed, result.errors

# List pending messages
pending = outbox.list_pending(limit=50)

# Check if Outbox folder exists
outbox.exists()
```

### AccountManager Integration

```python
mgr = AccountManager.from_yaml("config.yaml")

# Stage → send → cleanup in one call
result = mgr.send_via_outbox(message, "work")

# Drain all pending for an account
result = mgr.drain_outbox("work")
```

---

## Credential Store (lib/credential_store.py)

Resolves passwords and secrets from secure backends.

```python
from lib import credential_store

# Resolve any credential reference
password = credential_store.resolve("op://Work/IMAP/password")    # 1Password CLI
password = credential_store.resolve("keychain://service/account")  # macOS Keychain
password = credential_store.resolve("env://MY_SECRET")             # Environment variable
password = credential_store.resolve("plaintext")                   # Returned as-is (logs warning)
```

All scripts, including direct `--imap-pass` and `--smtp-pass` flags, OAuth2
`client_secret`/`refresh_token`, and S/MIME key passwords, are resolved
through this module.

---

## Security

### TLS Configuration

All IMAP and SMTP connections use `_create_secure_context()`:

- **Minimum version**: TLS 1.2
- **Cipher suites**: `ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20`
- **Blocked**: `!aNULL:!MD5:!DSS:!RC4:!3DES`
- **Certificate verification**: `check_hostname=True`, `verify_mode=CERT_REQUIRED`

### RFC 5322 Compliance

All outgoing emails automatically include:

- `Date:` — formatted per RFC 5322
- `Message-ID:` — generated as `<timestamp.uuid@hostname>`
- `MIME-Version: 1.0`
- `User-Agent: clawMail/0.7.0`

---

## SendQueue (lib/send_queue.py) — Legacy

> **Superseded by Outbox.** The file-backed send queue is retained for
> backwards compatibility but is no longer used by any script.

---

## idle_monitor.py

Monitor a mailbox via IMAP IDLE for real-time push notifications.

### Arguments

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--config` | string | auto | YAML config file |
| `--account` | string | default | Account profile |
| `--folder` | string | `INBOX` | Folder to monitor |
| `--timeout` | int | `1740` | IDLE timeout in seconds (29 min) |
| `--poll-interval` | float | `30.0` | Seconds between idle_check polls |
| `--max-events` | int | `0` | Stop after N events (0 = forever) |
| `--format` | `json\|cli` | `json` | Output format |

---

## retry_send.py

Drain the IMAP Outbox for one or all accounts, retrying any messages that
previously failed to send. After all messages are delivered, the Outbox
folder is automatically removed.

### Arguments

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--config` | string | auto | YAML config file |
| `--account` | string | all | Process only this account |
| `--list` | flag | off | List pending messages without sending |
| `--format` | `json\|cli` | `json` | Output format |

---

## calendar_invite.py

Compose and send iCalendar meeting invitations (VEVENT).

### Arguments

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--to` | string (repeatable) | **Required** | Attendee address |
| `--cc` | string (repeatable) | | CC address |
| `--subject` | string | **Required** | Event subject |
| `--start` | string | **Required** | Start datetime (ISO 8601) |
| `--end` | string | **Required** | End datetime (ISO 8601) |
| `--location` | string | | Event location |
| `--description` | string | | Event description |
| `--rrule` | string | | Recurrence rule (e.g. `FREQ=WEEKLY;COUNT=10`) |
| `--method` | `REQUEST\|CANCEL\|REPLY` | `REQUEST` | Calendar method |
| `--config` | string | | YAML config file |

---

## mail_merge.py

Batch personalised sends from a template + CSV/JSON data source.
Uses `{{field_name}}` placeholder syntax.

### Arguments

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--data` | string | **Required** | CSV or JSON file path |
| `--subject` | string | **Required** | Subject template |
| `--body` | string | **Required** | Body template (HTML) |
| `--to-field` | string | **Required** | Column name with email address |
| `--name-field` | string | | Column name with display name |
| `--delay` | float | `0.5` | Seconds between sends |
| `--dry-run` | flag | off | Compose without sending |
| `--attach` | string (repeatable) | | File to attach (same for all) |
| `--config` | string | | YAML config file |

---

## thread_mail.py

Group messages into conversation threads using References / In-Reply-To.

### Arguments

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--config` | string | | YAML config file |
| `--account` | string | default | Account profile |
| `--folder` | string | `INBOX` | Folder to thread |
| `--limit` | int | `100` | Max messages to fetch |
| `--from-stdin` | flag | off | Read messages JSON from stdin |
| `--format` | `json\|cli` | `json` | Output format |

### Output (JSON)

```json
{
  "total_messages": 50,
  "thread_count": 12,
  "threads": [
    {
      "thread_id": "<root@example.com>",
      "subject": "Project Update",
      "message_count": 5,
      "participants": ["alice@x.com", "bob@x.com"],
      "latest_date": "2026-02-25T14:00:00",
      "messages": [...]
    }
  ]
}
```

---

## archive_mail.py

Auto-archive old messages into dated folders (e.g. `Archive-202503`, `Archive-W11`, `Archive-20250315`) with a configurable frequency.

### Arguments

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--config` | string | | YAML config file |
| `--account` | string | default | Account profile |
| `--folder` | string | `INBOX` | Source folder |
| `--days` | int | **Required** | Archive messages older than N days |
| `--archive-root` | string | `Archive` | Parent folder for archives |
| `--frequency` | string | `monthly` | Dated folder cadence (`daily`, `weekly`, `monthly`, `yearly`) |
| `--create-folders` | flag | on | Create archive folders if needed |
| `--dry-run` | flag | off | Show what would be archived |
| `--limit` | int | `500` | Max messages to scan |
| `--format` | `json\|cli` | `json` | Output format |

---

## Processing Rules — Webhook Action

The `webhook` action POSTs a JSON payload to a URL when a rule matches.

### Config

```yaml
rules:
  - name: notify-slack
    sender_pattern: "alerts@"
    actions: [tag, webhook]
    tag: alert
    webhook_url: "https://hooks.slack.com/services/..."
```

### Payload (POST body)

```json
{
  "event": "email_rule_match",
  "message_id": "<id@example.com>",
  "subject": "Server Alert",
  "sender": "alerts@example.com",
  "recipients": ["ops@example.com"],
  "date": "2026-02-25T12:00:00",
  "account": "work",
  "mailbox": "INBOX",
  "matched_rules": ["notify-slack"],
  "tags": ["alert"]
}
```

---

## S/MIME (lib/smime.py)

Sign and encrypt outgoing emails. Requires `pip install cryptography`.

```python
from lib.smime import SMIMESigner, SMIMEEncryptor

# Sign with PEM certificate
signer = SMIMESigner(cert_path="cert.pem", key_path="key.pem")
signed_msg = signer.sign(mime_message)

# Sign with PKCS#12
signer = SMIMESigner(pkcs12_path="identity.p12", pkcs12_password="secret")

# Encrypt to recipient certificates
encryptor = SMIMEEncryptor(recipient_cert_paths=["recipient.pem"])
encrypted_msg = encryptor.encrypt(mime_message)
```
