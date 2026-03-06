# IMAP Settings by Provider

## Quick Reference Cards

### Gmail
```
IMAP Server: imap.gmail.com
Port: 993 (SSL/TLS)
SMTP Server: smtp.gmail.com  
Port: 465 (SSL) or 587 (STARTTLS)
Authentication: App Password (2FA required)
Special: Labels appear as folders, All Mail contains everything
```

### Microsoft 365/Outlook.com
```
IMAP Server: outlook.office365.com
Port: 993 (SSL/TLS)
SMTP Server: smtp-mail.outlook.com (personal) or smtp.office365.com (business)
Port: 587 (STARTTLS)
Authentication: App Password or OAuth2
Special: Modern auth preferred for business accounts
```

### Yahoo Mail
```
IMAP Server: imap.mail.yahoo.com
Port: 993 (SSL/TLS)
SMTP Server: smtp.mail.yahoo.com
Port: 465 (SSL) or 587 (STARTTLS)
Authentication: App Password required
Special: Free accounts have folder limitations
```

### iCloud Mail
```
IMAP Server: imap.mail.me.com
Port: 993 (SSL/TLS)
SMTP Server: smtp.mail.me.com
Port: 587 (STARTTLS)
Authentication: App Password always required
Special: Generate at appleid.apple.com
```

### Zoho Mail
```
IMAP Server: imap.zoho.com
Port: 993 (SSL/TLS)
SMTP Server: smtp.zoho.com
Port: 465 (SSL) or 587 (STARTTLS)
Authentication: Regular password or app password
Special: Full IMAP support on free and paid plans
```

## Provider-Specific Setup Instructions

### Gmail Setup

**Enable IMAP:**
1. Settings → Forwarding and POP/IMAP
2. Enable IMAP
3. Choose "Auto-Expunge off" for migration

**Generate App Password:**
1. Google Account → Security
2. 2-Step Verification (must be enabled)
3. App passwords → Generate
4. Use generated password (not regular password)

**Client Configuration:**
```
Username: full.email@gmail.com
Password: 16-character app password
Security: SSL/TLS
Server Certificate: Accept
```

### Yahoo Mail Setup

**Enable IMAP:**
1. Account Info → Account Security
2. Generate and manage app passwords
3. Create app password for "Mail"

**Client Configuration:**
```
Username: full.email@yahoo.com
Password: app password from Yahoo
Security: SSL/TLS
Authentication: Normal password
```

**Troubleshooting:**
- Use full email address as username
- Ensure "Less secure app access" is enabled (legacy)
- Some regions require app passwords even without 2FA

### iCloud Mail Setup

**Generate App Password:**
1. Sign in to appleid.apple.com
2. Sign-In and Security → App-Specific Passwords
3. Generate password for "Mail"
4. Use immediately (passwords shown only once)

**Client Configuration:**
```
Username: apple.id@icloud.com
Password: app-specific password
IMAP Prefix: INBOX (if required)
Security: SSL/TLS
```

**Common Issues:**
- Must use @icloud.com, not @me.com or @mac.com in client
- Some clients require INBOX prefix
- Slow IMAP response times are normal

### Zoho Mail Setup

**Basic Configuration:**
```
Username: user@domain.com (or user@zohomail.com)
Password: regular account password
Security: SSL/TLS
Special Folders: Standard IMAP folders
```

**For Enhanced Security:**
1. Zoho Account → Security → App Passwords
2. Generate specific password for email client
3. Use app password instead of regular password

### Microsoft 365 Setup

**Modern Authentication (Preferred):**
- Use OAuth2 if supported by client
- Sign in with regular credentials
- Client handles token refresh automatically

**Basic Authentication (Legacy):**
```
Username: user@domain.com
Password: regular password or app password
Security: STARTTLS on port 587
Server: outlook.office365.com
```

**App Passwords (if 2FA enabled):**
1. portal.office.com → My Account → Security info
2. Add method → App password
3. Use generated password in email client

## Client-Specific Settings

### Outlook Desktop

**Account Setup Wizard:**
1. File → Add Account → Manual setup
2. Choose IMAP → Enter server details
3. Test account settings before completing
4. Set sync limits if needed (12 months recommended)

**Advanced Settings:**
- Root folder path: Leave blank (usually)
- Use secure authentication: Check if available
- Leave messages on server: Check for migration
- Download shared folders: Uncheck initially

### Thunderbird

**Account Setup:**
1. Account Actions → Add Mail Account
2. Enter name, email, password
3. Manual config if auto-detection fails
4. Set server settings from provider matrix

**Optimization for Migration:**
- Edit → Preferences → Advanced → Config Editor
- Set `mail.server.default.max_cached_connections` to 1
- Set download limit to "Don't download messages larger than X MB"

### Apple Mail

**Account Setup:**
1. Mail → Preferences → Accounts → Add Account
2. Choose "Other Mail Account"
3. Enter email and app password
4. Manual configuration if needed

**Performance Tips:**
- Mailbox → Synchronize All Accounts
- View → Mailbox List → Show All Mailboxes
- For large mailboxes, sync recent messages first

### Mobile Clients (iOS/Android)

**iOS Mail:**
```
Account Type: IMAP
Mail Server: (from provider matrix)
Username: full email address
Password: app password
Use SSL: On
Authentication: Password
Server Port: 993
```

**Gmail App:**
- Can add non-Gmail IMAP accounts
- Go to Settings → Add Account → Other
- Use IMAP settings from matrix

**Outlook Mobile:**
- Supports most IMAP providers
- Add Account → choose provider or "Other"
- Auto-configuration works for major providers

## Advanced Configuration

### Folder Mapping

**Gmail Specifics:**
- All Mail = Archive in other clients
- Sent Mail = Sent Items
- [Gmail]/Spam = Junk/Spam
- [Gmail]/Trash = Deleted Items
- Labels appear as additional folders

**Exchange/Outlook Mapping:**
- Inbox = Inbox
- Sent Items = Sent Mail  
- Deleted Items = Trash
- Junk Email = Spam
- Archive = Archive (if enabled)

### Batch Optimization

**For Migration Tools:**
- Increase connection timeout: 120+ seconds
- Reduce concurrent connections: 1-2 max
- Enable incremental sync
- Set realistic batch sizes (1000 messages max)

**Throttling Settings:**
```
IMAP Commands per minute: 60-120
Concurrent folders: 1-3
Message size limit: 25MB
Retry attempts: 3-5
Backoff multiplier: 2x
```

## Security Considerations

### Authentication Methods Ranked

1. **OAuth2** (most secure) - Token-based, handles 2FA
2. **App passwords** (recommended) - Unique per application
3. **Regular passwords** (least secure) - Main account password

### Network Security

**SSL/TLS Requirements:**
- Always use encrypted connections (993/465/587)
- Verify server certificates
- Avoid plain text IMAP (port 143) in production

**Firewall Considerations:**
- Outbound 993 (IMAP SSL) must be allowed
- Outbound 465/587 (SMTP SSL/STARTTLS) for sending
- Some providers use additional ports for authentication

### Credential Management

**Best Practices:**
- Use app passwords when available
- Rotate passwords after migration
- Document credentials securely
- Revoke unused app passwords
- Monitor for suspicious login attempts

**App Password Naming:**
- Use descriptive names: "Migration Tool - Jan 2024"
- Include date for expiration tracking
- Note purpose and device/application