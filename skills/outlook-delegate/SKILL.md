---
name: outlook-delegate
description: Read, search, and manage Outlook emails and calendar via Microsoft Graph API with delegate support. Supports sending as self, as owner (Send As), and on behalf of owner (Send on Behalf). Modified for delegate access from https://clawhub.ai/jotamed/outlook
version: 1.1.0
author: 87marc
---

# Outlook Delegate Skill

Access another user's Outlook/Microsoft 365 email and calendar as a **delegate** via Microsoft Graph API. Supports three sending modes: as yourself, as the owner, or on behalf of the owner.

## Delegate Architecture

This skill is designed for scenarios where:
- **Your AI assistant** (the delegate) has its own Microsoft 365 account
- **The owner** has granted the assistant delegate access to their mailbox/calendar
- The assistant can send emails as itself, as the owner, or on behalf of the owner

### Sending Modes Explained

All three modes use the same Graph API call (`/users/{delegate}/sendMail` with the `from` field set). **The difference between Send As and Send on Behalf is determined entirely by which Exchange permission is granted**, not by the API endpoint.

| Mode | Command | Exchange Permission Required | `from` field | `sender` field | What Recipient Sees |
|------|---------|------------------------------|--------------|----------------|---------------------|
| As Self | `send` | (none extra) | Delegate | Delegate | "From: Assistant" |
| As Owner (Send As) | `send-as` | **SendAs only** | Owner | Owner | "From: Owner" |
| On Behalf Of | `send-behalf` | **SendOnBehalf only** | Owner | Delegate | "From: Assistant on behalf of Owner" |

> **⚠️ CRITICAL:** Do NOT grant both SendAs and SendOnBehalf permissions. If both are granted, Exchange always uses SendAs, and the "on behalf of" indication will never appear. Choose ONE based on your desired behavior.

### How It Works Under the Hood

When you call `send-as` or `send-behalf`, the skill makes the same API call: it sends via the delegate's endpoint with the owner in the `from` field. Microsoft Graph automatically sets the `sender` property to the authenticated user (the delegate). Whether the recipient sees "on behalf of" depends solely on the Exchange permission:

- **SendAs permission** → Graph sets both `sender` and `from` to the owner. No indication of delegation.
- **SendOnBehalf permission** → Graph keeps `sender` as the delegate and `from` as the owner. Recipient sees "on behalf of."

## Configuration

### Config File: `~/.outlook-mcp/config.json`

```json
{
  "client_id": "your-app-client-id",
  "client_secret": "your-app-client-secret",
  "tenant_id": "your-tenant-id",
  "owner_email": "owner@yourdomain.com",
  "owner_name": "Owner Display Name",
  "delegate_email": "assistant@yourdomain.com",
  "delegate_name": "AI Assistant",
  "timezone": "America/New_York"
}
```

| Field | Description |
|-------|-------------|
| `client_id` | Microsoft Entra ID App Registration client ID |
| `client_secret` | Microsoft Entra ID App Registration client secret |
| `tenant_id` | Your Microsoft Entra tenant ID (auto-detected during setup) |
| `owner_email` | The mailbox the assistant accesses as delegate |
| `owner_name` | Display name for the owner (used in From field) |
| `delegate_email` | The assistant's own email address |
| `delegate_name` | Display name for the assistant |
| `timezone` | IANA timezone for calendar operations (e.g., `America/New_York`, `Europe/London`, `UTC`) |

## Setup Requirements

### 1. Microsoft Entra ID App Registration

Create an app registration in Azure Portal:

1. Go to portal.azure.com → Microsoft Entra ID → App registrations
2. New registration:
   - Name: "AI Assistant Mail Access"
   - Supported account types: **"Accounts in this organizational directory only"** (single tenant)
   - Redirect URI: `http://localhost:8400/callback`
3. Note the **Application (client) ID** and **Directory (tenant) ID**

### 2. Configure API Permissions

