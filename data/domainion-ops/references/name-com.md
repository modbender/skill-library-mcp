# name.com API Reference

Base URL: `https://api.name.com/v4`
Auth: HTTP Basic — `$NAMECOM_USERNAME:$NAMECOM_TOKEN`

Get token: name.com → My Account → API Settings → Generate Token

---

## Domain Operations

### Check availability
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  -X POST "https://api.name.com/v4/domains:checkAvailability" \
  -H "Content-Type: application/json" \
  -d '{"domainNames":["example.com","example.net"]}'
```

### Register a domain
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  -X POST "https://api.name.com/v4/domains" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": {
      "domainName": "example.com",
      "nameservers": ["ns1.name.com","ns2.name.com","ns3.name.com","ns4.name.com"]
    },
    "purchasePrice": 10.99,
    "years": 1
  }'
```

### List domains
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  "https://api.name.com/v4/domains"
```

### Get domain details
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  "https://api.name.com/v4/domains/example.com"
```

### Renew domain
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  -X POST "https://api.name.com/v4/domains/example.com:renew" \
  -H "Content-Type: application/json" \
  -d '{"purchasePrice": 10.99, "years": 1}'
```

### Enable/disable auto-renew
```bash
# Enable
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  -X POST "https://api.name.com/v4/domains/example.com:enableAutorenew"

# Disable
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  -X POST "https://api.name.com/v4/domains/example.com:disableAutorenew"
```

### Enable/disable domain lock (transfer lock)
```bash
# Lock (recommended default)
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  -X POST "https://api.name.com/v4/domains/example.com:lock"

# Unlock (before transfer)
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  -X POST "https://api.name.com/v4/domains/example.com:unlock"
```

### Get auth code (for transfer out)
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  "https://api.name.com/v4/domains/example.com:getAuthCode"
```

---

## Nameserver Operations

### Set custom nameservers
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  -X POST "https://api.name.com/v4/domains/example.com:setNameservers" \
  -H "Content-Type: application/json" \
  -d '{"nameservers":["ns1.cloudflare.com","ns2.cloudflare.com"]}'
```

### Reset to name.com default nameservers
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  -X POST "https://api.name.com/v4/domains/example.com:setNameservers" \
  -H "Content-Type: application/json" \
  -d '{"nameservers":["ns1.name.com","ns2.name.com","ns3.name.com","ns4.name.com"]}'
```

---

## DNS Record Operations

> Only works when nameservers point to name.com. If custom NS (e.g. Cloudflare), manage DNS there.

### List DNS records
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  "https://api.name.com/v4/domains/example.com/records"
```

### Create a DNS record
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  -X POST "https://api.name.com/v4/domains/example.com/records" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "",
    "type": "A",
    "answer": "1.2.3.4",
    "ttl": 300
  }'
```

**Type examples:**

| Type | host | answer | Notes |
|---|---|---|---|
| A | `""` or `"www"` | `1.2.3.4` | IPv4 |
| AAAA | `""` or `"www"` | `2001:db8::1` | IPv6 |
| CNAME | `"www"` | `example.com.` | Trailing dot required |
| MX | `""` | `mail.example.com.` | Add `priority` field |
| TXT | `""` | `"v=spf1 include:... ~all"` | Wrap in double quotes |
| NS | `"sub"` | `ns1.example.com.` | Subdomain delegation |

### MX record (add priority)
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  -X POST "https://api.name.com/v4/domains/example.com/records" \
  -H "Content-Type: application/json" \
  -d '{"host":"","type":"MX","answer":"mail.example.com.","ttl":300,"priority":10}'
```

### Update a DNS record (by ID)
```bash
# First: get record ID from list records
RECORD_ID=12345

curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  -X PUT "https://api.name.com/v4/domains/example.com/records/$RECORD_ID" \
  -H "Content-Type: application/json" \
  -d '{"host":"","type":"A","answer":"5.6.7.8","ttl":300}'
```

### Delete a DNS record (by ID)
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  -X DELETE "https://api.name.com/v4/domains/example.com/records/$RECORD_ID"
```

---

## URL Forwarding (Redirects)

name.com supports URL forwarding via the API:

### List forwards
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  "https://api.name.com/v4/domains/example.com/url/forwards"
```

### Create a forward
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  -X POST "https://api.name.com/v4/domains/example.com/url/forwards" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "",
    "forwardTo": "https://target.com",
    "type": "Permanent",
    "masking": false,
    "meta": false
  }'
```
- `type`: `"Permanent"` (301) or `"Temporary"` (302)
- `host`: `""` for apex, `"www"` for subdomain

### Delete a forward (by ID)
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  -X DELETE "https://api.name.com/v4/domains/example.com/url/forwards/$FORWARD_ID"
```

---

## DNSSEC

### Enable DNSSEC (if using name.com NS)
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  -X POST "https://api.name.com/v4/domains/example.com/dnssec:enable"
```

### List DNSSEC records
```bash
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  "https://api.name.com/v4/domains/example.com/dnssec"
```

---

## Useful Notes

- **Sandbox API:** `https://api.dev.name.com/v4` — use for testing (requires separate dev account)
- **Rate limits:** Not officially published; back off on 429 responses
- **Trailing dots:** CNAME, MX, NS answers must end with `.` (FQDN format)
- **Apex CNAME:** Not supported — use A/AAAA for apex records
- **TTL minimum:** 300 seconds
