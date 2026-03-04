---
name: cloudflare
description: Manage Cloudflare via API — DNS zones and records, page rules, SSL/TLS settings, caching, firewall rules, Workers, and analytics. Free tier includes DNS, CDN, DDoS protection, and SSL.
---

# Cloudflare API Skill

Control Cloudflare infrastructure: DNS management, CDN, security, Workers, and more.

## Authentication

API token required. Get one from: https://dash.cloudflare.com/profile/api-tokens

**Recommended permissions:**
- Zone:Zone:Read
- Zone:Zone:Edit  
- Zone:DNS:Read
- Zone:DNS:Edit

Store in `~/.config/cloudflare/token`:
```bash
mkdir -p ~/.config/cloudflare
echo -n "YOUR_API_TOKEN" > ~/.config/cloudflare/token
chmod 600 ~/.config/cloudflare/token
```

## Quick Reference

### Zones (Domains)

```bash
# List all zones
python3 scripts/cloudflare.py zones list

# Get zone details
python3 scripts/cloudflare.py zones get <domain>

# Add new zone
python3 scripts/cloudflare.py zones add <domain>

# Delete zone
python3 scripts/cloudflare.py zones delete <domain>

# Check zone status (pending/active)
python3 scripts/cloudflare.py zones status <domain>

# Purge cache
python3 scripts/cloudflare.py zones purge <domain>
python3 scripts/cloudflare.py zones purge <domain> --urls https://example.com/page
```

### DNS Records

```bash
# List records for a zone
python3 scripts/cloudflare.py dns list <domain>

# Add record
python3 scripts/cloudflare.py dns add <domain> --type A --name @ --content 1.2.3.4
python3 scripts/cloudflare.py dns add <domain> --type CNAME --name www --content example.com
python3 scripts/cloudflare.py dns add <domain> --type MX --name @ --content mail.example.com --priority 10
python3 scripts/cloudflare.py dns add <domain> --type TXT --name @ --content "v=spf1 include:_spf.google.com ~all"

# Update record
python3 scripts/cloudflare.py dns update <domain> <record_id> --content 5.6.7.8

# Delete record
python3 scripts/cloudflare.py dns delete <domain> <record_id>

# Proxy toggle (orange cloud on/off)
python3 scripts/cloudflare.py dns proxy <domain> <record_id> --on
python3 scripts/cloudflare.py dns proxy <domain> <record_id> --off
```

### SSL/TLS

```bash
# Get SSL mode
python3 scripts/cloudflare.py ssl get <domain>

# Set SSL mode (off, flexible, full, strict)
python3 scripts/cloudflare.py ssl set <domain> --mode full

# Always use HTTPS
python3 scripts/cloudflare.py ssl https <domain> --on
```

### Page Rules

```bash
# List page rules
python3 scripts/cloudflare.py rules list <domain>

# Add redirect rule
python3 scripts/cloudflare.py rules add <domain> --match "example.com/*" --redirect "https://new.com/$1"

# Delete rule
python3 scripts/cloudflare.py rules delete <domain> <rule_id>
```

### Firewall

```bash
# List firewall rules
python3 scripts/cloudflare.py firewall list <domain>

# Block IP
python3 scripts/cloudflare.py firewall block <domain> --ip 1.2.3.4 --note "Spammer"

# Block country
python3 scripts/cloudflare.py firewall block <domain> --country CN --note "Block China"

# Whitelist IP
python3 scripts/cloudflare.py firewall allow <domain> --ip 1.2.3.4

# Challenge (captcha) for IP range
python3 scripts/cloudflare.py firewall challenge <domain> --ip 1.2.3.0/24
```

### Analytics

```bash
# Get traffic stats (last 24h)
python3 scripts/cloudflare.py analytics <domain>

# Get stats for date range
python3 scripts/cloudflare.py analytics <domain> --since 2024-01-01 --until 2024-01-31
```

### Workers (Serverless)

```bash
# List workers
python3 scripts/cloudflare.py workers list

# Deploy worker
python3 scripts/cloudflare.py workers deploy <name> --script worker.js

# Delete worker
python3 scripts/cloudflare.py workers delete <name>
```

