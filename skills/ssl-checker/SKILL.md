---
description: Check SSL/TLS certificate expiry, validity, chain, and configuration for any domain.
---

# SSL Checker

Inspect SSL/TLS certificates — expiry dates, issuer details, chain validation, and bulk checks.

## Requirements

- `openssl` (pre-installed on most systems)
- No API keys needed

## Instructions

### Single domain check
```bash
echo | openssl s_client -servername example.com -connect example.com:443 2>/dev/null | openssl x509 -noout -dates -subject -issuer -ext subjectAltName
```

### Extract specific fields
```bash
# Expiry date only
echo | openssl s_client -servername example.com -connect example.com:443 2>/dev/null | openssl x509 -noout -enddate

# Days until expiry
echo | openssl s_client -servername example.com -connect example.com:443 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2 | xargs -I{} bash -c 'echo $(( ($(date -d "{}" +%s) - $(date +%s)) / 86400 )) days'

# Full certificate chain
echo | openssl s_client -servername example.com -connect example.com:443 -showcerts 2>/dev/null
```

### Bulk check (multiple domains)
```bash
for domain in example.com google.com github.com; do
  expiry=$(echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
  echo "$domain: $expiry"
done
```

### Output format
```
## 🔒 SSL Certificate Report — <timestamp>

| Domain | Status | Expires | Days Left | Issuer |
|--------|--------|---------|-----------|--------|
| example.com | 🟢 Valid | 2025-06-15 | 128 | Let's Encrypt |
| expired.com | 🔴 Expired | 2024-12-01 | -39 | DigiCert |
| soon.com | 🟡 Expiring | 2025-02-20 | 12 | Comodo |

**Thresholds**: 🟢 > 30 days | 🟡 ≤ 30 days | 🔴 Expired or ≤ 7 days
```

## Edge Cases

- **Non-standard port**: Support `domain:8443` syntax for custom ports.
- **Connection refused**: Host may not serve HTTPS. Report clearly, don't hang.
- **Self-signed certs**: `openssl` will show verify errors — report but still extract cert details.
- **SNI required**: Always pass `-servername` flag (some servers serve different certs per hostname).
- **Timeout**: Add `-connect` timeout: `timeout 5 openssl s_client ...`
- **Wildcard certs**: Note when SAN contains `*.domain.com`.

## Security

- Only connects to port 443 (or user-specified port) — read-only inspection.
- No credentials or sensitive data involved.
- Validate domain input: alphanumeric, hyphens, dots only.
