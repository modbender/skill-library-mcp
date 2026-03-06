---
name: porkbun
description: Manage Porkbun DNS records and domains via API v3. Use when Codex needs to create, read, update, or delete DNS records on Porkbun; list domains; configure API access; work with common record types (A, AAAA, CNAME, MX, TXT, etc.). The skill includes a CLI tool `scripts/porkbun-dns.js` for executing DNS operations reliably.
---

# Porkbun DNS Management

Manage DNS records and domains on Porkbun via their REST API v3.

## Quick Start

### Set up API credentials

1. Generate API keys: https://porkbun.com/account/api
2. Save credentials to config file: `~/.config/porkbun/config.json`
```json
{
  "apiKey": "your-api-key",
  "secretApiKey": "your-secret-api-key"
}
```

Or set environment variables:
```bash
export PORKBUN_API_KEY="your-api-key"
export PORKBUN_SECRET_API_KEY="your-secret-api-key"
```

3. Enable API access for each domain: Domain Management → Details → API Access → Enable

### Test connection

```bash
node ~/.openclaw/workspace/skills/public/porkbun/scripts/porkbun-dns.js ping
```

## Using the CLI Tool

The `scripts/porkbun-dns.js` script provides a reliable, deterministic way to execute DNS operations. Use it directly for common tasks instead of writing custom code.

### Common Operations

#### List domains
```bash
node scripts/porkbun-dns.js list
```

#### List DNS records
```bash
node scripts/porkbun-dns.js records example.com
```

#### Create records
```bash
# A record
node scripts/porkbun-dns.js create example.com type=A name=www content=1.1.1.1 ttl=600

# CNAME
node scripts/porkbun-dns.js create example.com type=CNAME name=docs content=example.com

# MX record
node scripts/porkbun-dns.js create example.com type=MX name= content="mail.example.com" prio=10

# TXT record ( SPF for email)
node scripts/porkbun-dns.js create example.com type=TXT name= content="v=spf1 include:_spf.google.com ~all"
```

#### Edit records
```bash
# By ID (get ID from records command)
node scripts/porkbun-dns.js edit example.com 123456 content=2.2.2.2

# By type and subdomain (updates all matching records)
node scripts/porkbun-dns.js edit-by example.com A www content=2.2.2.2
```

#### Delete records
```bash
# By ID
node scripts/porkbun-dns.js delete example.com 123456

# By type and subdomain
node scripts/porkbun-dns.js delete-by example.com A www
```

#### Get specific records
```bash
# All records
node scripts/porkbun-dns.js get example.com

# Filter by type
node scripts/porkbun-dns.js get example.com A

# Filter by type and subdomain
node scripts/porkbun-dns.js get example.com A www
```

## Record Types

Supported record types: A, AAAA, CNAME, ALIAS, TXT, NS, MX, SRV, TLSA, CAA, HTTPS, SVCB, SSHFP

For detailed field requirements and examples, see [references/dns-record-types.md](references/dns-record-types.md).

## Common Patterns

### Website Setup

Create root A record and www CNAME:
```bash
node scripts/porkbun-dns.js create example.com type=A name= content=192.0.2.1
node scripts/porkbun-dns.js create example.com type=CNAME name=www content=example.com
```

### Email Configuration

Set up MX records for Google Workspace:
```bash
node scripts/porkbun-dns.js create example.com type=MX name= content="aspmx.l.google.com" prio=1
node scripts/porkbun-dns.js create example.com type=MX name= content="alt1.aspmx.l.google.com" prio=5
node scripts/porkbun-dns.js create example.com type=MX name= content="alt2.aspmx.l.google.com" prio=5
node scripts/porkbun-dns.js create example.com type=MX name= content="alt3.aspmx.l.google.com" prio=10
node scripts/porkbun-dns.js create example.com type=MX name= content="alt4.aspmx.l.google.com" prio=10
```

Add SPF record:
```bash
node scripts/porkbun-dns.js create example.com type=TXT name= content="v=spf1 include:_spf.google.com ~all"
```

### Dynamic DNS

Update home IP address (can be scripted/automated):
```bash
HOME_IP=$(curl -s ifconfig.me)
node scripts/porkbun-dns.js edit-by example.com A home content=$HOME_IP
```

### Wildcard DNS

Create a wildcard record pointing to root:
```bash
node scripts/porkbun-dns.js create example.com type=A name=* content=192.0.2.1
```

## Reference Documentation

- **[references/dns-record-types.md](references/dns-record-types.md)** - Detailed reference for all DNS record types and field requirements
- **[https://porkbun.com/api/json/v3/documentation](https://porkbun.com/api/json/v3/documentation)** - Full API documentation

## Troubleshooting

### "API key not found"
- Verify config file exists at `~/.config/porkbun/config.json`
- Check environment variables: `echo $PORKBUN_API_KEY`
- Ensure API access is enabled for the specific domain

### "Invalid type passed"
- Record types must be uppercase (e.g., `A`, not `a`)
- See supported types list above

### HTTP errors
- Verify API keys are valid at https://porkbun.com/account/api
- Check network connectivity
- Confirm API endpoint is `api.porkbun.com` (not `porkbun.com`)

### TTL errors
- Minimum TTL is 600 seconds (10 minutes)
- Default TTL is 600 seconds
- Common values: 300 (dynamic), 3600 (standard), 86400 (stable)

## Notes

- TTL minimum is 600 seconds
- Use "@" for root domain records
- Use "*" for wildcard records
- TXT records with spaces need quotes
- Multiple MX records allowed with different priorities
- API v3 current hostname: `api.porkbun.com`