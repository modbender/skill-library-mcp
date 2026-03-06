# Delegate Setup Guide

Complete guide for setting up your AI assistant as a delegate for the owner's Microsoft 365 mailbox and calendar.

## Overview

**Architecture:**
- Your AI assistant has its own M365 account (the delegate)
- The owner grants the assistant access to their mailbox/calendar
- The assistant can send emails three ways:
  1. **As itself** — emails come from the assistant
  2. **As owner (Send As)** — emails appear to come directly from owner
  3. **On behalf of owner** — emails show "Assistant on behalf of Owner"

> **⚠️ Important:** Modes 2 and 3 are mutually exclusive at the Exchange level. You must grant only ONE of SendAs or SendOnBehalf. If both are granted, Exchange always uses SendAs and the "on behalf of" indication will never appear.

## Step 1: Create the Assistant's M365 Account

If not already done, create a user account for the assistant in your Microsoft 365 admin center (admin.microsoft.com).

## Step 2: Microsoft Entra ID App Registration

### Create the App

1. Go to **portal.azure.com** → **Microsoft Entra ID** → **App registrations**
2. Click **New registration**
3. Configure:
   - **Name**: "AI Assistant Mail Access" (or your preferred name)
   - **Supported account types**: Select **"Accounts in this organizational directory only"** (single tenant)
   - **Redirect URI**: Platform = Web, URI = `http://localhost:8400/callback`
4. Click **Register**
5. Note these values from the Overview page:
   - **Application (client) ID** → This is your `client_id`
   - **Directory (tenant) ID** → This is your `tenant_id`

### Configure API Permissions

1. In your app → **API permissions** → **Add a permission**
2. Select **Microsoft Graph** → **Delegated permissions**
3. Add these permissions:

**Basic permissions:**
- `Mail.ReadWrite` — Read/write assistant's mail
- `Mail.Send` — Send as assistant
- `Calendars.ReadWrite` — Calendar access
- `User.Read` — Read profile
- `offline_access` — Refresh tokens

**Delegate permissions:**
- `Mail.ReadWrite.Shared` — Read/write owner's mail
- `Mail.Send.Shared` — Send as/on behalf of owner
- `Calendars.ReadWrite.Shared` — Owner's calendar

4. Click **Grant admin consent for [Your Org]** (requires admin)

### Create Client Secret

1. Go to **Certificates & secrets** → **New client secret**
2. Description: "AI Assistant"
3. Expiration: Choose based on your security policy
4. Click **Add**
5. **IMPORTANT**: Copy the **Value** immediately — it's only shown once!

## Step 3: Grant Exchange Delegate Permissions

Connect to Exchange Online PowerShell and grant permissions:

```powershell
# Install the module (first time only)
Install-Module -Name ExchangeOnlineManagement -Force

# Connect to Exchange Online
Connect-ExchangeOnline -UserPrincipalName admin@yourdomain.com
```

### Grant Core Permissions (Required)

```powershell
# Variables - update these
$Owner = "owner@yourdomain.com"
$Assistant = "assistant@yourdomain.com"

# 1. Full Mailbox Access (read/manage owner's mail)
Add-MailboxPermission -Identity $Owner `
    -User $Assistant `
    -AccessRights FullAccess `
    -InheritanceType All `
    -AutoMapping $false

# 2. Calendar Delegate Access
Add-MailboxFolderPermission -Identity "${Owner}:\Calendar" `
    -User $Assistant `
    -AccessRights Editor `
    -SharingPermissionFlags Delegate
```

### Choose Your Sending Mode (Pick ONE)

> **⚠️ Do NOT grant both.** If both SendAs and SendOnBehalf are active, Exchange always uses SendAs and the "on behalf of" indication will never appear.

**Option A: Send As (emails look like they came directly from the owner)**
```powershell
Add-RecipientPermission -Identity $Owner `
    -Trustee $Assistant `
    -AccessRights SendAs `
    -Confirm:$false
```
Use the `send-as`, `reply-as`, `forward-as` commands.

