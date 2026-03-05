---
name: praxis-gws
description: Google Workspace CLI for Gmail, Calendar, and Drive. Official Google APIs wrapper for secure, direct API access without third-party proxies. Use when managing emails, calendar events, or searching Google Drive files. Supports Gmail search operators, label management, drafts, calendar event creation, and Drive file search.
---

# Praxis Google Workspace CLI

Official Google APIs wrapper for Gmail, Calendar, and Drive. Direct connection to Google — no third-party proxy.

## Setup

### 1. Create Google Cloud Project

1. Go to https://console.cloud.google.com
2. Create a new project
3. Enable these APIs:
   - Gmail API
   - Google Calendar API
   - Google Drive API

### 2. Create OAuth Credentials

1. Go to **APIs & Services → Credentials**
2. Click **Create Credentials → OAuth client ID**
3. Application type: **Desktop app**
4. Download the JSON file

### 3. Configure the CLI

```bash
praxis-gws auth credentials /path/to/client_secret.json
```

### 4. Authenticate

```bash
praxis-gws gmail labels
```

This will output a Google OAuth URL. Open it in your browser, authorize the app, and paste the authorization code back.

## Usage

### Gmail Commands

**Search messages:**
```bash
praxis-gws gmail search "is:unread from:example.com"
praxis-gws gmail search "subject:meeting has:attachment" --max 20
```

**Get message:**
```bash
praxis-gws gmail get <messageId>
```

**Send email:**
```bash
praxis-gws gmail send "recipient@example.com" "Subject" "Body text"
```

**Create draft:**
```bash
praxis-gws gmail draft "recipient@example.com" "Subject" "Draft body"
```

**List labels:**
```bash
praxis-gws gmail labels
```

**Modify labels:**
```bash
praxis-gws gmail modify <messageId> --add STARRED --remove UNREAD
```

### Calendar Commands

**List events:**
```bash
praxis-gws calendar list primary --max 10
praxis-gws calendar list primary --from "2026-02-22T00:00:00" --to "2026-03-01T23:59:59"
```

**Create event:**
```bash
praxis-gws calendar create primary "Meeting Title" \
  --from "2026-02-25T14:00:00" \
  --to "2026-02-25T15:00:00"
```

### Drive Commands

**Search files:**
```bash
praxis-gws drive search "name contains 'project'"
praxis-gws drive search "mimeType = 'application/vnd.google-apps.document'"
```

**Get file metadata:**
```bash
praxis-gws drive get <fileId>
```

## Gmail Search Operators

- `is:unread` - Unread messages
- `is:starred` - Starred messages
- `from:email@example.com` - From specific sender
- `to:email@example.com` - To specific recipient
- `subject:keyword` - Subject contains keyword
- `after:2026/01/01` - After date
- `before:2026/12/31` - Before date
- `has:attachment` - Has attachments
- `in:inbox` - In inbox
- `label:important` - With specific label

## Common Labels

- `INBOX` - Inbox
- `SENT` - Sent mail
- `DRAFT` - Drafts
- `STARRED` - Starred
- `UNREAD` - Unread
- `IMPORTANT` - Important
- `TRASH` - Trash
- `SPAM` - Spam

## Security

- OAuth tokens stored locally in `~/.config/praxis-gws/`
- Direct API connection to Google (no proxy)
- Uses official `googleapis` Node.js library
- Required scopes:
  - `https://www.googleapis.com/auth/gmail.modify`
  - `https://www.googleapis.com/auth/calendar`
  - `https://www.googleapis.com/auth/drive.readonly`

## Troubleshooting

**Error: credentials.json not found**
→ Run `praxis-gws auth credentials /path/to/client_secret.json`

**Error: Invalid grant / Token expired**
→ Delete `~/.config/praxis-gws/token.json` and re-run to trigger new OAuth flow

**"Google hasn't verified this app" warning**
→ Click **Advanced → Go to [project name] (unsafe)** to proceed

## CLI Script

The CLI is available at:
```
scripts/praxis-gws.js
```

Requires Node.js and the `googleapis` npm package:
```bash
npm install -g googleapis
```
