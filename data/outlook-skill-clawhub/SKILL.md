---
name: outlook-delegate
description: Read, search, and manage Outlook emails and calendar via Microsoft Graph API with delegate support. Your AI assistant authenticates as itself but accesses the owner's mailbox/calendar as a delegate. Modified for delegate access from https://clawhub.ai/jotamed/outlook
version: 1.0.0
author: 87marc
---

# Outlook Delegate Skill

Access another user's Outlook/Microsoft 365 email and calendar as a **delegate** via Microsoft Graph API.

## Delegate Architecture

This skill is designed for scenarios where:
- **Your AI assistant** has its own Microsoft 365 account (e.g., `assistant@domain.com`)
- **The owner** has granted the assistant delegate access to their mailbox/calendar
- The assistant authenticates as itself but accesses the owner's resources

### What Changed from Direct Access

| Feature | Direct Access (`/me`) | Delegate Access (`/users/{id}`) |
|---------|----------------------|--------------------------------|
| API Base | `/me/messages` | `/users/{owner}/messages` |
| Send Email | Appears "From: Owner" | Appears "From: Assistant on behalf of Owner" |
| Calendar | Full control | Based on permission level granted |
| Permissions | Mail.ReadWrite, Mail.Send | Mail.ReadWrite.Shared, Mail.Send.Shared, Calendars.ReadWrite.Shared |

## Configuration

### Config File: `~/.outlook-mcp/config.json`

```json
{
  "client_id": "your-app-client-id",
  "client_secret": "your-app-client-secret",
  "owner_email": "owner@domain.com",
  "delegate_email": "assistant@domain.com"
}
```

The `owner_email` is the mailbox the assistant will access as a delegate.

## Setup Requirements

### 1. Azure AD App Registration

The app registration needs **delegated permissions** (not application permissions):

- `Mail.ReadWrite.Shared` - Read/write access to shared mailboxes
- `Mail.Send.Shared` - Send mail on behalf of others
- `Calendars.ReadWrite.Shared` - Read/write shared calendars
- `User.Read` - Read assistant's own profile
- `offline_access` - Refresh tokens

### 2. Exchange Delegate Permissions (Admin or Owner)

The owner must grant the assistant delegate access via Exchange/Outlook:

**PowerShell (Admin):**
```powershell
# Grant mailbox access
Add-MailboxPermission -Identity "owner@domain.com" -User "assistant@domain.com" -AccessRights FullAccess

# Grant Send-on-Behalf
Set-Mailbox -Identity "owner@domain.com" -GrantSendOnBehalfTo "assistant@domain.com"

# Grant calendar access (Editor = can create/modify events)
Add-MailboxFolderPermission -Identity "owner@domain.com:\Calendar" -User "assistant@domain.com" -AccessRights Editor -SharingPermissionFlags Delegate
```

**Or via Outlook Settings:**
The owner can add the assistant as a delegate in Outlook → File → Account Settings → Delegate Access.

### 3. Token Flow

The assistant authenticates as itself via OAuth2, then accesses the owner's resources using the `/users/{owner@domain.com}/` endpoint.

## Usage

### Token Management
```bash
./scripts/outlook-token.sh refresh   # Refresh expired token
./scripts/outlook-token.sh test      # Test connection to BOTH accounts
./scripts/outlook-token.sh get       # Print access token
```

### Reading Owner's Emails
```bash
./scripts/outlook-mail.sh inbox [count]           # Owner's inbox
./scripts/outlook-mail.sh unread [count]          # Owner's unread
./scripts/outlook-mail.sh search "query" [count]  # Search owner's mail
./scripts/outlook-mail.sh from <email> [count]    # Owner's mail from sender
./scripts/outlook-mail.sh read <id>               # Read email content
```

### Managing Owner's Emails
```bash
./scripts/outlook-mail.sh mark-read <id>          # Mark as read
./scripts/outlook-mail.sh mark-unread <id>        # Mark as unread
./scripts/outlook-mail.sh flag <id>               # Flag as important
./scripts/outlook-mail.sh delete <id>             # Move to trash
./scripts/outlook-mail.sh archive <id>            # Move to archive
./scripts/outlook-mail.sh move <id> <folder>      # Move to folder
```