**Option B: Send on Behalf (emails show "assistant on behalf of owner")**
```powershell
Set-Mailbox -Identity $Owner `
    -GrantSendOnBehalfTo @{Add=$Assistant}
```
Use the `send-behalf`, `reply-behalf`, `forward-behalf` commands.

### Verify Permissions

```powershell
# Check mailbox access
Get-MailboxPermission -Identity $Owner | `
    Where-Object {$_.User -like "*$Assistant*"} | `
    Format-Table User, AccessRights

# Check Send As
Get-RecipientPermission -Identity $Owner | `
    Where-Object {$_.Trustee -like "*$Assistant*"} | `
    Format-Table Trustee, AccessRights

# Check Send on Behalf
Get-Mailbox $Owner | Select-Object GrantSendOnBehalfTo

# Check Calendar
Get-MailboxFolderPermission -Identity "${Owner}:\Calendar" | `
    Where-Object {$_.User -like "*$Assistant*"}
```

## Step 4: Configure the Skill

Create the config directory:
```bash
mkdir -p ~/.outlook-mcp
chmod 700 ~/.outlook-mcp
```

Create `~/.outlook-mcp/config.json`:
```json
{
  "client_id": "YOUR-APPLICATION-CLIENT-ID",
  "client_secret": "YOUR-CLIENT-SECRET-VALUE",
  "tenant_id": "YOUR-DIRECTORY-TENANT-ID",
  "owner_email": "owner@yourdomain.com",
  "owner_name": "Owner Full Name",
  "delegate_email": "assistant@yourdomain.com",
  "delegate_name": "AI Assistant",
  "timezone": "America/New_York"
}
```

Secure the config file:
```bash
chmod 600 ~/.outlook-mcp/config.json
```

### Timezone Reference

Use IANA timezone format. Common values:
- `America/New_York` — US Eastern
- `America/Chicago` — US Central
- `America/Denver` — US Mountain
- `America/Los_Angeles` — US Pacific
- `Europe/London` — UK
- `Europe/Paris` — Central Europe
- `Asia/Tokyo` — Japan
- `Australia/Sydney` — Australia Eastern
- `UTC` — Coordinated Universal Time

Full list: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

## Step 5: Authorize the Assistant

Run the OAuth flow. The assistant signs in as itself:

```bash
# Load config
CLIENT_ID=$(jq -r '.client_id' ~/.outlook-mcp/config.json)
TENANT_ID=$(jq -r '.tenant_id' ~/.outlook-mcp/config.json)
REDIRECT="http://localhost:8400/callback"
SCOPE="offline_access%20User.Read%20Mail.ReadWrite%20Mail.Send%20Mail.ReadWrite.Shared%20Mail.Send.Shared%20Calendars.ReadWrite%20Calendars.ReadWrite.Shared"

# Generate auth URL (tenant-specific, not /common)
echo "Open this URL in a browser and sign in as the ASSISTANT account:"
echo ""
echo "https://login.microsoftonline.com/$TENANT_ID/oauth2/v2.0/authorize?client_id=$CLIENT_ID&response_type=code&redirect_uri=$REDIRECT&scope=$SCOPE"
```

After signing in:
1. You'll be redirected to `http://localhost:8400/callback?code=XXXXXX...`
2. Copy the `code` parameter value from the URL

Exchange the code for tokens:
```bash
CODE="paste-the-code-here"
CLIENT_SECRET=$(jq -r '.client_secret' ~/.outlook-mcp/config.json)

# Use stdin to avoid exposing secrets in process list
printf 'client_id=%s&client_secret=%s&code=%s&redirect_uri=%s&grant_type=authorization_code&scope=%s' \
  "$CLIENT_ID" "$CLIENT_SECRET" "$CODE" "$REDIRECT" "$SCOPE" | \
  curl -s -X POST "https://login.microsoftonline.com/$TENANT_ID/oauth2/v2.0/token" \
  --data @- > ~/.outlook-mcp/credentials.json

chmod 600 ~/.outlook-mcp/credentials.json

# Verify
cat ~/.outlook-mcp/credentials.json | jq '{status: "authorized", expires_in, scope}'
```

