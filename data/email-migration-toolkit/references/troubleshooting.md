# Email Migration Troubleshooting Guide

## Connection Issues

### "Connection Refused" or "Cannot Connect"

**Likely Causes:**
- Wrong server address or port
- Firewall blocking connections  
- Provider maintenance/downtime

**Diagnostic Steps:**
```bash
# Test basic connectivity
telnet imap.provider.com 993

# Test SSL connection
openssl s_client -connect imap.provider.com:993 -servername imap.provider.com

# Check DNS resolution
nslookup imap.provider.com
dig imap.provider.com A +short
```

**Solutions:**
1. Verify server settings against provider documentation
2. Try alternative ports (587 for SMTP, 143+STARTTLS for IMAP)
3. Check corporate firewall/proxy settings
4. Test from different network (mobile hotspot)
5. Contact provider support if widespread issue

### "SSL/TLS Handshake Failed"

**Likely Causes:**
- Certificate issues
- Outdated client
- Wrong encryption settings

**Diagnostic Steps:**
```bash
# Check certificate details
openssl s_client -connect imap.provider.com:993 -servername imap.provider.com

# Check supported ciphers
nmap --script ssl-enum-ciphers -p 993 imap.provider.com
```

**Solutions:**
1. Update email client to latest version
2. Try different SSL/TLS settings (SSL vs STARTTLS)
3. Disable certificate validation temporarily for testing
4. Check system date/time (affects certificate validation)
5. Clear SSL certificate cache in client

## Authentication Failures

### "Invalid Credentials" or "Authentication Failed"

**Common Causes by Provider:**

**Gmail:**
- Not using app password with 2FA enabled
- "Less secure app access" disabled (deprecated)
- Wrong Google Account selected (multiple accounts)

**Yahoo:**
- Account key/app password required
- Using wrong domain (@yahoo.com vs @yahoo.co.uk)
- 2FA blocking regular password

**iCloud:**
- App-specific password not generated
- Using @me.com instead of @icloud.com
- Case sensitivity in username

**Outlook.com:**
- Two-factor authentication enabled but using regular password
- Modern authentication required
- Wrong server for personal vs business account

**Diagnostic Steps:**
1. Test credentials on provider's webmail interface
2. Check if 2FA is enabled on account
3. Verify exact username format required
4. Try authentication in incognito/private browser

**Solutions by Provider:**

**Gmail Fix:**
```
1. Google Account → Security → 2-Step Verification → On
2. App passwords → Generate
3. Use 16-character generated password in client
4. Username: full email address
```

**Yahoo Fix:**
```
1. Account Security → Generate app password
2. Name it descriptively ("Migration Tool")
3. Use generated password immediately
4. Username: full email address including domain
```

**iCloud Fix:**
```
1. appleid.apple.com → Sign-In and Security
2. App-Specific Passwords → Generate
3. Use immediately (shown only once)
4. Username: must be @icloud.com format
```

### "Account Locked" or "Too Many Login Attempts"

**Immediate Actions:**
1. Stop migration tool immediately
2. Wait 15-30 minutes before retry
3. Check provider's account security page
4. Look for security alerts in email

**Prevention:**
- Reduce concurrent connections to 1-2
- Add delays between operations
- Use provider-recommended rate limits
- Implement exponential backoff

## Data Transfer Issues

### "Missing Emails" or "Incomplete Migration"

**Check These First:**
1. **Date range filters** — Migration tool may have date limits
2. **Folder selection** — Some folders might be excluded
3. **Size limits** — Large messages might be skipped
4. **Spam/Junk folders** — Often excluded by default

**Diagnostic Steps:**
```bash
# Check total message count via IMAP
# Use provided mailbox-size.py script
python3 scripts/mailbox-size.py user@provider.com password
```

**Solutions:**
1. Run migration in smaller date ranges
2. Migrate large folders separately
3. Check provider's trash/spam folders
4. Verify folder permissions (shared mailboxes)
5. Re-run migration for delta sync

### "Emails Corrupted" or "Encoding Issues"

**Symptoms:**
- Foreign characters displayed as "???" or boxes
- HTML emails show as plain text
- Attachments won't open

**Common Causes:**
- Character encoding mismatch (UTF-8 vs. Latin-1)
- MIME type conversion issues
- Client-side display problems

**Solutions:**
1. Set client to UTF-8 encoding
2. Use MBOX format for better compatibility
3. Test with different email client
4. Check source encoding in original provider
5. Consider format conversion tools

### "Slow Migration Speed"

**Typical Speeds by Provider:**
- Gmail: 500-1000 messages/hour
- Yahoo: 200-500 messages/hour  
- iCloud: 100-300 messages/hour
- Zoho: 300-800 messages/hour

**Optimization Steps:**
1. **Reduce concurrent connections** to 1
2. **Use off-peak hours** (night/weekend)
3. **Filter by date** — migrate recent first
4. **Exclude large attachments** initially
5. **Use dedicated network** (avoid shared Wi-Fi)

**Provider-Specific Tweaks:**

**Gmail:**
- Use Google Takeout for initial bulk export
- IMAP has daily bandwidth limits
- Multiple app passwords don't increase speed

**Yahoo:**
- Free accounts have lower limits
- Business accounts perform better
- Avoid Friday evenings (maintenance window)

**iCloud:**
- Inherently slow IMAP implementation  
- Break into very small batches
- Consider overnight migration runs

## Folder and Structure Issues