In your app → API permissions → Add a permission → Microsoft Graph → Delegated permissions:

**Required for all modes:**
- `Mail.ReadWrite` — Read/write assistant's own mail
- `Mail.Send` — Send mail as assistant
- `Calendars.ReadWrite` — Read/write calendars
- `User.Read` — Read own profile
- `offline_access` — Refresh tokens

**Required for delegate access:**
- `Mail.ReadWrite.Shared` — Read/write shared mailboxes
- `Mail.Send.Shared` — Send on behalf of others
- `Calendars.ReadWrite.Shared` — Read/write shared calendars

Click **"Grant admin consent"** (requires admin).

### 3. Create Client Secret

1. Certificates & secrets → New client secret
2. Description: "AI Assistant"
3. Expiration: Choose appropriate duration
4. **Copy the Value immediately** (shown only once)

### 4. Grant Exchange Delegate Permissions

The owner (or an admin) must grant the assistant access via PowerShell.

**Choose your sending mode FIRST**, then grant the appropriate permissions:

```powershell
# Connect to Exchange Online
Install-Module -Name ExchangeOnlineManagement
Connect-ExchangeOnline -UserPrincipalName admin@yourdomain.com

# REQUIRED: Full Mailbox Access (for reading owner's mail)
Add-MailboxPermission -Identity "owner@yourdomain.com" `
    -User "assistant@yourdomain.com" `
    -AccessRights FullAccess `
    -InheritanceType All `
    -AutoMapping $false

# REQUIRED: Calendar Delegate Access
Add-MailboxFolderPermission -Identity "owner@yourdomain.com:\Calendar" `
    -User "assistant@yourdomain.com" `
    -AccessRights Editor `
    -SharingPermissionFlags Delegate
```

**Then choose ONE of the following — do NOT grant both:**

```powershell
# OPTION A: Send As (emails appear directly from owner, no indication)
Add-RecipientPermission -Identity "owner@yourdomain.com" `
    -Trustee "assistant@yourdomain.com" `
    -AccessRights SendAs `
    -Confirm:$false
```

```powershell
# OPTION B: Send on Behalf (emails show "assistant on behalf of owner")
Set-Mailbox -Identity "owner@yourdomain.com" `
    -GrantSendOnBehalfTo "assistant@yourdomain.com"
```

**Verify permissions:**
```powershell
# Check mailbox permissions
Get-MailboxPermission -Identity "owner@yourdomain.com" | Where-Object {$_.User -like "*assistant*"}

# Check Send As
Get-RecipientPermission -Identity "owner@yourdomain.com" | Where-Object {$_.Trustee -like "*assistant*"}

# Check Send on Behalf
Get-Mailbox "owner@yourdomain.com" | Select-Object GrantSendOnBehalfTo

