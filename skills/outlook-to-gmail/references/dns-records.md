# DNS Records — Google Workspace

Copy-paste templates for MX cutover.

## MX Records

Remove ALL existing MX records, then add:

| Type | Host | Value | Priority | TTL |
|------|------|-------|----------|-----|
| MX | @ | ASPMX.L.GOOGLE.COM | 1 | 3600 |
| MX | @ | ALT1.ASPMX.L.GOOGLE.COM | 5 | 3600 |
| MX | @ | ALT2.ASPMX.L.GOOGLE.COM | 5 | 3600 |
| MX | @ | ALT3.ASPMX.L.GOOGLE.COM | 10 | 3600 |
| MX | @ | ALT4.ASPMX.L.GOOGLE.COM | 10 | 3600 |

## SPF Record

```
Type: TXT
Host: @
Value: v=spf1 include:_spf.google.com ~all
TTL: 3600
```

If client also sends from other services (HubSpot, Mailchimp, etc.), combine:
```
v=spf1 include:_spf.google.com include:mail.hubspot.net include:servers.mcsv.net ~all
```

## DKIM Record

Generated in Admin Console → Apps → Gmail → Authenticate email.
Typically a TXT record at `google._domainkey.domain.com`.

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

## Autodiscover / Autoconfig (Optional)

To help Outlook clients auto-configure:
```
Type: CNAME
Host: autodiscover
Value: autodiscover.outlook.com
TTL: 3600
```

Remove this after migration if no longer using Exchange.

## Verification Commands

```bash
# Check MX
dig MX domain.com +short

# Check SPF
dig TXT domain.com +short | grep spf

# Check DKIM
dig TXT google._domainkey.domain.com +short

# Check DMARC
dig TXT _dmarc.domain.com +short

# Check propagation worldwide
# https://dnschecker.org
```
