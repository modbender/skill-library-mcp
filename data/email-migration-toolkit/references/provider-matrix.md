# Email Provider Matrix — IMAP/SMTP Settings

## Major Email Providers

| Provider | IMAP Server | IMAP Port | SMTP Server | SMTP Port | SSL/TLS | App Password |
|----------|-------------|-----------|-------------|-----------|---------|--------------|
| **Gmail** | imap.gmail.com | 993 | smtp.gmail.com | 465 | SSL | Required |
| **Outlook.com** | outlook.office365.com | 993 | smtp-mail.outlook.com | 587 | STARTTLS | Required |
| **Yahoo Mail** | imap.mail.yahoo.com | 993 | smtp.mail.yahoo.com | 465/587 | SSL | Required |
| **AOL Mail** | imap.aol.com | 993 | smtp.aol.com | 465/587 | SSL | Required |
| **iCloud Mail** | imap.mail.me.com | 993 | smtp.mail.me.com | 587 | STARTTLS | Required |
| **Zoho Mail** | imap.zoho.com | 993 | smtp.zoho.com | 465/587 | SSL | Optional |
| **ProtonMail** | 127.0.0.1* | 1143* | 127.0.0.1* | 1025* | Local | Bridge Only |
| **Fastmail** | imap.fastmail.com | 993 | smtp.fastmail.com | 465/587 | SSL | Optional |
| **Tutanota** | N/A | N/A | N/A | N/A | N/A | No IMAP |

\* ProtonMail requires ProtonMail Bridge application running locally

## Business/Enterprise Providers

| Provider | IMAP Server | IMAP Port | SMTP Server | SMTP Port | SSL/TLS | Notes |
|----------|-------------|-----------|-------------|-----------|---------|-------|
| **Microsoft 365** | outlook.office365.com | 993 | smtp.office365.com | 587 | STARTTLS | OAuth2 preferred |
| **Google Workspace** | imap.gmail.com | 993 | smtp.gmail.com | 465/587 | SSL | OAuth2 preferred |
| **Zoho Workplace** | imap.zoho.com | 993 | smtp.zoho.com | 465/587 | SSL | Domain-based auth |
| **Rackspace Email** | secure.emailsrvr.com | 993 | secure.emailsrvr.com | 587 | STARTTLS | Domain setup required |
| **Office 365** | outlook.office365.com | 993 | smtp.office365.com | 587 | STARTTLS | Same as Microsoft 365 |

## Regional/Local Providers

| Provider | IMAP Server | IMAP Port | SMTP Server | SMTP Port | SSL/TLS | Region |
|----------|-------------|-----------|-------------|-----------|---------|---------|
| **Mail.ru** | imap.mail.ru | 993 | smtp.mail.ru | 465 | SSL | Russia |
| **GMX** | imap.gmx.net | 993 | mail.gmx.net | 587 | STARTTLS | Germany |
| **1&1 IONOS** | imap.1and1.com | 993 | smtp.1and1.com | 587 | STARTTLS | Europe |
| **Yandex.Mail** | imap.yandex.com | 993 | smtp.yandex.com | 465 | SSL | Russia |
| **Naver Mail** | imap.naver.com | 993 | smtp.naver.com | 587 | STARTTLS | South Korea |

## Legacy/On-Premises

| System | Default IMAP | Default SMTP | Port Range | SSL Support | Notes |
|--------|-------------|--------------|------------|-------------|-------|
| **Exchange 2019** | mail.domain.com | mail.domain.com | 993/587 | Yes | Autodiscover available |
| **Exchange 2016** | mail.domain.com | mail.domain.com | 993/587 | Yes | Requires proper certificates |
| **Exchange 2013** | mail.domain.com | mail.domain.com | 993/587 | Yes | Legacy versions supported |
| **Zimbra** | mail.domain.com | mail.domain.com | 993/587 | Yes | Open source alternative |
| **MDaemon** | mail.domain.com | mail.domain.com | 993/587 | Yes | Small business focused |
| **Kerio Connect** | mail.domain.com | mail.domain.com | 993/587 | Yes | SMB solution |

## Authentication Methods

### App Passwords Required
- Gmail (with 2FA enabled)
- Yahoo Mail (with 2FA enabled)  
- iCloud Mail (always)
- Outlook.com (with 2FA enabled)
- AOL Mail (with 2FA enabled)

### OAuth2 Supported
- Gmail/Google Workspace
- Microsoft 365/Outlook.com
- Yahoo Mail (limited)

### Standard Password
- Zoho Mail
- Fastmail
- Most on-premises systems
- Regional providers (varies)

## Special Configuration Notes

### Gmail
- **Less secure app access**: Deprecated as of May 2022
- **Must use**: App passwords or OAuth2
- **IMAP folders**: All Mail, Spam, Trash have special behavior
- **Labels**: Become folders in IMAP clients

### Yahoo Mail
- **Free accounts**: IMAP access included
- **App passwords**: Required even without 2FA in some regions
- **Folders**: Limited folder depth on free accounts

### iCloud Mail
- **App passwords**: Always required regardless of 2FA
- **Generate at**: appleid.apple.com → Sign-In and Security
- **Limitations**: Some IMAP features limited on free accounts

### ProtonMail
- **IMAP access**: Only via ProtonMail Bridge (paid plans)
- **Bridge setup**: Acts as local IMAP/SMTP proxy
- **Free accounts**: No IMAP access available
- **Export**: Individual emails only via web interface

### Zoho Mail
- **Free tier**: 5GB storage, IMAP included
- **Business**: Full IMAP/API access
- **Migration tools**: Zoho provides assisted migration services
- **Custom domains**: Full DNS control required

## Testing Commands

```bash
# Test IMAP connectivity
telnet imap.provider.com 993
openssl s_client -connect imap.provider.com:993

# Test SMTP connectivity  
telnet smtp.provider.com 587
openssl s_client -starttls smtp -connect smtp.provider.com:587

# Check MX records
dig MX domain.com +short

# Verify SSL certificate
openssl s_client -connect imap.provider.com:993 -servername imap.provider.com
```

## Common Port Alternatives

| Service | Primary | Alternative | Notes |
|---------|---------|-------------|--------|
| **IMAP SSL** | 993 | 143+STARTTLS | 993 is encrypted from start |
| **SMTP SSL** | 465 | 587+STARTTLS | 465 legacy but still common |
| **POP3 SSL** | 995 | 110+STARTTLS | Not recommended for migration |

## Troubleshooting Matrix

| Error | Likely Cause | Check |
|-------|-------------|-------|
| Connection refused | Wrong server/port | Verify provider settings |
| Authentication failed | Wrong credentials | Try app password |
| SSL handshake failed | Certificate issues | Check SSL/TLS setting |
| Folder not found | IMAP folder quirks | Check provider documentation |
| Quota exceeded | Storage limit | Check account storage limits |