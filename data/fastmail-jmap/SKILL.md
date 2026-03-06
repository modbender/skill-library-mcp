---
name: fastmail-jmap
description: "Give your AI agent email superpowers via Fastmail JMAP. Read, search, send, move, trash — zero deps. By The Agent Wire (theagentwire.ai)"
homepage: https://theagentwire.ai
env:
  FASTMAIL_TOKEN:
    required: true
    description: "Fastmail API token (starts with fmu1-). Get one at https://app.fastmail.com/settings/security/tokens"
  FASTMAIL_IDENTITY:
    required: false
    description: "Override sender email address (defaults to primary identity)"
metadata: { "openclaw": { "emoji": "📧" } }
---

# Give Your Agent Email

Your agent can browse the web, write code, and manage your calendar. But can it read your email? Check for that invoice? Send a reply?

Now it can. Zero dependencies, pure Python, Fastmail's JMAP API.

Built by [The Agent Wire](https://theagentwire.ai) — an AI agent writing a newsletter about AI agents.

## 2-Minute Quick Start

```bash
# 1. Get a Fastmail API token
#    → https://app.fastmail.com/settings/security/tokens
#    → Scopes: Email (read/write) + Email Submission (send)

# 2. Set the token
export FASTMAIL_TOKEN="fmu1-..."

# 3. Check your inbox
python3 scripts/fastmail.py unread
```

That's it. No pip install, no config files, no OAuth dance.

## Commands

| Command | What it does |
|---|---|
| `inbox [--limit N] [--unread]` | List inbox emails (newest first) |
| `unread` | Unread count per mailbox + list unread emails |
| `search <query> [--from ADDR] [--after DATE] [--before DATE]` | Full-text search across all mailboxes |
| `read <email-id>` | Read full email body |
| `send <to> <subject> <body>` | Send an email |
| `move <email-id> <mailbox-name>` | Move email to a mailbox |
| `mark-read <email-id>` | Mark as read |
| `mark-unread <email-id>` | Mark as unread |
| `trash <email-id>` | Move to trash |
| `mailboxes` | List all mailboxes with counts |

## Agent Integration

### Example reference snippet for your docs:

```markdown
## Email
Check, search, and manage email via Fastmail JMAP.
Script: `python3 scripts/fastmail.py <command>`
Env: `FASTMAIL_TOKEN` must be set.

### Checking email
- `python3 scripts/fastmail.py unread` — quick unread scan
- `python3 scripts/fastmail.py search "invoice" --after 2026-01-01` — find specific emails

### Reading email
- `python3 scripts/fastmail.py read <id>` — get full body text

### Managing email
- `python3 scripts/fastmail.py move <id> <mailbox>` — file to folder
- `python3 scripts/fastmail.py mark-read <id>` — mark as read
- `python3 scripts/fastmail.py trash <id>` — trash it

### Sending email
- `python3 scripts/fastmail.py send "user@example.com" "Subject" "Body text"`
- Always ask before sending. Never send without approval.
```

### In heartbeat/cron:

```markdown
## Email Check
Run: `python3 scripts/fastmail.py unread`
If urgent/actionable emails found, summarize and alert.
If nothing new, skip.
```

## Real-World Examples

```bash
# Morning inbox scan
python3 scripts/fastmail.py unread

# Find receipts from this month
python3 scripts/fastmail.py search "receipt" --after 2026-02-01

# Search from a specific sender
python3 scripts/fastmail.py search "meeting" --from "boss@company.com" --limit 5

# Read a specific email
python3 scripts/fastmail.py read "M1234abcd"

# File an invoice
python3 scripts/fastmail.py move "M1234abcd" "Invoices"

# Quick reply (agent should ask before sending)
python3 scripts/fastmail.py send "client@example.com" "Re: Invoice #1234" "Thanks, received and filed."

# Trash spam
python3 scripts/fastmail.py trash "Mspam5678"
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `FASTMAIL_TOKEN` | ✅ | API token from Fastmail settings |
| `FASTMAIL_IDENTITY` | ❌ | Override sender email (defaults to primary identity) |

### Getting a token

1. Go to [Fastmail Settings → Security → API Tokens](https://app.fastmail.com/settings/security/tokens)
2. Create new token
3. Enable scopes: **Email** (read/write) and **Email Submission** (for sending)
4. Copy the token (starts with `fmu1-`)

### Storing the token

For OpenClaw agents, add to your gateway config:
```json
{
  "env": {
    "vars": {
      "FASTMAIL_TOKEN": "fmu1-..."
    }
  }
}
```

Or use 1Password injection: `op run --env-file=.env -- python3 scripts/fastmail.py unread`

## How It Works

Uses [JMAP](https://jmap.io/) (JSON Meta Application Protocol) — Fastmail's modern, JSON-based email API. It's what Fastmail built to replace IMAP, and it's *fast*.

- **No IMAP/SMTP** — pure HTTP JSON requests
- **No pip dependencies** — Python 3 stdlib only (`urllib`, `json`)
- **Stateless** — no local database, no sync, just query and go
- **Batch requests** — multiple operations in a single API call

### JMAP Methods Used

| Method | Purpose |
|---|---|
| `Mailbox/get` | List folders |
| `Email/query` | Search/filter |
| `Email/get` | Fetch content |
| `Email/set` | Move, mark read/unread, trash |
| `EmailSubmission/set` | Send |
| `Identity/get` | Resolve sender address |

## Gotchas

- **Token scope matters**: Email scope for read/write, Email Submission for sending. Missing scope = 403.
- **`urn:ietf:params:jmap:core` is required** in the JMAP `using` array — omitting it gives a confusing 403.
- **Email IDs are opaque strings** (like `M1234abcd`), not numbers.
- **Search is global** by default — add `--from` or date flags to narrow results.
- **Body fetch requires explicit opt-in** — the script handles this, but if you extend it, remember `fetchTextBodyValues: true`.
- **Dates are UTC** — `--after 2026-02-18` becomes `2026-02-18T00:00:00Z` internally.

## Why Fastmail?

If you're a solopreneur running an AI agent, Fastmail is the move:

- **$5/mo** for a full email account with custom domains
- **JMAP API** — modern, fast, well-documented
- **No OAuth maze** — just an API token
- **Privacy-focused** — no scanning, no ads
- **Custom domains** — `you@yourdomain.com`
- **Sieve filters** — server-side rules that your agent can complement

Gmail's API requires OAuth2, app registration, consent screens, and token refresh. Fastmail gives you a token and gets out of the way.

## Files

- `scripts/fastmail.py` — the CLI (single file, ~300 lines)
- `SKILL.md` — this file

---

## FAQ

**What is this skill?**
Fastmail JMAP is a Python script that gives AI agents full email access — read, search, send, move, trash — via Fastmail's JMAP API. No OAuth, no client IDs, just an API token.

**What problem does it solve?**
Gmail's API requires OAuth consent screens, client IDs, redirect URIs, and token refresh flows — hostile to headless agents. Fastmail's JMAP API uses a single API token for full access. Setup takes 2 minutes, not 2 hours.

**What are the requirements?**
Python 3 (standard library only), a Fastmail account ($5/mo Standard plan), and an API token from Fastmail Settings → Privacy & Security → API Tokens.

**How much does it cost?**
Fastmail Standard is $5/mo. The API is included — no per-request charges. Compared to Google Workspace at $7.20/mo minimum.

**Can it replace Gmail for an AI agent?**
Yes. It supports inbox, unread, search, read, send, move, mark-read/unread, trash, and mailbox listing. The JMAP protocol is simpler and more agent-friendly than Gmail's REST API.

**Does it work with custom domains?**
Yes. Fastmail supports custom domains on all paid plans. You can send/receive from your own domain (e.g., agent@yourdomain.com).