# Check Calendar permissions
Get-MailboxFolderPermission -Identity "owner@yourdomain.com:\Calendar"
```

### 5. Permissions Summary

| Action | Graph Permission | Exchange Permission |
|--------|-----------------|---------------------|
| Read owner's mail | `Mail.ReadWrite.Shared` | FullAccess |
| Send as self | `Mail.Send` | (none needed) |
| Send as owner | `Mail.Send.Shared` | SendAs **only** |
| Send on behalf of owner | `Mail.Send.Shared` | SendOnBehalf **only** |
| Read/write owner's calendar | `Calendars.ReadWrite.Shared` | Editor |

## Usage

### Token Management
```bash
./scripts/outlook-token.sh refresh   # Refresh expired token
./scripts/outlook-token.sh test      # Test connection to both accounts
./scripts/outlook-token.sh get       # Print access token
./scripts/outlook-token.sh info      # Show configuration info
```

### Reading Owner's Emails
```bash
./scripts/outlook-mail.sh inbox [count]           # Owner's inbox
./scripts/outlook-mail.sh unread [count]          # Owner's unread
./scripts/outlook-mail.sh search "query" [count]  # Search owner's mail
./scripts/outlook-mail.sh from <email> [count]    # Owner's mail from sender
./scripts/outlook-mail.sh read <id>               # Read email content
./scripts/outlook-mail.sh attachments <id>        # List attachments
```

### Managing Owner's Emails
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

**As Assistant (self):**
```bash
./scripts/outlook-mail.sh send <to> <subject> <body>
./scripts/outlook-mail.sh reply <id> "body"
./scripts/outlook-mail.sh forward <id> <to> [message]
```
Recipient sees: **"From: AI Assistant <assistant@domain.com>"**

**As Owner (Send As — requires SendAs permission, no indication):**
```bash
./scripts/outlook-mail.sh send-as <to> <subject> <body>
./scripts/outlook-mail.sh reply-as <id> "body"
./scripts/outlook-mail.sh forward-as <id> <to> [message]
```
Recipient sees: **"From: Owner <owner@domain.com>"**

**On Behalf of Owner (requires SendOnBehalf permission):**
```bash
./scripts/outlook-mail.sh send-behalf <to> <subject> <body>
./scripts/outlook-mail.sh reply-behalf <id> "body"
./scripts/outlook-mail.sh forward-behalf <id> <to> [message]
```
Recipient sees: **"From: AI Assistant on behalf of Owner <owner@domain.com>"**

### Drafts
```bash
./scripts/outlook-mail.sh draft <to> <subject> <body>  # Create draft in owner's mailbox
./scripts/outlook-mail.sh drafts [count]               # List owner's drafts
./scripts/outlook-mail.sh send-draft <id>              # Send draft as self
./scripts/outlook-mail.sh send-draft-as <id>           # Send draft as owner
./scripts/outlook-mail.sh send-draft-behalf <id>       # Send draft on behalf of owner
```

### Folders & Stats
```bash
./scripts/outlook-mail.sh folders                 # List mail folders
./scripts/outlook-mail.sh stats                   # Inbox statistics
./scripts/outlook-mail.sh whoami                  # Show delegate info
```

### Calendar

**Viewing Events:**
```bash
./scripts/outlook-calendar.sh events [count]      # Owner's upcoming events (future only)
./scripts/outlook-calendar.sh today               # Today's events (timezone-aware)
./scripts/outlook-calendar.sh week                # This week's events
./scripts/outlook-calendar.sh read <id>           # Event details
./scripts/outlook-calendar.sh calendars           # List all calendars
./scripts/outlook-calendar.sh free <start> <end>  # Check availability
```

**Creating Events:**
```bash
./scripts/outlook-calendar.sh create <subject> <start> <end> [location]
./scripts/outlook-calendar.sh quick <subject> [time]
```
Date format: `YYYY-MM-DDTHH:MM` (e.g., `2026-01-26T10:00`)

**Managing Events:**
```bash
./scripts/outlook-calendar.sh update <id> <field> <value>
./scripts/outlook-calendar.sh delete <id>
```
Fields: `subject`, `location`, `start`, `end`

## Sent Items Behavior

Where the sent copy is saved depends on the endpoint used, not the sending mode:

| Command | Endpoint Used | Saved To |
|---------|--------------|----------|
| `send` (as self) | `/users/{delegate}/sendMail` | Delegate's Sent Items |
| `send-as` | `/users/{delegate}/sendMail` | Delegate's Sent Items * |
| `send-behalf` | `/users/{delegate}/sendMail` | Delegate's Sent Items * |
| All draft sends | `/users/{owner}/messages/{id}/send` | Owner's Sent Items |

\* Administrators can configure Exchange to also save a copy in the owner's Sent Items using:
```powershell
Set-Mailbox -Identity "owner@yourdomain.com" -MessageCopyForSentAsEnabled $true -MessageCopyForSendOnBehalfEnabled $true
```

## Troubleshooting

**"Access denied" or "403 Forbidden"**
→ Check that the assistant has MailboxPermission on the owner's mailbox

**"ErrorSendAsDenied"**
→ Missing SendAs or SendOnBehalf permission. Run the PowerShell commands above.

**Emails don't show "on behalf of"**
→ You may have both SendAs and SendOnBehalf granted. When both exist, Exchange always uses SendAs (which hides the delegate). Remove the SendAs permission if you want "on behalf of" to appear.

**"The mailbox is not found"**
→ Verify `owner_email` in config.json is correct

**"AADSTS90002: Tenant not found"**
→ Check `tenant_id` in config.json matches your Microsoft Entra tenant

**"Token expired"**
→ Run `outlook-token.sh refresh`

**Wrong timezone for calendar**
→ Update `timezone` in config.json (use IANA format like `America/New_York`)

## Security Considerations

1. **Credential Protection**: The `~/.outlook-mcp/` directory is automatically set to `700` and credential files to `600`
2. **No Process Leaks**: Token refresh and exchange operations pass secrets via stdin, not command-line arguments
3. **Input Sanitization**: All user input is JSON-escaped via `jq` to prevent injection
4. **Audit Trail**: All actions are logged in the owner's mailbox audit log
5. **Scope Limitation**: The assistant only has access to what's explicitly granted
6. **Revocation**: Owner can revoke access via Exchange PowerShell or Outlook settings

## Revoking Access

```powershell
# Remove all permissions
Remove-MailboxPermission -Identity "owner@yourdomain.com" -User "assistant@yourdomain.com" -AccessRights FullAccess -Confirm:$false

