# GoDaddy API Reference

Base URL: `https://api.godaddy.com/v1`
Auth: `Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET`

Get credentials: developer.godaddy.com → API Keys → Create New Key
- **OTE (test):** `https://api.ote-godaddy.com/v1` (sandbox)
- **Production:** `https://api.godaddy.com/v1`

---

## Domain Operations

### Check domain availability
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  "https://api.godaddy.com/v1/domains/available?domain=example.com"
```

### Check multiple domains
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  -H "Content-Type: application/json" \
  -X POST "https://api.godaddy.com/v1/domains/available" \
  -d '{"domains":["example.com","example.net","example.org"]}'
```

### List domains in account
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  "https://api.godaddy.com/v1/domains?limit=100"
```

### Get domain details
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  "https://api.godaddy.com/v1/domains/example.com"
```

### Purchase a domain
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  -H "Content-Type: application/json" \
  -X POST "https://api.godaddy.com/v1/domains/purchase" \
  -d '{
    "domain": "example.com",
    "consent": {
      "agreedAt": "2024-01-01T00:00:00Z",
      "agreedBy": "127.0.0.1",
      "agreementKeys": ["DNRA"]
    },
    "period": 1,
    "renewAuto": true
  }'
```
> Note: `agreementKeys` must be fetched first via `/v1/domains/agreements`

### Get purchase agreement keys
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  "https://api.godaddy.com/v1/domains/agreements?tlds=com&privacy=false&forTransfer=false"
```

### Renew domain
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  -H "Content-Type: application/json" \
  -X POST "https://api.godaddy.com/v1/domains/example.com/renew" \
  -d '{"period": 1}'
```

### Update domain (auto-renew, locked, privacy)
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  -H "Content-Type: application/json" \
  -X PATCH "https://api.godaddy.com/v1/domains/example.com" \
  -d '{
    "renewAuto": true,
    "locked": true
  }'
```

### Get auth/EPP code (for transfer out)
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  "https://api.godaddy.com/v1/domains/example.com"
# authCode field in response
```

---

## Nameserver Operations

### Set custom nameservers
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  -H "Content-Type: application/json" \
  -X PUT "https://api.godaddy.com/v1/domains/example.com/nameservers" \
  -d '{"nameservers":["ns1.cloudflare.com","ns2.cloudflare.com"]}'
```

### Reset to GoDaddy default nameservers
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  -H "Content-Type: application/json" \
  -X PUT "https://api.godaddy.com/v1/domains/example.com/nameservers" \
  -d '{"nameservers":["ns73.domaincontrol.com","ns74.domaincontrol.com"]}'
```

---

## DNS Record Operations

> GoDaddy DNS only works when using GoDaddy nameservers.

### List all DNS records
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  "https://api.godaddy.com/v1/domains/example.com/records"
```

### List by type
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  "https://api.godaddy.com/v1/domains/example.com/records/A"
```

### List by type + name
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  "https://api.godaddy.com/v1/domains/example.com/records/A/@"
# "@" = apex
```

### Add DNS records (append — does not replace)
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  -H "Content-Type: application/json" \
  -X PATCH "https://api.godaddy.com/v1/domains/example.com/records" \
  -d '[
    {"type":"A","name":"@","data":"1.2.3.4","ttl":600},
    {"type":"CNAME","name":"www","data":"example.com","ttl":600}
  ]'
```

**Type cheat sheet:**

| Type | name | data | Extra |
|---|---|---|---|
| A | `"@"` or `"www"` | `"1.2.3.4"` | |
| AAAA | `"@"` | `"2001:db8::1"` | |
| CNAME | `"www"` | `"example.com"` | No trailing dot |
| MX | `"@"` | `"mail.example.com"` | Add `"priority":10` |
| TXT | `"@"` | `"v=spf1 ..."` | |
| NS | `"sub"` | `"ns1.example.com"` | |
| SRV | `"_sip._tcp"` | `"0 5 5060 sip.example.com"` | Add `"priority"`, `"weight"`, `"port"` |

### Replace all records of a type + name
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  -H "Content-Type: application/json" \
  -X PUT "https://api.godaddy.com/v1/domains/example.com/records/A/@" \
  -d '[{"type":"A","name":"@","data":"5.6.7.8","ttl":600}]'
```
> ⚠️ PUT replaces ALL records of that type+name. Always confirm what exists first.

### Replace ALL DNS records (full zone replace)
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  -H "Content-Type: application/json" \
  -X PUT "https://api.godaddy.com/v1/domains/example.com/records" \
  -d '[...full record array...]'
```
> ⚠️ Destructive. Confirm before executing.

### Delete records by type + name
```bash
curl -H "Authorization: sso-key $GODADDY_API_KEY:$GODADDY_API_SECRET" \
  -X DELETE "https://api.godaddy.com/v1/domains/example.com/records/TXT/@"
```

---

## Useful Notes

- **`@`** = apex/root in GoDaddy API (not `""` like name.com)
- **No trailing dots** on CNAME/MX data (unlike name.com)
- **PATCH** = append; **PUT** = replace; never confuse them
- **Rate limits:** 60 req/min per key; back off on 429
- **Sandbox (OTE):** Create separate OTE account at developer.godaddy.com for testing
- **DNSSEC:** Managed via UI only, not available in v1 API
- **Forwarding/redirects:** Not available via API — use Cloudflare Workers or a proxy instead
