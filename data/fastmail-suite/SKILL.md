---
name: fastmail-suite
description: Secure, safe-by-default Fastmail integration (email, contacts, calendar) via JMAP + CalDAV. Use when you want to verify Fastmail setup, triage/search email, inspect threads, read/search contacts, view upcoming events, or (only when explicitly enabled) send email and create/reschedule/cancel calendar events. Designed for least-privilege tokens, redacted output by default, and explicit write enable switches.
env:
  FASTMAIL_TOKEN:
    required: true
    description: "Fastmail JMAP API token (Mail + Contacts scopes). Read-only is recommended by default."
  FASTMAIL_TOKEN_SEND:
    required: false
    description: "Optional Fastmail JMAP token with Email Submission scope for sending mail. Only needed when writes are explicitly enabled."
  FASTMAIL_CALDAV_USER:
    required: false
    description: "Username/email for Fastmail CalDAV (calendar app password). Required for calendar features."
  FASTMAIL_CALDAV_PASS:
    required: false
    description: "Fastmail CalDAV app password used for calendar access."
  FASTMAIL_REDACT:
    required: false
    description: "Controls redaction of output (default 1 = redacted)."
  FASTMAIL_ENABLE_WRITES:
    required: false
    description: "When set to 1, enables write operations (send/move/update). Omit or 0 to keep read-only."
metadata: { "openclaw": { "emoji": "📧" } }
---

# Fastmail Suite

Use the bundled scripts (stdlib-only) to interact with Fastmail **safely**.

## Quick start

Set credentials/tokens:

```bash
# JMAP token (Mail + Contacts scopes)
export FASTMAIL_TOKEN='…'

# CalDAV app password (calendar)
export FASTMAIL_CALDAV_USER='you@yourdomain'
export FASTMAIL_CALDAV_PASS='app-password'

# Optional: redact output (default is 1)
export FASTMAIL_REDACT=1
```

Verify setup:

```bash
python3 skills/fastmail-suite/scripts/suite.py status
```

## Suite CLI (v0.2)

### Status / onboarding checks

```bash
python3 skills/fastmail-suite/scripts/suite.py status
```

Expected style:
- `Mail (JMAP): OK` / `MISSING TOKEN` / `AUTH FAILED`
- `Calendar (CalDAV): OK` / `MISSING APP PASSWORD` / `AUTH FAILED`
- `Contacts (JMAP): OK` / `MISSING TOKEN` / `AUTH FAILED`

### Inbox triage

```bash
python3 skills/fastmail-suite/scripts/suite.py triage today
python3 skills/fastmail-suite/scripts/suite.py triage last-7d
```

Triage summarizes:
- top senders,
- action-needed subject patterns (`invoice`, `bill`, `payment`, `due`, `confirm`, `action required`, `reminder`, ...),
- highlights for `friends.tas.edu.au` and bill/payment-like items.

### Search

```bash
python3 skills/fastmail-suite/scripts/suite.py search "from:billing@ subject:invoice last:7d"
python3 skills/fastmail-suite/scripts/suite.py search "has:attachment before:2026-02-01 tax"
python3 skills/fastmail-suite/scripts/suite.py search "after:2026-02-01 reminder"
```

Supported query tokens:
- `from:foo`
- `subject:bar`
- `has:attachment`
- `last:7d` (and other `Nd` forms)
- `before:YYYY-MM-DD`
- `after:YYYY-MM-DD`
- Bare words → subject/body text search

### Thread summary

```bash
python3 skills/fastmail-suite/scripts/suite.py thread <email-id>
python3 skills/fastmail-suite/scripts/suite.py thread <thread-id>
python3 skills/fastmail-suite/scripts/suite.py thread "school invoice"
```

Shows concise thread summary:
- participants,
- rough timeline,
- latest 1–2 messages with short plain-text summary.

## Other existing scripts

### Email (JMAP)

```bash
python3 skills/fastmail-suite/scripts/fastmail.py mail inbox --limit 20
python3 skills/fastmail-suite/scripts/fastmail.py mail search "invoice" --limit 10
python3 skills/fastmail-suite/scripts/fastmail.py mail read <email-id>
```

### Contacts (JMAP)

```bash
python3 skills/fastmail-suite/scripts/fastmail.py contacts list --limit 20
python3 skills/fastmail-suite/scripts/fastmail.py contacts search "alice" --limit 5
python3 skills/fastmail-suite/scripts/fastmail.py contacts get <contact-id>
```

### Calendar (CalDAV)

```bash
python3 skills/fastmail-suite/scripts/fastmail.py calendar calendars
python3 skills/fastmail-suite/scripts/fastmail.py calendar upcoming --days 7
```

## Security & Credentials (important)

Fastmail Suite works with real Fastmail credentials, so the design is intentionally conservative.

### Required
- `FASTMAIL_TOKEN` — Fastmail JMAP API token (Mail + Contacts scopes). Best practice is to use a **read-only** token for normal usage.

### Optional but supported
- `FASTMAIL_TOKEN_SEND` — separate JMAP token with Email Submission scope for **sending mail**. Only used if you explicitly enable writes.
- `FASTMAIL_CALDAV_USER` / `FASTMAIL_CALDAV_PASS` — Fastmail app password for **calendar** (CalDAV).
- `FASTMAIL_REDACT` — controls redaction of output (default `1` = redacted).
- `FASTMAIL_ENABLE_WRITES` — when set to `1`, enables write operations (send/move/update). Omit or set to `0` to keep read-only.

### Safety model
- **Redaction is ON by default**  
  Output is redacted unless you pass `--raw` where supported. `FASTMAIL_REDACT=1` is the default.

- **Writes are OFF by default**  
  The skill will not send/move/update anything unless `FASTMAIL_ENABLE_WRITES=1` *and* you have provided appropriate tokens (for example `FASTMAIL_TOKEN_SEND` for sending mail).

- **Separation of roles**  
  You can keep a strict separation:
  - **Email reading:** `FASTMAIL_TOKEN`
  - **Email sending:** `FASTMAIL_TOKEN_SEND` (optional, only when writes are enabled)
  - **Calendar:** `FASTMAIL_CALDAV_USER` + `FASTMAIL_CALDAV_PASS` (Fastmail app password)

- **Read-only mode is fully supported**  
  You can run the entire suite (status, triage, search, thread, contacts, calendar read) with a **read-only JMAP token + calendar app password**, without ever enabling writes.

## Changelog

### v0.1.1
- Contacts commands (`list`, `search`, `get`) tested against real Fastmail accounts.
- `suite.py status` now probes Contacts via JMAP and reports `Contacts (JMAP)` health.

### v0.2
- Added `scripts/suite.py` with onboarding `status` checks for JMAP + CalDAV.
- Added mail workflows:
  - `triage today`
  - `triage last-7d`
  - `search <query>` with token parser (`from:`, `subject:`, `has:attachment`, `last:`, `before:`, `after:`)
  - `thread <id-or-snippet>` conversation summary
- Added wrapper passthrough in `scripts/fastmail.py` for `suite ...`.
- Added quick-start and usage examples for status/triage/search/thread.
