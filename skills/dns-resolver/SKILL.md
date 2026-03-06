---
name: dns-resolver
description: Perform detailed DNS lookups, check record types, and verify DNS
  propagation across multiple servers.
---


# DNS Lookup

Query and analyze DNS records for any domain.

## Capabilities

- **Record Lookup**: Query A, AAAA, MX, TXT, CNAME, NS, SOA, PTR records
- **Propagation Check**: Query multiple public DNS servers to verify propagation
- **Reverse DNS**: Look up PTR records for IP addresses
- **WHOIS**: Basic domain registration info

## Usage

Ask the agent to:
- "Look up DNS records for example.com"
- "Check MX records for gmail.com"
- "Has DNS propagated for newsite.com?"
- "Reverse DNS lookup for 8.8.8.8"

## How It Works

Uses `dig`, `nslookup`, and `whois`:

```bash
dig example.com ANY +noall +answer
dig @8.8.8.8 example.com A
dig @1.1.1.1 example.com A
dig -x 8.8.8.8
```

## Requirements

- `dig` or `nslookup` (from `dnsutils`/`bind-utils`)
- Optional: `whois`
- No API keys needed
