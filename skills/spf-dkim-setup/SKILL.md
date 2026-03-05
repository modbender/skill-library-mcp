---
name: cloudflare-dns
description: Manage DNS records via the Cloudflare API. Create, list, update, and delete DNS records (A, AAAA, CNAME, TXT, MX, SPF, DKIM). Use when the agent needs to add or modify DNS records, set up email authentication (SPF/DKIM/DMARC), verify domains, or manage any DNS configuration on Cloudflare-hosted domains. Works great with mailtarget-email for fully autonomous sending domain setup.
---

# Cloudflare DNS

Manage DNS records on Cloudflare-hosted domains via the [Cloudflare API](https://developers.cloudflare.com/api/).

## Setup

Set these environment variables:

- `CLOUDFLARE_API_TOKEN` — API token with **DNS Write** permission ([create one](https://dash.cloudflare.com/profile/api-tokens))
- `CLOUDFLARE_ZONE_ID` — Zone ID of the domain (found on the domain overview page in Cloudflare dashboard)

## API Basics

Base URL: `https://api.cloudflare.com/client/v4`

Auth header: `Authorization: Bearer $CLOUDFLARE_API_TOKEN`

All responses follow: `{"success": true, "result": {...}, "errors": [], "messages": []}`

## Common Operations

### List DNS records

```bash
curl -s "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" | jq '.result[] | {id, type, name, content}'
```

Filter by type or name:
```bash
# TXT records only
curl -s "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records?type=TXT" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"

# By name
curl -s "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records?name=example.com" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
```

### Create a DNS record

```bash
curl -X POST "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "TXT",
    "name": "example.com",
    "content": "v=spf1 include:_spf.mailtarget.co ~all",
    "ttl": 3600
  }'
```

### Update a DNS record

```bash
curl -X PATCH "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records/$RECORD_ID" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content": "new-value"}'
```

### Delete a DNS record

```bash
curl -X DELETE "https://api.cloudflare.com/client/v4/zones/$CLOUDFLARE_ZONE_ID/dns_records/$RECORD_ID" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN"
```

## Email Authentication Setup

### SPF record (TXT)

```json
{"type": "TXT", "name": "example.com", "content": "v=spf1 include:_spf.mailtarget.co ~all", "ttl": 3600}
```

If an SPF record already exists, merge the `include:` directive into the existing value.

### DKIM record (TXT)

Use the hostname and value from your email provider:

```json
{"type": "TXT", "name": "selector._domainkey.example.com", "content": "v=DKIM1; k=rsa; p=MIGf...", "ttl": 3600}
```

### DMARC record (TXT)

```json
{"type": "TXT", "name": "_dmarc.example.com", "content": "v=DMARC1; p=quarantine; rua=mailto:dmarc@example.com", "ttl": 3600}
```

### CNAME record (for tracking domains)

```json
{"type": "CNAME", "name": "track.example.com", "content": "tracking.mailtarget.co", "ttl": 3600, "proxied": false}
```

**Important:** Set `proxied: false` for email-related CNAME records (DKIM, tracking) — Cloudflare proxy breaks email authentication.

## Mailtarget Integration Workflow

When used together with `mailtarget-email`, the agent can do end-to-end domain setup:

1. **Create sending domain** in Mailtarget → `POST /domain/sending`
2. **Read required DNS records** → `GET /domain/sending/{id}` returns SPF, DKIM, CNAME values
3. **Add DNS records** in Cloudflare using this skill
4. **Verify domain** in Mailtarget → `PUT /domain/sending/{id}/verify-txt`
5. **Confirm** all records are verified

Zero manual DNS editing required.

## Reference

See [references/api.md](references/api.md) for full endpoint documentation.
