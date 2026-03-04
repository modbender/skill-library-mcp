---
name: claw-mail
description: >
  Multi-account email management skill for IMAP/SMTP. Fetches, reads, searches,
  composes, sends, replies, forwards, and organizes emails across multiple accounts.
  Features IMAP Outbox for reliable delivery, secure credential storage via 1Password
  and macOS Keychain, TLS 1.2+ with hardened ciphers, OAuth2 authentication,
  IMAP IDLE push monitoring, connection pooling, S/MIME signing, calendar invitations,
  mail merge, conversation threading, webhook rule actions, and configurable
  dated-folder archival.
license: MIT
metadata:
  author: openclaw
  version: "0.7.0"
compatibility: >
  Requires Python 3.11+ and PyYAML. Optional: 1Password CLI (op) for op:// credentials,
  macOS for keychain:// credentials, cryptography package for S/MIME.
allowed-tools: Bash(python3 *) Read Write
---

# clawMail Skill

You are an email management agent with multi-account IMAP/SMTP support. You can
fetch, read, search, process, compose, send, reply, forward, move, and manage
emails, drafts, and folders across multiple email accounts.

## Multi-Account Model

- **Account profiles**: Each account has its own IMAP/SMTP credentials, mailboxes,
  fetch limits, archival settings, and processing rules.
- **Default account**: One account is designated as the default. Any script invoked
  without `--account` uses the default automatically.
- **SMTP fallback**: If an account's SMTP server fails, the system automatically
  retries via a configured fallback relay.
- **IMAP Outbox**: Messages are staged in a temporary Outbox folder before SMTP
  delivery. If SMTP fails, the message stays in Outbox for retry by the heartbeat.
- **Per-account + global rules**: Each account has its own rules, plus global rules
  that apply to all accounts.
- **OAuth2**: Accounts can use OAuth2 (XOAUTH2) authentication instead of passwords.
- **Dated-folder archival**: `archive_mail.py` and the heartbeat honor per-account
  `archive_root`/`archive_frequency` defaults so messages routed to the `archive`
  action land in folders such as `Archive-202603`, `Archive-W09`, or `Archive-20260315`.

## Security

- **TLS 1.2+**: All IMAP and SMTP connections enforce TLS 1.2 or higher.
- **Hardened ciphers**: Only ECDHE+AESGCM, ECDHE+CHACHA20, DHE+AESGCM, and
  DHE+CHACHA20 cipher suites are allowed. Weak ciphers (MD5, RC4, 3DES, DSS)
  are explicitly blocked.
- **Certificate verification**: Hostname checking and certificate validation are
  always enabled.
- **RFC 5322 compliance**: All outgoing emails include required Date, Message-ID,
  and MIME-Version headers automatically.
- **Secure credential storage**: Passwords in config support 1Password CLI
  (`op://vault/item/field`), macOS Keychain (`keychain://service/account`),
  and environment variables (`env://VAR_NAME`).

## Available Scripts

All scripts are in the `scripts/` directory. Run with
`python3 scripts/<name>.py` from the skill root. Every script accepts
`--account <name>` to target a specific account.

### Core Scripts

