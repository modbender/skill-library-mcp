---
name: ews-email
version: 1.0.0
description: "CLI to manage enterprise Outlook emails via Exchange Web Services (EWS). Use ews-mail.py to list, read, reply, forward, search, send, move, delete emails and download attachments."
metadata:
  openclaw:
    emoji: "📧"
    requires:
      bins: ["python3"]
    primaryEnv: "EWS_EMAIL"
---

# EWS Email CLI

A CLI for enterprise Exchange (EWS) email. Use when the user asks about email, inbox, messages, or mail.

## Setup

Set these environment variables before use:

- `EWS_SERVER` — Exchange server hostname (e.g. mail.company.com)
- `EWS_EMAIL` — Your email address (e.g. user@company.com)
- `EWS_PASSWORD` — Your email password

## IMPORTANT: Reading Email Content

To read the FULL content/body of an email, you MUST follow these two steps:

1. First run `envelope-list` to get the message list (this gives you numeric IDs)
2. Then run `message-read <ID>` to get the FULL email body/content

**`envelope-list` only shows subject lines and metadata. It does NOT contain the email body.**
**You MUST run `message-read` to get the actual email content. NEVER guess or summarize based on subject alone.**
**NEVER say you cannot read email content — you CAN, by running `message-read`.**

## Script Location

`~/.openclaw/skills/ews-email/scripts/ews-mail.py`

## Commands

### List Emails (step 1 — metadata only)

```bash
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py envelope-list
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py envelope-list --page 2 --page-size 20
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py envelope-list --folder "Sent"
```

### Read Email Body (step 2 — REQUIRED for content)

```bash
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py message-read <ID>
```

### Search Emails

```bash
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py envelope-list from sender@example.com
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py envelope-list subject keyword
```

### Send / Reply / Forward

```bash
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py message-send --to "email" --subject "subject" --body "body"
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py message-send --to "a@x.com" --cc "b@x.com" --subject "Hi" --body "msg"
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py message-reply <ID> --body "reply text"
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py message-reply <ID> --body "reply text" --all
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py message-forward <ID> --to "email" --body "FYI"
```

### Other Commands

```bash
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py folder-list
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py message-move <ID> "Archive"
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py message-delete <ID>
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py attachment-download <ID> --dir ~/Downloads
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py flag-add <ID> --flag seen
python3 ~/.openclaw/skills/ews-email/scripts/ews-mail.py flag-remove <ID> --flag seen
```

## Tips

- Message IDs are numeric and come from the most recent `envelope-list` output.
- Always run `envelope-list` first before `message-read`, `message-reply`, etc.
- Long email bodies are truncated at 8000 chars.
- Use `--page` and `--page-size` to navigate large inboxes.