# Remove Send As (if granted)
Remove-RecipientPermission -Identity "owner@yourdomain.com" -Trustee "assistant@yourdomain.com" -AccessRights SendAs -Confirm:$false

# Remove Send on Behalf (if granted)
Set-Mailbox -Identity "owner@yourdomain.com" -GrantSendOnBehalfTo @{Remove="assistant@yourdomain.com"}

# Remove Calendar access
Remove-MailboxFolderPermission -Identity "owner@yourdomain.com:\Calendar" -User "assistant@yourdomain.com" -Confirm:$false
```

## Files

- `~/.outlook-mcp/config.json` — Configuration (client ID, tenant ID, emails, timezone)
- `~/.outlook-mcp/credentials.json` — OAuth tokens (access + refresh)

## Changelog

### v1.1.0
- **FIXED**: Reply command no longer sends duplicate emails (removed dead code that sent a garbage email)
- **FIXED**: All reply/forward variants now use proper Graph API threading (createReply/createForward → patch from → send)
- **FIXED**: send-as and send-behalf now correctly documented — behavior depends on Exchange permissions, not API endpoint
- **FIXED**: send-draft-behalf no longer deletes draft before sending (prevents data loss on send failure)
- **FIXED**: All user input is now JSON-escaped via `jq` to prevent injection and malformed payloads
- **FIXED**: Credentials file permissions enforced on every write (`chmod 600`)
- **FIXED**: Config directory permissions enforced (`chmod 700`)
- **FIXED**: Client secrets no longer visible in process list (sent via stdin)
- **FIXED**: Calendar `events` command now shows only future events
- **FIXED**: Sent Items behavior documented accurately
- **FIXED**: Version number corrected
- Updated Microsoft Entra ID naming (formerly Azure Active Directory)
- Setup guide now explicitly warns against granting both SendAs and SendOnBehalf
- Revocation commands updated (GrantSendOnBehalfTo uses @{Remove=...} syntax)

### v1.0.0
- Three sending modes: as self, as owner (Send As), on behalf of owner
- Tenant-specific authentication (no `/common` endpoint)
- Configurable timezone for calendar operations
- Display names for owner and delegate
- Drafts saved to owner's mailbox
- Comprehensive PowerShell setup commands
- Based on outlook v1.3.0 by jotamed (https://clawhub.ai/jotamed/outlook)