| Script | Purpose |
|--------|---------|
| `scripts/fetch_mail.py` | Fetch emails from an IMAP folder |
| `scripts/read_mail.py` | Read/render an email by Message-ID; save attachments to disk |
| `scripts/search_mail.py` | Search emails by subject, sender, body, date, flags |
| `scripts/send_mail.py` | Send rich HTML emails via SMTP (Outbox + fallback); attach files |
| `scripts/compose_mail.py` | Compose rich HTML emails from templates; attach files |
| `scripts/reply_mail.py` | Reply to an email with original-message quoting |
| `scripts/forward_mail.py` | Forward an email inline-quoted or with attachments |
| `scripts/draft_mail.py` | Save, list, resume, or send drafts via IMAP Drafts folder |
| `scripts/process_mail.py` | Run emails through the rule-based processing pipeline |
| `scripts/manage_folders.py` | List, create, delete, rename, and move IMAP folders |
| `scripts/move_mail.py` | Move emails between IMAP folders (batch support) |
| `scripts/heartbeat.py` | Run a full heartbeat cycle (drains Outbox, fetches, processes) |
| `scripts/idle_monitor.py` | Monitor a mailbox via IMAP IDLE (push notifications) |
| `scripts/retry_send.py` | Retry sending messages stuck in the IMAP Outbox |
| `scripts/calendar_invite.py` | Compose and send iCalendar meeting invitations |
| `scripts/mail_merge.py` | Batch personalised sends from template + CSV/JSON data |
| `scripts/thread_mail.py` | Group messages into conversation threads |
| `scripts/archive_mail.py` | Auto-archive old messages into dated folders (daily/weekly/monthly/yearly) |

### Library Modules

| Module | Purpose |
|--------|---------|
| `scripts/lib/imap_client.py` | IMAP client with IDLE, search, folder management, TLS 1.2+ |
| `scripts/lib/smtp_client.py` | SMTP client with TLS 1.2+, RFC 5322, OAuth2, MIME building |
| `scripts/lib/composer.py` | Rich HTML email composer with templates, reply, forward |
| `scripts/lib/processor.py` | Rule-based processing pipeline with webhook actions |
| `scripts/lib/account_manager.py` | Multi-account manager with SMTP fallback and Outbox |
| `scripts/lib/outbox.py` | IMAP Outbox — temporary folder for reliable delivery |
| `scripts/lib/credential_store.py` | Secure credential storage (1Password, Keychain, env) |
| `scripts/lib/pool.py` | Connection pool for IMAP/SMTP reuse |
| `scripts/lib/send_queue.py` | Legacy file-backed send queue (superseded by Outbox) |
| `scripts/lib/smime.py` | S/MIME signing and encryption |
| `scripts/lib/oauth2.py` | OAuth2 (XOAUTH2) token management |
| `scripts/lib/models.py` | Data models (EmailMessage, EmailAddress, etc.) |

### Reference Documents

| Reference | When to read |
|-----------|-------------|
| `references/REFERENCE.md` | API overview, all script arguments and output formats |
| `references/TEMPLATES.md` | Available email templates and template variables |
| `references/RULES.md` | How to configure processing rules |
| `ROADMAP.md` | Feature roadmap and progress tracker |

## Quick Start

### Fetching Mail

```bash
python3 scripts/fetch_mail.py --config config.yaml

python3 scripts/fetch_mail.py --account personal --unread-only --format cli --config config.yaml
```

### Sending Rich Emails

Messages are staged in a temporary IMAP Outbox folder, sent via SMTP
(with automatic fallback), then removed from Outbox on success.

```bash
python3 scripts/send_mail.py \
  --to "recipient@example.com" \
  --subject "Weekly Report" \
  --body "<p>Here are this week's results.</p>" \
  --template default \
  --attach report.pdf \
  --config config.yaml
```

### Replying and Forwarding

```bash
python3 scripts/reply_mail.py --message-id "<id@example.com>" --body "Thanks!" --config config.yaml

python3 scripts/forward_mail.py --message-id "<id@example.com>" --to "colleague@x.com" --config config.yaml
```

### Searching Emails

```bash
python3 scripts/search_mail.py --subject "invoice" --unseen --config config.yaml

python3 scripts/search_mail.py --criteria '(FROM "alice@x.com" SINCE 01-Jan-2026)' --config config.yaml
```

### Working with Drafts

```bash
python3 scripts/draft_mail.py --action save --to "user@x.com" --subject "WIP" --body "..." --config config.yaml
python3 scripts/draft_mail.py --action list --format cli --config config.yaml
python3 scripts/draft_mail.py --action send --message-id "<draft@x.com>" --config config.yaml
```

### Outbox & Send Retry

