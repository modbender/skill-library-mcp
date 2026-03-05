---
name: outlook
description: Read, search, and manage Outlook emails and calendar via Microsoft Graph API. Use when the user asks about emails, inbox, Outlook, Microsoft mail, calendar events, or scheduling.
version: 1.9.0
author: cristiandan
homepage: https://github.com/cristiandan/outlook-skill
metadata: {"clawdbot":{"requires":{"bins":["az","jq"]},"credentials":{"note":"Setup creates Azure App Registration and stores client_id/client_secret/OAuth tokens in ~/.outlook-mcp. The token script can print access tokens. Treat these as sensitive."}}}
---

# Outlook Skill

Access Outlook/Hotmail email and calendar via Microsoft Graph API using OAuth2.

## Quick Setup (Automated)

```bash
# Requires: Azure CLI, jq
./scripts/outlook-setup.sh
```

The setup script will:
1. Log you into Azure (device code flow)
2. Create an App Registration automatically
3. Configure API permissions (Mail.ReadWrite, Mail.Send, Calendars.ReadWrite)
4. Guide you through authorization
5. Save credentials to `~/.outlook-mcp/`

## Manual Setup

See `references/setup.md` for step-by-step manual configuration via Azure Portal.

## Multiple Accounts

You can connect multiple Outlook accounts (personal, work, etc.):

### Setup additional accounts
```bash
./scripts/outlook-setup.sh --account work
./scripts/outlook-setup.sh --account personal
```

### Use specific account
```bash
./scripts/outlook-mail.sh --account work inbox
./scripts/outlook-calendar.sh --account personal today
./scripts/outlook-token.sh --account work refresh
```

### Or use environment variable
```bash
export OUTLOOK_ACCOUNT=work
./scripts/outlook-mail.sh inbox
```

### List configured accounts
```bash
./scripts/outlook-token.sh list
```

Credentials are stored separately:
```
~/.outlook-mcp/
  default/
    config.json
    credentials.json
  work/
    config.json  
    credentials.json
```

Existing single-account setups are auto-migrated to `default`.

## Usage

### Token Management
```bash
./scripts/outlook-token.sh refresh       # Refresh expired token
./scripts/outlook-token.sh test          # Test connection
./scripts/outlook-token.sh get --confirm # Print access token (requires confirmation)
```

### Reading Emails
```bash
./scripts/outlook-mail.sh inbox [count]           # List latest emails (default: 10)
./scripts/outlook-mail.sh unread [count]          # List unread emails
./scripts/outlook-mail.sh search "query" [count]  # Search emails (KQL syntax)
./scripts/outlook-mail.sh from <email> [count]    # List emails from sender
./scripts/outlook-mail.sh read <id>               # Read email content
./scripts/outlook-mail.sh attachments <id>        # List email attachments
```

### Advanced Queries
```bash
# Date range filters
./scripts/outlook-mail.sh query --after 2024-01-01 --before 2024-01-31

# Folder + unread filter
./scripts/outlook-mail.sh query --folder Inbox --unread --count 50

# Sender + attachments filter
./scripts/outlook-mail.sh query --from boss@work.com --has-attachments

# Combined filters
./scripts/outlook-mail.sh query --after 2024-06-01 --folder "Sent Items" --count 100
```

