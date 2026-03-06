---
name: email-migration-toolkit
description: "Universal email migration toolkit for any provider to any provider. Use when migrating between Yahoo, Zoho, ProtonMail, iCloud, on-premises Exchange, or any IMAP-capable email service. Covers decision trees, backup/export procedures, IMAP connectivity testing, troubleshooting, and provider-specific configurations. Essential for IT professionals handling diverse email migrations beyond Google/Microsoft ecosystems."
---

# Universal Email Migration Toolkit

## Migration Decision Tree

Use this matrix to determine the best migration path:

| Source | Destination | Method | Complexity | Notes |
|--------|-------------|--------|-----------|-------|
| Yahoo Mail | Gmail | IMAP → Gmail Import | Easy | Use app passwords |
| Yahoo Mail | Outlook | IMAP → Outlook Desktop | Medium | Manual folder setup |
| Zoho Mail | Gmail | IMAP → Gmail Import | Easy | Supports IMAP natively |
| Zoho Mail | Outlook | Microsoft Migration | Medium | Use Zoho IMAP settings |
| ProtonMail | Gmail | Export → Import | Hard | Limited export options |
| ProtonMail | Outlook | Manual forwarding | Hard | No bulk export |
| iCloud Mail | Gmail | IMAP → Gmail Import | Easy | Requires app password |
| iCloud Mail | Outlook | IMAP → Outlook | Medium | Limited folder support |
| Any IMAP | Any IMAP | IMAP bridging | Medium | Universal solution |
| Exchange On-prem | Cloud | PST export/import | Hard | Requires Exchange admin |

## Universal IMAP Migration Process

For most provider-to-provider migrations:

### Step 1: Source Preparation
1. **Enable IMAP** on source account (if not enabled by default)
2. **Create app password** (Gmail, Yahoo, iCloud require this)
3. **Test connectivity** using the IMAP test script
4. **Estimate data size** using the mailbox size script
5. **Document folder structure** for mapping reference

### Step 2: Destination Setup
1. **Create target account** with sufficient storage
2. **Enable IMAP access** (for intermediary tools)
3. **Configure mail client** (Outlook, Thunderbird, or web import)
4. **Set up folder structure** matching source (if needed)
5. **Test inbound mail** to verify account is working

### Step 3: Migration Execution
Choose based on destination platform:

#### To Gmail (any source with IMAP)
1. Gmail → Settings → Accounts → Import mail and contacts
2. Enter source IMAP details from provider matrix
3. Choose import options (last 30 days vs. all mail)
4. Start import — Gmail handles the rest automatically

#### To Outlook/Microsoft 365
1. Outlook Desktop → Add Account → IMAP source
2. Set up both accounts in same Outlook profile
3. Drag and drop folders from source to destination
4. Alternative: Use Microsoft's import tools for bulk

#### IMAP-to-IMAP (Universal)
1. Use desktop client (Outlook, Thunderbird, Apple Mail)
2. Configure both accounts as IMAP
3. Copy folders between accounts via client
4. Monitor for errors and retry failed items

### Step 4: Validation
1. **Compare email counts** between source and destination
2. **Test key functionality** (send, receive, search)
3. **Verify contacts and calendar** if migrated
4. **Check folder structure** matches expectations
5. **Validate largest messages** and attachments

## Email Backup and Export

Before any migration, create backups:

### Source-Specific Export Methods

#### Gmail / Google Workspace
- **Method**: Google Takeout (takeout.google.com)
- **Format**: MBOX (Thunderbird compatible)
- **Includes**: Email, contacts, calendar
- **Time**: 2-48 hours depending on mailbox size

#### Outlook / Exchange
- **Method**: Export to PST file
- **Format**: PST (Outlook native)
- **Process**: File → Open & Export → Export to File
- **Limitation**: Desktop Outlook required

#### Yahoo Mail
- **Method**: IMAP download via email client
- **Format**: Various (depends on client)
- **Process**: Configure IMAP, sync all folders locally
- **Note**: No bulk export tool from Yahoo

#### Zoho Mail
- **Method**: IMAP export or Zoho's backup tool
- **Format**: MBOX or EML
- **Process**: Contact Zoho support for large mailboxes
- **Alternative**: IMAP sync to local client

#### iCloud Mail
- **Method**: IMAP download
- **Format**: Various (client dependent)
- **Process**: Configure IMAP with app password
- **Limitation**: No native export tool

#### ProtonMail
- **Method**: Individual email export only
- **Format**: EML files
- **Process**: Select emails individually, export
- **Note**: No bulk export due to encryption

See `references/backup-export.md` for detailed step-by-step procedures.

## Common Migration Challenges

| Challenge | Solution | Prevention |
|-----------|----------|------------|
| Authentication failures | Use app passwords, check 2FA settings | Test connectivity first |
| Size limitations | Split into batches, exclude large attachments | Check provider limits |
| Folder mapping issues | Document structure, plan manual creation | Map folders before migration |
| Missing emails | Check spam/junk, verify date ranges | Do incremental migration |
| Slow transfer speeds | Use multiple connections, off-peak hours | Plan adequate time |
| Character encoding | Ensure UTF-8 support in tools | Test with non-ASCII subjects |

## Provider-Specific Considerations

### Yahoo Mail
- **IMAP Limitations**: Free accounts have folder limits
- **Authentication**: Must use app passwords with 2FA
- **Best Practice**: Migrate during off-peak hours (night/weekend)

### Zoho Mail
- **IMAP Support**: Full IMAP access on all plans
- **Bulk Migration**: Zoho offers migration services for enterprise
- **API Access**: Available for custom migration tools

### ProtonMail
- **Major Limitation**: No IMAP access due to encryption
- **Workaround**: Export to Thunderbird, then migrate from Thunderbird
- **Enterprise**: ProtonMail Bridge available for paid plans

### iCloud Mail
- **Storage Limits**: 5GB free, consider upgrading temporarily
- **IMAP Quirks**: Some folders may not sync properly
- **Performance**: Slow IMAP response, plan extra time

### On-Premises Exchange
- **Admin Access**: Required for PST export/import
- **Network**: Consider bandwidth limitations
- **Legacy Versions**: Older Exchange may need PST conversion

## Troubleshooting Workflow

When migration fails or stalls:

1. **Check authentication** — Re-enter passwords, regenerate app passwords
2. **Verify IMAP settings** — Double-check server, port, SSL settings
3. **Test connectivity** — Run `scripts/imap-test.py` with exact settings
4. **Check quotas** — Verify destination has enough storage space
5. **Review logs** — Look for specific error messages in client logs
6. **Retry smaller batches** — Split large mailboxes into smaller chunks
7. **Contact support** — Provider-specific issues may need support tickets

See `references/troubleshooting.md` for comprehensive error resolution guide.

## Migration Best Practices

### Planning Phase
- **Inventory thoroughly** — Document all email accounts, sizes, special requirements
- **Test with pilot users** — Never migrate entire organization without testing
- **Communicate clearly** — Set expectations with users about timeline and downtime
- **Plan rollback** — Always have a way to revert if migration fails

### Execution Phase
- **Monitor actively** — Don't start migration and walk away
- **Validate incrementally** — Check each user/batch before proceeding
- **Keep logs** — Document what worked, what failed, and why
- **Stay flexible** — Be prepared to switch methods if primary approach fails

### Post-Migration
- **Validate data integrity** — Compare counts, spot-check important emails
- **Train users** — New interface, different features, updated mobile setup
- **Monitor performance** — Watch for issues in first 48-72 hours
- **Plan cleanup** — When to disable old accounts, how long to retain access