### Sending Emails (On Behalf Of Owner)
```bash
./scripts/outlook-mail.sh send <to> <subj> <body>  # Send on behalf of owner
./scripts/outlook-mail.sh reply <id> "body"        # Reply on behalf of owner
```

**Note:** Emails will show "Assistant on behalf of Owner" in the From field.

### Owner's Calendar
```bash
./scripts/outlook-calendar.sh events [count]      # Owner's upcoming events
./scripts/outlook-calendar.sh today               # Owner's today
./scripts/outlook-calendar.sh week                # Owner's week
./scripts/outlook-calendar.sh read <id>           # Event details
./scripts/outlook-calendar.sh free <start> <end>  # Owner's availability
```

### Creating Events on Owner's Calendar
```bash
./scripts/outlook-calendar.sh create <subj> <start> <end> [location]
./scripts/outlook-calendar.sh quick <subject> [time]
```

## API Endpoint Changes

The key change is replacing `/me` with `/users/{owner_email}`:

```bash
# Direct access (old)
API="https://graph.microsoft.com/v1.0/me"

# Delegate access (new)
OWNER=$(jq -r '.owner_email' "$CONFIG_FILE")
API="https://graph.microsoft.com/v1.0/users/$OWNER"
```

## Send-on-Behalf Implementation

When sending mail as a delegate, you must specify the `from` address:

```json
{
  "message": {
    "subject": "Meeting follow-up",
    "from": {
      "emailAddress": {
        "address": "owner@domain.com"
      }
    },
    "toRecipients": [{"emailAddress": {"address": "recipient@example.com"}}],
    "body": {"contentType": "Text", "content": "..."}
  }
}
```

The recipient sees: **"Assistant on behalf of Owner <owner@domain.com>"**

## Permissions Summary

| Action | Required Permission | Exchange Setting |
|--------|-------------------|-----------------|
| Read owner's mail | Mail.ReadWrite.Shared | FullAccess or Reviewer |
| Modify owner's mail | Mail.ReadWrite.Shared | FullAccess or Editor |
| Send as owner | Mail.Send.Shared | SendOnBehalf |
| Read owner's calendar | Calendars.ReadWrite.Shared | Reviewer+ |
| Create events on owner's calendar | Calendars.ReadWrite.Shared | Editor |

## Troubleshooting

**"Access denied" or "403 Forbidden"**
→ Check that the assistant has MailboxPermission on the owner's mailbox

**"The mailbox is not found"**
→ Verify `owner_email` in config.json is correct

**"Insufficient privileges"**
→ App registration missing `.Shared` permissions (check Azure AD)

**Emails send but don't show "on behalf of"**
→ Missing SendOnBehalf permission. Run:
```powershell
Set-Mailbox -Identity "owner@domain.com" -GrantSendOnBehalfTo "assistant@domain.com"
```

**"Token expired"**
→ Run `outlook-token.sh refresh`

## Security Considerations

1. **Audit Trail**: All actions by the assistant are logged in the owner's mailbox audit log
2. **Token Storage**: Credentials stored in `~/.outlook-mcp/` - protect this directory
3. **Scope Limitation**: The assistant only has access to what the owner explicitly grants
4. **Revocation**: The owner can revoke access anytime via Delegate settings

## Files

- `~/.outlook-mcp/config.json` - Client ID, secret, and owner/delegate emails
- `~/.outlook-mcp/credentials.json` - OAuth tokens (access + refresh)

## Changelog

### v1.0.0 (Delegate Edition)
- **Breaking**: API calls now use `/users/{owner}` instead of `/me`
- Added: `owner_email` and `delegate_email` config fields
- Added: Send-on-behalf support with proper `from` field
- Changed: Permissions to `.Shared` variants
- Added: Delegate setup documentation
- Added: Token test validates access to owner's mailbox
- Based on outlook v1.3.0 by jotamed (https://clawhub.ai/jotamed/outlook)
