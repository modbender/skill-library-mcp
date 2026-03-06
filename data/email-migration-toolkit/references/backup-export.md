# Email Backup and Export Procedures

## Google Workspace / Gmail

### Method 1: Google Takeout (Recommended)

**Steps:**
1. Go to **takeout.google.com**
2. **Deselect all** → Select only **Mail**
3. Click **Next step**
4. Choose **Export once** and **Send download link via email**
5. Select **MBOX format** (most compatible)
6. Choose archive size (2GB recommended for easier download)
7. Click **Create export**
8. Wait for email notification (can take 2-48 hours)
9. Download archive files

**What's Included:**
- All emails from all folders
- Labels (as folder structure)
- Attachments
- Sent items, drafts, spam

**Format:** MBOX (Thunderbird, Apple Mail compatible)

### Method 2: IMAP Download

**Use when:** Takeout fails or you need selective backup

**Steps:**
1. Enable IMAP in Gmail settings
2. Set up email client (Thunderbird recommended)
3. Configure Gmail account with app password
4. Let client sync all folders
5. Export from client to desired format

## Microsoft 365 / Outlook

### Method 1: PST Export (Desktop Outlook)

**Steps:**
1. Open **Outlook Desktop** (not web version)
2. Go to **File** → **Open & Export** → **Import/Export**
3. Select **Export to a file** → **Next**
4. Choose **Outlook Data File (.pst)** → **Next**
5. Select account or specific folders → **Next**
6. Choose save location and filename → **Finish**
7. Set password (optional but recommended)

**What's Included:**
- All emails, sent items, drafts
- Calendar events
- Contacts
- Rules and settings

**Format:** PST (Outlook native, widely supported)

### Method 2: eDiscovery Export (Admin)

**Use when:** Admin-level bulk export needed

**Steps:**
1. **Microsoft Purview** compliance portal
2. **Content search** → Create new search
3. Select users/mailboxes to export
4. Run search → **Export results**
5. Download using eDiscovery Export Tool

**Requirements:** Compliance admin permissions

## Yahoo Mail

### Method 1: IMAP Download (Only Option)

**Steps:**
1. Enable **IMAP access** in Yahoo Mail settings
2. Generate **app password**: Account Security → App passwords
3. Configure email client with IMAP settings:
   - Server: imap.mail.yahoo.com
   - Port: 993, SSL enabled
   - Use app password (not regular password)
4. Let client download all mail
5. Export from client to desired format

**Limitations:**
- No bulk export tool from Yahoo
- Free accounts have folder limitations
- Large mailboxes may take days to sync

## Zoho Mail

### Method 1: Zoho's Migration Tool

**Steps:**
1. **Zoho Admin Console** → **Migration**
2. Choose **Export** option
3. Select users and date range
4. Choose format (MBOX recommended)
5. Submit request (may take hours/days)
6. Download when ready

**Requirements:** Admin access to Zoho organization

### Method 2: IMAP Download

**Steps:**
1. Use IMAP settings from provider matrix
2. Configure in email client
3. No app password needed for most Zoho accounts
4. Download and export locally

## iCloud Mail

### Method 1: IMAP Download (Only Option)

**Steps:**
1. Generate **app password**: appleid.apple.com → App-Specific Passwords
2. Configure email client with IMAP settings:
   - Server: imap.mail.me.com
   - Port: 993, SSL enabled
   - Use app password
3. Download all folders via client
4. Export from client

**Limitations:**
- No native export tool from Apple
- Some folders may not sync properly
- Slow IMAP performance

## ProtonMail

### Method 1: Individual Export (Web Interface)

**Steps:**
1. Log in to **ProtonMail web interface**
2. Open email to export
3. Click **More** → **Export**
4. Save as EML file
5. Repeat for each important email

**Limitations:**
- No bulk export option
- Very time-consuming for large mailboxes
- Free accounts cannot use Bridge

### Method 2: ProtonMail Bridge (Paid Plans)

**Steps:**
1. Install **ProtonMail Bridge** application
2. Add ProtonMail account to Bridge
3. Configure email client to connect to Bridge
4. Use local IMAP connection to download mail
5. Export from email client

**Requirements:**
- Paid ProtonMail plan
- Desktop Bridge application

## Exchange On-Premises

### Method 1: Exchange Management Shell

**Admin PowerShell:**
```powershell
New-MailboxExportRequest -Mailbox "user@domain.com" -FilePath "\\server\share\user.pst"
Get-MailboxExportRequest | Get-MailboxExportRequestStatistics
```

### Method 2: Outlook PST Export

**Same as Microsoft 365 method** — works for on-premises Exchange

## Thunderbird Universal Backup

**For any IMAP account:**

1. **Install Thunderbird** (free)
2. **Add email account** with IMAP settings
3. **Let sync complete** (may take hours/days)
4. **Profile backup**: Copy entire Thunderbird profile folder
   - Windows: `%APPDATA%\Thunderbird\Profiles\`
   - Mac: `~/Library/Thunderbird/Profiles/`
   - Linux: `~/.thunderbird/`

**Advantages:**
- Works with any IMAP provider
- Preserves folder structure
- Can import to other Thunderbird installations

## Format Conversion Tools

### MBOX to PST
- **MailStore Home** (free for personal use)
- **Stellar MBOX to PST Converter**
- **SysTools MBOX Converter**

### PST to MBOX
- **Aid4Mail** (commercial)
- **PST Converter Pro**
- **MailStore Home**

### EML to MBOX/PST
- **Thunderbird** (import EML files)
- **Windows Live Mail** (can import/export both)

## Backup Best Practices

### Before Migration
1. **Full backup** of source system
2. **Test restore** on sample data
3. **Document folder structure**
4. **Note special configurations** (rules, signatures, etc.)

### During Migration
1. **Incremental backups** of changes
2. **Keep source active** during migration
3. **Monitor backup integrity**

### After Migration
1. **Retain source backups** for 30-90 days
2. **Document successful migration**
3. **Archive backups** for compliance
4. **Test restore procedures**

## Storage Considerations

### File Sizes
- **MBOX files**: Can be very large (GB+)
- **PST files**: 50GB limit (older Outlook versions)
- **Split large files**: Use client options to split

### Compression
- **ZIP archives**: Significant compression for email
- **Encrypted archives**: Recommended for sensitive data
- **Cloud storage**: Ensure encryption in transit/rest

## Recovery Testing

### Verification Steps
1. **Import backup** to test system
2. **Compare email counts** with original
3. **Test search functionality**
4. **Verify attachments** open correctly
5. **Check folder structure** preservation
6. **Test with sample users**

### Common Issues
- **Character encoding** problems with international text
- **Date/time stamps** may change during export/import
- **Folder hierarchy** may flatten in some formats
- **Large attachments** may fail to export/import
- **Encrypted emails** may not decrypt after migration