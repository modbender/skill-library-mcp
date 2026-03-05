---
name: cloudflare-dns
version: 1.0.0
description: Manage Cloudflare DNS records via API. Use when user asks to list, create, update, or delete DNS records, set up DDNS, manage domains on Cloudflare, or check DNS propagation. Supports A, AAAA, CNAME, TXT, MX, and other record types.
---

# Cloudflare DNS

Manage DNS records via Cloudflare API using the bundled `cf-dns.sh` script.

## Setup

Store credentials in environment or pass via flags:

```bash
export CF_API_TOKEN="your-api-token"
export CF_ZONE_ID="your-zone-id"       # optional, can auto-detect from domain
```

Get API token: Cloudflare Dashboard → My Profile → API Tokens → Create Token → "Edit zone DNS" template.

Get Zone ID: Cloudflare Dashboard → select domain → Overview → right sidebar "Zone ID".

## Usage

The script is at `scripts/cf-dns.sh`. All commands:

```bash
# List zones (find zone ID)
cf-dns.sh zones

# List all records for a zone
cf-dns.sh list <zone_id>
cf-dns.sh list --domain example.com

# Get specific record
cf-dns.sh get <zone_id> <record_id>

# Create record
cf-dns.sh create <zone_id> --type A --name www --content 1.2.3.4 [--ttl 300] [--proxied]
cf-dns.sh create <zone_id> --type CNAME --name blog --content example.com
cf-dns.sh create <zone_id> --type TXT --name @ --content "v=spf1 ..."
cf-dns.sh create <zone_id> --type MX --name @ --content mail.example.com --priority 10

# Update record
cf-dns.sh update <zone_id> <record_id> --content 5.6.7.8 [--ttl 600] [--proxied]

# Delete record
cf-dns.sh delete <zone_id> <record_id>

# DDNS: update A record to current public IP
cf-dns.sh ddns <zone_id> --name home
cf-dns.sh ddns --domain example.com --name home
```

## Common Patterns

**Add subdomain pointing to IP:**
```bash
cf-dns.sh create <zone_id> --type A --name subdomain --content 203.0.113.50 --proxied
```

**Set up email (MX + SPF):**
```bash
cf-dns.sh create <zone_id> --type MX --name @ --content mail.example.com --priority 10
cf-dns.sh create <zone_id> --type TXT --name @ --content "v=spf1 include:_spf.google.com ~all"
```

**Dynamic DNS for home server:**
```bash
# Run periodically via cron
cf-dns.sh ddns --domain example.com --name home
```

## Notes

- `--proxied` enables Cloudflare proxy (orange cloud) — hides origin IP, adds CDN
- TTL in seconds; use 1 for "Auto" when proxied
- `@` means root domain
- Script outputs JSON; pipe to `jq` for parsing
