---
description: Perform DNS lookups, check record types, and verify propagation across DNS servers.
---

# DNS Lookup

Query and analyze DNS records for any domain.

## Instructions

1. **Full record lookup**:
   ```bash
   dig example.com ANY +noall +answer
   ```

2. **Specific record types**:
   ```bash
   dig example.com A +short        # IPv4
   dig example.com AAAA +short     # IPv6
   dig example.com MX +short       # Mail
   dig example.com TXT +short      # TXT (SPF, DKIM, etc.)
   dig example.com CNAME +short    # Alias
   dig example.com NS +short       # Nameservers
   dig example.com SOA +short      # Authority
   ```

3. **Propagation check** (query multiple DNS servers):
   ```bash
   for dns in 8.8.8.8 1.1.1.1 9.9.9.9 208.67.222.222; do
     echo "$dns: $(dig @$dns example.com A +short)"
   done
   ```

4. **Reverse DNS**:
   ```bash
   dig -x 8.8.8.8 +short
   ```

5. **Report format**:
   ```
   🌐 DNS Report — example.com

   | Type  | Value | TTL |
   |-------|-------|-----|
   | A     | 93.184.216.34 | 3600 |
   | AAAA  | 2606:2800:220:1:... | 3600 |
   | MX    | 10 mail.example.com | 3600 |
   | NS    | ns1.example.com | 86400 |

   ## Propagation (A record)
   | DNS Server | Provider | Result | Match |
   |-----------|----------|--------|-------|
   | 8.8.8.8   | Google   | 93.184.216.34 | ✅ |
   | 1.1.1.1   | Cloudflare | 93.184.216.34 | ✅ |
   ```

## Edge Cases

- **NXDOMAIN**: Domain doesn't exist — check for typos
- **SERVFAIL**: DNS server error — try alternate resolvers
- **Low TTL during migration**: Note that propagation may take up to TTL seconds
- **Wildcard records**: `*.example.com` — query specific subdomain to verify
- **DNSSEC**: Check with `dig +dnssec` if security validation needed

## Requirements

- `dig` (from `dnsutils` / `bind-utils`) or `nslookup`
- Optional: `whois` for domain registration info
- No API keys needed