### "Folders Missing" or "Wrong Hierarchy"

**Gmail Specific:**
- Labels become folders in IMAP clients
- Nested labels create folder hierarchy
- "All Mail" contains everything (may cause duplicates)

**Exchange/Outlook Specific:**
- Some system folders have fixed names
- Public folders require special permissions
- Archive folders may be separate

**Solutions:**
1. **Map folder names** before migration
2. **Create target folders** manually if needed
3. **Check IMAP folder subscriptions** in client
4. **Use folder mapping tools** in migration software
5. **Document special folder behaviors**

### "Duplicate Messages"

**Common Causes:**
- Message exists in multiple labels/folders
- Migration tool ran multiple times
- IMAP "All Mail" folder included

**Prevention:**
1. Exclude "All Mail" folder in Gmail migrations
2. Use message-ID based deduplication
3. Run test migration on small subset first
4. Check migration tool's duplicate handling

**Cleanup:**
- Use client's built-in duplicate removal
- PowerShell scripts for Exchange
- Third-party deduplication tools

## Provider-Specific Error Codes

### Gmail Error Codes

| Error | Code | Meaning | Solution |
|-------|------|---------|----------|
| IMAP_LOGIN_FAILED | - | Wrong credentials | Use app password |
| QUOTA_EXCEEDED | - | Daily limit reached | Wait 24 hours |
| CONNECTION_FAILED | - | Too many connections | Reduce concurrency |

### Yahoo Error Codes

| Error | Meaning | Solution |
|-------|---------|----------|
| LOGIN invalid credentials | Wrong password | Generate app password |
| IMAP disabled | IMAP not enabled | Enable in account settings |
| Rate limited | Too many requests | Wait and retry |

### Microsoft Error Codes

| Error | Code | Meaning | Solution |
|-------|------|---------|----------|
| AUTHENTICATE failed | - | Modern auth required | Use OAuth2 or app password |
| CONNECTION_LOST | - | Network timeout | Increase timeout settings |
| QUOTA_EXCEEDED | - | Mailbox full | Clean up or upgrade storage |

## Migration Tool Specific Issues

### GWMMO (Google Workspace Migration for Microsoft Outlook)

**Common Issues:**
- Hangs at "Preparing migration"
- "Unable to connect to Google"
- Outlook profile corruption

**Solutions:**
1. Run as administrator
2. Create new Outlook profile
3. Disable antivirus temporarily
4. Check Windows user permissions

### Microsoft Migration Service

**Common Issues:**
- Service account permissions
- API rate limiting
- Delta sync failures

**Solutions:**
1. Re-authorize service account
2. Check Google API console quotas
3. Use smaller batch sizes
4. Monitor migration dashboard

### Third-Party Tools (ImapSync, etc.)

**Common Issues:**
- Perl dependencies missing
- SSL certificate problems
- Memory issues with large mailboxes

**Solutions:**
1. Install required dependencies
2. Use --nossl for testing
3. Process in smaller chunks
4. Monitor system resources

## Network and Infrastructure Issues

### Corporate Firewall Problems

**Required Outbound Ports:**
- 993 (IMAP SSL)
- 465 (SMTP SSL)  
- 587 (SMTP STARTTLS)
- 80/443 (authentication/OAuth)

**Proxy Configuration:**
- Many email clients don't support SOCKS proxies for IMAP
- HTTP proxies rarely work with IMAP
- Consider VPN instead of proxy

### DNS Issues

**Symptoms:**
- Intermittent connection failures
- Some domains work, others don't
- Works from one network but not another

**Diagnostic Steps:**
```bash
# Check DNS resolution
nslookup imap.gmail.com
dig @8.8.8.8 imap.gmail.com A

# Test different DNS servers
dig @1.1.1.1 imap.gmail.com A
dig @208.67.222.222 imap.gmail.com A
```

**Solutions:**
1. Use public DNS servers (8.8.8.8, 1.1.1.1)
2. Clear DNS cache
3. Check hosts file for overrides
4. Test with direct IP addresses

## Recovery Procedures

### When Migration Fails Completely

1. **Stop all migration processes**
2. **Document current state** — what was migrated, what failed
3. **Check source data integrity** — ensure nothing was lost
4. **Analyze logs** for patterns in failures
5. **Test with small subset** before full retry
6. **Consider alternative migration method**

### Partial Migration Recovery

1. **Identify successfully migrated data**
2. **Export list of processed items** from migration tool
3. **Create exclusion list** for retry
4. **Resume from last checkpoint** if tool supports it
5. **Validate data integrity** after completion

### Data Validation Checklist

After any migration issue resolution:

- [ ] **Email count matches** source vs. destination
- [ ] **Folder structure** preserved correctly  
- [ ] **Recent emails** (last 30 days) fully present
- [ ] **Sent items** migrated correctly
- [ ] **Attachments** open without errors
- [ ] **Search functionality** works in destination
- [ ] **Special characters** display correctly
- [ ] **User can login** and access all data

## Emergency Contacts

### When to Contact Provider Support

**Gmail/Google Workspace:**
- API quota issues
- Service account problems
- Unusual authentication errors

**Microsoft 365:**
- Tenant configuration issues
- Migration service failures
- Modern authentication problems

**Yahoo:**
- Account security lockouts
- Persistent authentication failures
- IMAP access problems

**Include in Support Request:**
1. Exact error messages
2. Migration tool and version
3. Timeline of when issue started
4. Steps already attempted
5. Affected user count/impact