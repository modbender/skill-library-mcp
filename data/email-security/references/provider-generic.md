# Generic Email Provider Guide

Security considerations for IMAP/SMTP, Proton Mail, and other email providers.

## IMAP Security

### Connection Security
Always use secure connections:

```python
import imaplib

# Secure connection (required)
imap = imaplib.IMAP4_SSL('imap.provider.com', 993)
imap.login(username, password)
```

Never use plain IMAP (port 143) without STARTTLS.

### Credential Storage
- Use app-specific passwords when available
- Store credentials encrypted
- Use OAuth if provider supports it (Microsoft, Yahoo)

## SMTP Security

### Sending Safely
```python
import smtplib
import ssl

context = ssl.create_default_context()
with smtplib.SMTP_SSL('smtp.provider.com', 465, context=context) as server:
    server.login(username, password)
    server.send_message(msg)
```

### SPF/DKIM for Outgoing Mail
If agent sends emails, ensure:
- SPF record includes sending server
- DKIM signing enabled
- DMARC policy published

This prevents agent emails from being marked as spam.

## Proton Mail Specifics

### Proton Bridge (Desktop)
Proton Mail requires the Proton Bridge app for IMAP/SMTP:

- Local IMAP: `127.0.0.1:1143`
- Local SMTP: `127.0.0.1:1025`
- Uses app-generated passwords

### End-to-End Encryption
Proton Mail emails are encrypted. Considerations:
- Content is only readable after decryption
- Agent must have access to decrypted content
- External emails (non-Proton) are stored encrypted

### Proton API (Direct)
For programmatic access without Bridge:
- Requires Proton API authentication
- Rate limits apply
- SRP (Secure Remote Password) protocol

## Standard Email Headers

Headers for security validation (all providers):

```
Return-Path: <sender@example.com>
Received: from mx.example.com (1.2.3.4)
        by mail.provider.com with SMTP
Authentication-Results: provider.com;
        spf=pass smtp.mailfrom=example.com;
        dkim=pass header.d=example.com
From: Sender Name <sender@example.com>
Reply-To: reply@example.com
```

### Header Validation Checklist
- [ ] `From` matches expected sender
- [ ] `Reply-To` matches `From` (if set)
- [ ] `Return-Path` matches domain
- [ ] `Authentication-Results` shows pass for SPF/DKIM
- [ ] `Received` chain is consistent

## Self-Hosted Email

For self-hosted email servers (Postfix, Dovecot, etc.):

### Security Considerations
- Ensure TLS 1.2+ for all connections
- Keep mail server software updated
- Monitor for open relay issues
- Implement fail2ban for brute force protection

### Log Analysis
Self-hosted servers provide detailed logs:

```
/var/log/mail.log
/var/log/maillog
```

Monitor for:
- Authentication failures
- Unusual sending patterns
- Connection from unexpected IPs

## FastMail, Yahoo, Outlook.com

### Common IMAP Settings

| Provider | IMAP Server | Port |
|----------|-------------|------|
| FastMail | imap.fastmail.com | 993 |
| Yahoo | imap.mail.yahoo.com | 993 |
| Outlook | outlook.office365.com | 993 |

### App Passwords
All major providers require app-specific passwords when 2FA enabled:
- Generate in provider's security settings
- Use instead of main password
- Revoke if compromised

## Universal Security Rules

Regardless of provider:

1. **Always use TLS/SSL** - No exceptions
2. **Verify sender identity** - Check headers, not just From
3. **Parse newest message only** - Ignore quoted content
4. **Respect rate limits** - Prevent account lockout
5. **Log all actions** - Maintain audit trail