Query options:
- `--after DATE` — Emails received after date (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
- `--before DATE` — Emails received before date
- `--folder NAME` — Search in specific folder
- `--from EMAIL` — Filter by sender email
- `--unread` — Only unread emails
- `--has-attachments` — Only emails with attachments
- `--count N` — Maximum results (default: 20)

### Managing Emails
```bash
./scripts/outlook-mail.sh mark-read <id>          # Mark as read
./scripts/outlook-mail.sh mark-unread <id>        # Mark as unread
./scripts/outlook-mail.sh flag <id>               # Flag as important
./scripts/outlook-mail.sh unflag <id>             # Remove flag
./scripts/outlook-mail.sh delete <id>             # Move to trash
./scripts/outlook-mail.sh archive <id>            # Move to archive
./scripts/outlook-mail.sh move <id> <folder>      # Move to folder
```

### Sending Emails
```bash
./scripts/outlook-mail.sh send <to> <subj> <body> # Send new email
./scripts/outlook-mail.sh reply <id> "body"       # Reply to email
```

### Folders & Stats
```bash
./scripts/outlook-mail.sh folders                 # List mail folders
./scripts/outlook-mail.sh stats                   # Inbox statistics
```

## Calendar

### Viewing Events
```bash
./scripts/outlook-calendar.sh events [count]      # List upcoming events
./scripts/outlook-calendar.sh today               # Today's events
./scripts/outlook-calendar.sh week                # This week's events
./scripts/outlook-calendar.sh read <id>           # Event details
./scripts/outlook-calendar.sh calendars           # List all calendars
./scripts/outlook-calendar.sh free <start> <end>  # Check availability
```

### Creating Events
```bash
./scripts/outlook-calendar.sh create <subj> <start> <end> [location]  # Create event
./scripts/outlook-calendar.sh quick <subject> [time]                  # Quick 1-hour event
```

### Managing Events
```bash
./scripts/outlook-calendar.sh update <id> <field> <value>  # Update (subject/location/start/end)
./scripts/outlook-calendar.sh delete <id>                  # Delete event
```

Date format: `YYYY-MM-DDTHH:MM` (e.g., `2026-01-26T10:00`)

### Example Output

```bash
$ ./scripts/outlook-mail.sh inbox 3

{
  "n": 1,
  "subject": "Your weekly digest",
  "from": "digest@example.com",
  "date": "2026-01-25T15:44",
  "read": false,
  "id": "icYY6QAIUE26PgAAAA=="
}
{
  "n": 2,
  "subject": "Meeting reminder",
  "from": "calendar@outlook.com",
  "date": "2026-01-25T14:06",
  "read": true,
  "id": "icYY6QAIUE26PQAAAA=="
}

$ ./scripts/outlook-mail.sh read "icYY6QAIUE26PgAAAA=="

{
  "subject": "Your weekly digest",
  "from": { "name": "Digest", "address": "digest@example.com" },
  "to": ["you@hotmail.com"],
  "date": "2026-01-25T15:44:00Z",
  "body": "Here's what happened this week..."
}

$ ./scripts/outlook-mail.sh stats

{
  "folder": "Inbox",
  "total": 14098,
  "unread": 2955
}

$ ./scripts/outlook-calendar.sh today

{
  "n": 1,
  "subject": "Team standup",
  "start": "2026-01-25T10:00",
  "end": "2026-01-25T10:30",
  "location": "Teams",
  "id": "AAMkAGQ5NzE4YjQ3..."
}

$ ./scripts/outlook-calendar.sh create "Lunch with client" "2026-01-26T13:00" "2026-01-26T14:00" "Restaurant"

{
  "status": "event created",
  "subject": "Lunch with client",
  "start": "2026-01-26T13:00",
  "end": "2026-01-26T14:00",
  "id": "AAMkAGQ5NzE4YjQ3..."
}
```

## Token Refresh

Access tokens expire after ~1 hour. Refresh with:

```bash
./scripts/outlook-token.sh refresh
```

## Files

- `~/.outlook-mcp/config.json` - Client ID and secret
- `~/.outlook-mcp/credentials.json` - OAuth tokens (access + refresh)

## Permissions

- `Mail.ReadWrite` - Read and modify emails
- `Mail.Send` - Send emails
- `Calendars.ReadWrite` - Read and modify calendar events
- `offline_access` - Refresh tokens (stay logged in)
- `User.Read` - Basic profile info

## Notes

- **Email IDs**: The `id` field shows the last 20 characters of the full message ID. Use this ID with commands like `read`, `mark-read`, `delete`, etc.
- **Numbered results**: Emails are numbered (n: 1, 2, 3...) for easy reference in conversation.
- **Text extraction**: HTML email bodies are automatically converted to plain text.
- **Token expiry**: Access tokens expire after ~1 hour. Run `outlook-token.sh refresh` when you see auth errors.
- **Recent emails**: Commands like `read`, `mark-read`, etc. search the 100 most recent emails for the ID.

## Troubleshooting

**"Token expired"** → Run `outlook-token.sh refresh`

**"Invalid grant"** → Token invalid, re-run setup: `outlook-setup.sh`

**"Insufficient privileges"** → Check app permissions in Azure Portal → API Permissions

**"Message not found"** → The email may be older than 100 messages. Use search to find it first.

**"Folder not found"** → Use exact folder name. Run `folders` to see available folders.

## Supported Accounts

- Personal Microsoft accounts (outlook.com, hotmail.com, live.com)
- Work/School accounts (Microsoft 365) - may require admin consent

## Security Considerations

- **Azure App Registration**: The automated setup creates an App Registration in your Azure tenant with the following permissions: `Mail.ReadWrite`, `Mail.Send`, `Calendars.ReadWrite`, `offline_access`, `User.Read`
- **Local credential storage**: Client ID, client secret, and OAuth tokens are stored in `~/.outlook-mcp/` with `chmod 600`
- **Token printing**: `outlook-token.sh get --confirm` prints access tokens (requires explicit confirmation flag)
- **Prerequisites**: Requires [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) (`az`) and `jq`

If you prefer not to use automated setup, follow the manual configuration in `references/setup.md`.