## DNS Record Types

| Type | Purpose | Example |
|------|---------|---------|
| A | IPv4 address | 192.0.2.1 |
| AAAA | IPv6 address | 2001:db8::1 |
| CNAME | Alias | www → example.com |
| MX | Mail server | mail.example.com (priority 10) |
| TXT | Text/verification | v=spf1 ... |
| NS | Nameserver | ns1.example.com |
| SRV | Service | _sip._tcp.example.com |
| CAA | Certificate authority | letsencrypt.org |

## Proxy Status (Orange Cloud)

- **Proxied (on)**: Traffic goes through Cloudflare CDN — caching, DDoS protection, hides origin IP
- **DNS only (off)**: Direct connection to origin — use for mail servers, non-HTTP services

```bash
# Enable proxy
python3 scripts/cloudflare.py dns add example.com --type A --name @ --content 1.2.3.4 --proxied

# Disable proxy (DNS only)
python3 scripts/cloudflare.py dns add example.com --type A --name mail --content 1.2.3.4 --no-proxy
```

## SSL Modes

| Mode | Description |
|------|-------------|
| off | No SSL (not recommended) |
| flexible | HTTPS to Cloudflare, HTTP to origin |
| full | HTTPS end-to-end, any cert on origin |
| strict | HTTPS end-to-end, valid cert on origin |

## Common Workflows

### Add a New Domain

```bash
# 1. Add zone to Cloudflare
python3 scripts/cloudflare.py zones add example.com

# 2. Note the nameservers (e.g., adam.ns.cloudflare.com, bella.ns.cloudflare.com)

# 3. Update nameservers at your registrar

# 4. Add DNS records
python3 scripts/cloudflare.py dns add example.com --type A --name @ --content 1.2.3.4 --proxied
python3 scripts/cloudflare.py dns add example.com --type CNAME --name www --content example.com --proxied

# 5. Set SSL to strict
python3 scripts/cloudflare.py ssl set example.com --mode strict
```

### Migrate DNS from Another Provider

```bash
# 1. Add zone (Cloudflare will scan existing records)
python3 scripts/cloudflare.py zones add example.com

# 2. Verify records imported correctly
python3 scripts/cloudflare.py dns list example.com

# 3. Add any missing records
python3 scripts/cloudflare.py dns add example.com --type MX --name @ --content mail.example.com --priority 10

# 4. Update nameservers at registrar

# 5. Wait for propagation, check status
python3 scripts/cloudflare.py zones status example.com
```

### Set Up Email Records

```bash
# MX records
python3 scripts/cloudflare.py dns add example.com --type MX --name @ --content mx1.provider.com --priority 10
python3 scripts/cloudflare.py dns add example.com --type MX --name @ --content mx2.provider.com --priority 20

# SPF
python3 scripts/cloudflare.py dns add example.com --type TXT --name @ --content "v=spf1 include:_spf.provider.com ~all"

# DKIM
python3 scripts/cloudflare.py dns add example.com --type TXT --name selector._domainkey --content "v=DKIM1; k=rsa; p=..."

# DMARC
python3 scripts/cloudflare.py dns add example.com --type TXT --name _dmarc --content "v=DMARC1; p=quarantine; rua=mailto:dmarc@example.com"
```

## Direct API Access

```bash
TOKEN=$(cat ~/.config/cloudflare/token)
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     https://api.cloudflare.com/client/v4/zones
```

## API Documentation

- Full API reference: https://developers.cloudflare.com/api/
- API v4 base URL: https://api.cloudflare.com/client/v4/

## Free Plan Includes

- DNS hosting (unlimited queries)
- CDN (caching at 300+ edge locations)
- DDoS protection (unmetered)
- SSL/TLS certificates (auto-renewed)
- 3 page rules
- Basic firewall rules
- Analytics

## Nameservers

When you add a domain, Cloudflare assigns two nameservers like:
- `adam.ns.cloudflare.com`
- `bella.ns.cloudflare.com`

Update these at your domain registrar. Zone stays "pending" until nameservers propagate.