## Step 6: Test Access

```bash
./scripts/outlook-token.sh test
```

Expected output:
```
Testing delegate access...

1. Delegate identity (who is authenticated):
{
  "authenticated_as": "assistant@yourdomain.com",
  "display_name": "AI Assistant"
}

2. Owner mailbox access (owner@yourdomain.com):
{
  "status": "OK",
  "folder": "Inbox",
  "unread": 15,
  "total": 1234
}

3. Owner calendar access (owner@yourdomain.com):
{
  "status": "OK",
  "calendar": "Calendar",
  "canEdit": true
}

4. Timezone configured: America/New_York
```

## Troubleshooting

### "AADSTS90002: Tenant 'xxx' not found"

Your `tenant_id` is incorrect. Find the correct value:
1. Azure Portal → Microsoft Entra ID → Overview
2. Copy the "Tenant ID" value

### "AADSTS700016: Application not found"

The `client_id` is incorrect or the app was deleted.

### "AADSTS7000215: Invalid client secret"

The `client_secret` is wrong or expired. Create a new secret in Azure Portal.

### "ErrorAccessDenied" when reading owner's mail

The assistant doesn't have FullAccess permission:
```powershell
Add-MailboxPermission -Identity "owner@yourdomain.com" -User "assistant@yourdomain.com" -AccessRights FullAccess
```

### "ErrorSendAsDenied" with send-as command

Missing SendAs permission:
```powershell
Add-RecipientPermission -Identity "owner@yourdomain.com" -Trustee "assistant@yourdomain.com" -AccessRights SendAs
```

### "ErrorSendAsDenied" with send-behalf command

Missing SendOnBehalf permission:
```powershell
Set-Mailbox -Identity "owner@yourdomain.com" -GrantSendOnBehalfTo @{Add="assistant@yourdomain.com"}
```

### Emails sent with send-behalf don't show "on behalf of"

You have both SendAs and SendOnBehalf granted. When both exist, Exchange always uses SendAs (which hides the delegate). Fix by removing the SendAs permission:
```powershell
Remove-RecipientPermission -Identity "owner@yourdomain.com" -Trustee "assistant@yourdomain.com" -AccessRights SendAs -Confirm:$false
```

### Calendar shows wrong times

Update `timezone` in config.json to match your local timezone.

### "invalid_grant" when refreshing token

The refresh token is invalid. Re-run the authorization flow (Step 5).

## Security Best Practices

1. **Protect credentials**: The scripts automatically enforce secure permissions:
   ```bash
   # These are set automatically, but verify:
   ls -la ~/.outlook-mcp/
   # Should show: drwx------ (700) for directory
   # Should show: -rw------- (600) for all .json files
   ```

2. **Use short-lived secrets**: Set client secret expiration to 6-12 months

3. **Monitor audit logs**: Check owner's mailbox audit log for unusual activity

4. **Principle of least privilege**: Only grant the permissions actually needed — especially choose ONE of SendAs or SendOnBehalf, not both

5. **Regular review**: Periodically verify delegate permissions are still appropriate

## Revoking Access

To completely remove the assistant's access:

```powershell
$Owner = "owner@yourdomain.com"
$Assistant = "assistant@yourdomain.com"

# Remove mailbox access
Remove-MailboxPermission -Identity $Owner -User $Assistant -AccessRights FullAccess -Confirm:$false

# Remove Send As (if granted)
Remove-RecipientPermission -Identity $Owner -Trustee $Assistant -AccessRights SendAs -Confirm:$false

# Remove Send on Behalf (if granted)
Set-Mailbox -Identity $Owner -GrantSendOnBehalfTo @{Remove=$Assistant}

# Remove Calendar access
Remove-MailboxFolderPermission -Identity "${Owner}:\Calendar" -User $Assistant -Confirm:$false
```

Also delete the local credentials:
```bash
rm -rf ~/.outlook-mcp/
```

And optionally delete the Microsoft Entra ID app registration in the portal.