```bash
python3 scripts/retry_send.py --config config.yaml
python3 scripts/retry_send.py --config config.yaml --list
```

### Heartbeat Cycle

The heartbeat drains each account's Outbox, then fetches and processes mail:

```bash
python3 scripts/heartbeat.py --config config.yaml
python3 scripts/heartbeat.py --config config.yaml --account work
```

### Archiving Old Messages

```bash
python3 scripts/archive_mail.py --config config.yaml --days 90 --frequency monthly
python3 scripts/archive_mail.py --config config.yaml --days 30 --frequency daily --archive-root "Old Mail" --dry-run --format cli
```

Archiving honors `archive_root` / `archive_frequency` settings (defaults: `Archive`, `monthly`). The heartbeat and any rule with the `archive` action move the message into folders named `Archive-202603`, `Archive-W09`, or `Archive-20260315` based on the configured cadence.

### Calendar Invitations

```bash
python3 scripts/calendar_invite.py \
  --to "bob@example.com" --subject "Standup" \
  --start "2026-03-01T09:00:00" --end "2026-03-01T09:30:00" \
  --location "Zoom" --config config.yaml
```

### Mail Merge

```bash
python3 scripts/mail_merge.py \
  --data contacts.csv --subject "Hello {{name}}" \
  --body "<p>Dear {{name}}, your code is {{code}}.</p>" \
  --to-field email --config config.yaml
```

## Configuration

Create a `config.yaml` from `assets/config.example.yaml`:

```yaml
default_account: work

accounts:
  work:
    label: "Work"
    sender_address: "alice@company.com"
    sender_name: "Alice Smith"
    imap:
      host: imap.company.com
      port: 993
      username: "alice@company.com"
      password: "op://Work/IMAP/password"          # 1Password CLI
      ssl: true
    smtp:
      host: smtp.company.com
      port: 587
      username: "alice@company.com"
      password: "op://Work/SMTP/password"          # 1Password CLI
      tls: true
    mailboxes: [INBOX, Projects]
    fetch_limit: 50
    rules:
      - name: flag_urgent
        sender_pattern: "boss@company\\.com"
        actions: [flag, tag]
        tag: urgent

  personal:
    label: "Personal"
    sender_address: "alice@gmail.com"
    imap:
      host: imap.gmail.com
      password: "keychain://imap.gmail.com/alice@gmail.com"  # macOS Keychain
    smtp:
      host: smtp.gmail.com
      password: "keychain://smtp.gmail.com/alice@gmail.com"  # macOS Keychain
```

You can also define `archive_root` (e.g., `Archive`) and `archive_frequency` (`daily`, `weekly`, `monthly`, `yearly`) either globally or per- account. These defaults drive both the `archive_mail.py` script and the heartbeat's handling of the `archive` rule action so that archived messages consistently live under folders like `Archive-202603`, `Archive-W09`, or `Archive-20260315`.

### Secure Credential Storage

Passwords in config support four backends:

| Scheme | Backend | Example |
|--------|---------|---------|
| `op://` | 1Password CLI | `"op://Work/IMAP/password"` |
| `keychain://` | macOS Keychain | `"keychain://imap.gmail.com/alice"` |
| `env://` | Environment variable | `"env://GMAIL_APP_PASSWORD"` |
| *(plain text)* | Literal value | `"my-password"` (logs a warning) |

### OAuth2 Authentication (Gmail, Outlook 365)

For providers that require OAuth2, set `auth: oauth2` on the IMAP/SMTP block:

```yaml
imap:
  host: imap.gmail.com
  username: "user@gmail.com"
  auth: oauth2
  oauth2:
    client_id: "your-client-id"
    client_secret: "your-client-secret"
    refresh_token: "your-refresh-token"
    token_uri: "https://oauth2.googleapis.com/token"
```

### Legacy Single-Account Config

Flat `imap:` / `smtp:` at root is automatically treated as a single account
named "default".
