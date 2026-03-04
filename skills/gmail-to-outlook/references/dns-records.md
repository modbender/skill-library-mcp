# DNS Records — Microsoft 365

Copy-paste templates for MX cutover from Google to Microsoft.

## MX Records

Remove ALL existing MX records, then add:

| Type | Host | Value | Priority | TTL |
|------|------|-------|----------|-----|
| MX | @ | [tenant-name].mail.protection.outlook.com | 0 | 3600 |

Replace `[tenant-name]` with your Microsoft 365 tenant name (e.g., `company-com` for company.com).

## SPF Record

```
Type: TXT
Host: @
Value: v=spf1 include:spf.protection.outlook.com ~all
TTL: 3600
```

If client also sends from other services (HubSpot, Mailchimp, etc.), combine:
```
v=spf1 include:spf.protection.outlook.com include:mail.hubspot.net include:servers.mcsv.net ~all
```

## DKIM Record

Enabled in Microsoft 365 Defender → Email & Collaboration → Policies & Rules → Threat policies → Email Authentication Settings → DKIM.

Two CNAME records will be generated:
```
Type: CNAME
Host: selector1._domainkey
Value: selector1-[tenant-guid]._domainkey.[tenant-name].onmicrosoft.com
TTL: 3600

Type: CNAME
Host: selector2._domainkey
Value: selector2-[tenant-guid]._domainkey.[tenant-name].onmicrosoft.com
TTL: 3600
```

## DMARC Record

Start permissive, tighten over 2-4 weeks:

```
# Phase 1: Monitor only
Type: TXT
Host: _dmarc
Value: v=DMARC1; p=none; rua=mailto:dmarc-reports@domain.com

# Phase 2: Quarantine (after 2 weeks)
Value: v=DMARC1; p=quarantine; pct=25; rua=mailto:dmarc-reports@domain.com

# Phase 3: Reject (after 4 weeks)
Value: v=DMARC1; p=reject; rua=mailto:dmarc-reports@domain.com
```

## Autodiscover

Essential for Outlook client auto-configuration:
```
Type: CNAME
Host: autodiscover
Value: autodiscover.outlook.com
TTL: 3600
```

## Mobile Device Management (Optional)

If using Intune/MDM:
```
Type: CNAME
Host: enterpriseregistration
Value: enterpriseregistration.windows.net
TTL: 3600

Type: CNAME
Host: enterpriseenrollment
Value: enterpriseenrollment.manage.microsoft.com
TTL: 3600
```

## Verification Commands

```bash
# Check MX
dig MX domain.com +short

# Check SPF
dig TXT domain.com +short | grep spf

# Check DKIM selectors
dig CNAME selector1._domainkey.domain.com +short
dig CNAME selector2._domainkey.domain.com +short

# Check DMARC
dig TXT _dmarc.domain.com +short

# Check Autodiscover
dig CNAME autodiscover.domain.com +short

# Check propagation worldwide
# https://dnschecker.org
```

## Pre-Cutover Test

Before changing MX records, test mail flow:
```bash
# Send test email to:
# [user]@[tenant-name].mail.onmicrosoft.com
# If it reaches the user, Exchange Online is working
```