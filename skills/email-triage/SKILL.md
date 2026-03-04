---
name: email-triage
version: 1.0.1
description: IMAP email scanning and triage with AI classification via a local Ollama LLM. Scans unread emails, categorizes them as urgent, needs-response, informational, or spam, and surfaces important messages for agent consumption. Works standalone with heuristic fallback — Ollama optional but recommended.
metadata:
  openclaw:
    requires:
      bins: ["python3"]
---

# Email Triage

Scan your IMAP inbox, classify emails into priority categories, and surface the ones that need attention. Uses a local LLM (Ollama) for intelligent classification with a rule-based heuristic fallback when Ollama is unavailable.

## Prerequisites

- **Python 3.10+**
- **IMAP-accessible email account** (Gmail, Fastmail, self-hosted, etc.)
- **Ollama** *(optional)* — for AI-powered classification. Without it, the script uses keyword-based heuristics that still work well for common patterns.

## Categories

| Icon | Category | Description |
|------|----------|-------------|
| 🔴 | `urgent` | Outages, security alerts, legal, payment failures, time-critical |
| 🟡 | `needs-response` | Business inquiries, questions, action items requiring a reply |
| 🔵 | `informational` | Receipts, confirmations, newsletters, automated notifications |
| ⚫ | `spam` | Marketing, promotions, unsolicited junk |

## Configuration

All configuration is via environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `IMAP_HOST` | ✅ | — | IMAP server hostname |
| `IMAP_PORT` | — | `993` | IMAP port (SSL) |
| `IMAP_USER` | ✅ | — | IMAP username / email address |
| `IMAP_PASS` | ✅ | — | IMAP password or app-specific password |
| `EMAIL_TRIAGE_STATE` | — | `./data/email-triage.json` | Path to the JSON state file |
| `OLLAMA_URL` | — | `http://127.0.0.1:11434` | Ollama API endpoint |
| `OLLAMA_MODEL` | — | `qwen2.5:7b` | Ollama model for classification |

## Directories Written

- **`EMAIL_TRIAGE_STATE`** (default: `./data/email-triage.json`) — Persistent state file tracking classified emails and surfacing status

## Commands

```bash
# Scan inbox and classify new unread emails
python3 scripts/email/email-triage.py scan

# Scan with verbose output (shows each classification)
python3 scripts/email/email-triage.py scan --verbose

# Dry run — scan and classify but don't save state
python3 scripts/email/email-triage.py scan --dry-run

# Show unsurfaced important emails (urgent + needs-response)
python3 scripts/email/email-triage.py report

# Same as report but JSON output (for programmatic use)
python3 scripts/email/email-triage.py report --json

# Mark reported emails as surfaced (so they don't appear again)
python3 scripts/email/email-triage.py mark-surfaced

# Show triage statistics
python3 scripts/email/email-triage.py stats
```

## How It Works

1. **Connects to IMAP** over SSL and fetches unread messages (up to 20 per scan).
2. **Deduplicates** by Message-ID (or a hash of subject + sender as fallback) so emails are never classified twice.
3. **Classifies** each email using Ollama if available, otherwise falls back to keyword heuristics.
4. **Stores state** in a local JSON file — tracks category, reason, and whether the email has been surfaced.
5. **`report`** surfaces only unsurfaced urgent and needs-response emails, sorted by priority.
6. **`mark-surfaced`** flags reported emails so they won't appear in future reports.
7. **Auto-prunes** state to the most recent 200 entries to prevent unbounded growth.

## Integration Tips

- **Heartbeat / cron:** Run `scan` periodically, then `report --json` to check for items needing attention.
- **Agent workflow:** `scan` → `report --json` → act on results → `mark-surfaced`.
- **Without Ollama:** The heuristic classifier handles common patterns (automated notifications, marketing, urgent keywords) well. Ollama adds nuance for ambiguous emails.
- **App passwords:** If your provider uses 2FA, generate an app-specific password for IMAP access.
