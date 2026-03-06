# Office 365 Multi-Account Guide

The Office 365 connector now supports multiple Microsoft 365 accounts! This lets you manage email, calendar, and contacts across different work identities from a single skill.

## Quick Start

### Import Your Existing Account

If you were already using the Office 365 connector, import your existing setup:

```bash
node accounts.js import-legacy
```

This creates a "primary" account with your existing authentication.

### Add a New Account

```bash
node accounts.js add <name> <tenant-id> <client-id> <client-secret> [email] [description]
```

**Example:**
```bash
node accounts.js add work \
  aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee \
  11111111-2222-3333-4444-555555555555 \
  "YourClientSecretHere~1234567890abcdefghijklmnopqrstuvwxyz" \
  matt@workandthrive.ai \
  "Work and Thrive account"
```

Each account needs its own Azure App Registration (same setup process as before).

### Authenticate Each Account

```bash
node auth.js login --account=work
```

Follow the device code flow to authenticate. The default account doesn't require `--account=`:

```bash
node auth.js login
```

## Account Management

### List All Accounts

```bash
node accounts.js list
```

Output:
```
📧 Office 365 Accounts:

primary [DEFAULT]
  Email: matt@example.com
  Description: Primary work account
  Added: 2/9/2026

work
  Email: matt@workandthrive.ai
  Description: Work and Thrive account
  Added: 2/9/2026
```

### Set Default Account

The default account is used when you don't specify `--account=`:

```bash
node accounts.js default work
```

### Remove an Account

```bash
node accounts.js remove <name>
```

This deletes the account configuration and authentication tokens.

## Using Multiple Accounts

All Office 365 commands now support `--account=<name>`:

### Email

```bash
# Read emails from default account
node email.js recent 10

# Read emails from specific account
node email.js recent 10 --account=work

# Search in specific account
node email.js search "project proposal" --account=primary

# Send from specific account
node send-email.js send to@example.com "Subject" "Body" --account=work
```

### Calendar

```bash
# Today's events (default account)
node calendar.js today

# Today's events (specific account)
node calendar.js today --account=work

# This week (specific account)
node calendar.js week --account=primary
```

### Authentication Status

```bash
# Check default account
node auth.js status

# Check specific account
node auth.js status --account=work
```

## Configuration Files

### Account Configuration
`~/.openclaw/auth/office365-accounts.json`

```json
{
  "default": "primary",
  "accounts": {
    "primary": {
      "tenantId": "e1a61901-e43e-4f6e-96d8-6888de2ceed0",
      "clientId": "72945084-85a2-4845-95f2-50131fc4e615",
      "clientSecret": "...",
      "email": "matt@example.com",
      "description": "Primary work account",
      "addedAt": "2026-02-09T16:00:00.000Z"
    },
    "work": {
      "tenantId": "...",
      "clientId": "...",
      "clientSecret": "...",
      "email": "matt@workandthrive.ai",
      "description": "Work and Thrive account",
      "addedAt": "2026-02-09T17:00:00.000Z"
    }
  }
}
```

### Token Storage
Each account has its own token file:
- `~/.openclaw/auth/office365/primary.json`
- `~/.openclaw/auth/office365/work.json`

Tokens are auto-refreshed when expired.

## Use Cases

### Multiple Work Identities

Perfect when you work across multiple organizations:

```bash
# Check calendar for consulting work
node calendar.js today --account=consulting

# Check emails for startup work
node email.js recent --account=startup

# Send from appropriate identity
node send-email.js send client@example.com "Update" "..." --account=consulting
```

### Personal + Work

Keep personal and work separate:

```bash
# Morning: Check work calendar
node calendar.js today --account=work

# Evening: Check personal email
node email.js recent --account=personal
```

### Delegate Access

Set up separate accounts for:
- Your own mailbox
- Shared mailboxes
- Delegated calendars

Each can be authenticated independently.

## Security

- **Client secrets** are stored in `~/.openclaw/auth/office365-accounts.json` with mode `0600` (owner read/write only)
- **Tokens** are stored in separate files per account with mode `0600`
- **Never commit** these files to version control
- **Rotate secrets** regularly (set calendar reminder for expiration)

## Azure App Registration

Each account needs its own Azure App Registration **OR** you can reuse the same app registration across accounts if they're in the same Azure AD tenant.

### Same Tenant, Multiple Accounts

If both accounts are in the same organization (same tenant ID), you can use the same Client ID and Client Secret for both.

### Different Tenants

If accounts are in different organizations, each needs its own Azure App Registration following the setup guide.

## Backward Compatibility

The skill automatically falls back to environment variables if no account is configured:

- `AZURE_TENANT_ID`
- `AZURE_CLIENT_ID`
- `AZURE_CLIENT_SECRET`

This means existing single-account setups continue working without changes.

## Troubleshooting

### "No account specified and no default account set"

```bash
# Set a default account
node accounts.js default primary

# Or always specify --account=
node calendar.js today --account=work
```

### "Account not found"

```bash
# List available accounts
node accounts.js list

# Add the missing account
node accounts.js add <name> ...
```

### Authentication expired

```bash
# Re-authenticate
node auth.js login --account=work
```

### Token refresh fails

```bash
# Check status
node auth.js status --account=work

# If expired, re-authenticate
node auth.js login --account=work
```

## Commands Reference

### Account Management
```bash
node accounts.js list                           # List all accounts
node accounts.js add <name> <tenant> <client> <secret> [email] [desc]
node accounts.js remove <name>                  # Remove account
node accounts.js default <name>                 # Set default
node accounts.js import-legacy                  # Import old setup
```

### Authentication
```bash
node auth.js login [--account=name]            # Authenticate
node auth.js status [--account=name]           # Check status
node auth.js token [--account=name]            # Get access token
```

### Email
```bash
node email.js recent [count] [--account=name]
node email.js search "query" [--account=name]
node email.js from email@domain [--account=name]
node email.js read <id> [--account=name]
```

### Calendar
```bash
node calendar.js today [--account=name]
node calendar.js week [--account=name]
```

### Send Mail
```bash
node send-email.js send <to> <subject> <body> [--account=name]
node send-email.js reply <message-id> <body> [--account=name]
```

### Cancel Event
```bash
node cancel-event.js <event-id> [comment] [--account=name]
```

---

## Next Steps

1. **Import or add your accounts**
2. **Authenticate each account**
3. **Set a default** for convenience
4. **Test with calendar/email commands**
5. **Update your scripts/workflows** to use `--account=` where needed

Need help? Check the main [SKILL.md](SKILL.md) and [Setup Guide](references/setup-guide.md).
