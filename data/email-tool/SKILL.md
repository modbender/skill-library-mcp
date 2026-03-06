---
name: Email Skill
description: Send an email to one or more recipients.
---

# Email Skill

**Description:** Use this skill to send and read emails (IMAP/SMTP). Designed for Zoho Mail but configurable.
**Capabilities:** `email.send`, `email.search`

## Tools

### `email.send`
Send an email to one or more recipients.

Parameters:
- `to` (string, required): Comma-separated list of recipients.
- `subject` (string, required): The email subject.
- `body` (string, required): The email body (HTML or plain text).
- `cc` (string, optional): CC recipients.
- `bcc` (string, optional): BCC recipients.

### `email.search`
Search for emails in the inbox.

Parameters:
- `query` (string, required): Search query (e.g. `from:example.com`, `subject:Invoice`).
- `limit` (number, optional): Max results (default 10).
- `markRead` (boolean, optional): Mark as read after fetching (default false).

## Configuration (NO HARDCODED SECRETS)
This skill **must not** contain credentials.

It loads secrets from either:
1) A JSON file at `%OPENCLAW_SECRETS_DIR%/email-tool.json` (recommended), or
2) Environment variables (fallback).

Required keys:
- `EMAIL_USER`
- `EMAIL_PASS`

Optional (defaults shown):
- `HOST_IMAP` (imap.zoho.com)
- `PORT_IMAP` (993)
- `HOST_SMTP` (smtp.zoho.com)
- `PORT_SMTP` (465)
- `SECURE_SMTP` (true)

If you are packaging/uploading this skill: run `node scripts/secret-scan.js` first.
