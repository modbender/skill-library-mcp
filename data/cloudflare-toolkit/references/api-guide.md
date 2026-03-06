# Cloudflare API Quick Reference

## Authentication

All API calls use Bearer token auth. Create tokens at:
https://dash.cloudflare.com/profile/api-tokens

### Recommended token templates:
- **DNS management:** Zone:DNS:Edit + Zone:Zone:Read
- **Full zone management:** Zone:DNS:Edit + Zone:Zone:Read + Zone:Zone Settings:Edit
- **Tunnel management:** Account:Cloudflare Tunnel:Edit + Zone:DNS:Edit
- **Read-only audit:** Zone:Zone:Read + Zone:DNS:Read + Zone:Analytics:Read

## Zone IDs

Every domain (zone) has a unique zone ID. Use `cf zones` to list all zones and their IDs.

## Common DNS record types

| Type | Use case | Example content |
|------|----------|-----------------|
| A | IPv4 address | `192.0.2.1` |
| AAAA | IPv6 address | `2001:db8::1` |
| CNAME | Alias to another domain | `example.com` |
| MX | Mail server | `mail.example.com` (+ priority) |
| TXT | Verification, SPF, DKIM | `v=spf1 include:...` |
| NS | Nameserver delegation | `ns1.example.com` |
| SRV | Service discovery | `target:port:weight:priority` |

## Proxied vs DNS-only

- **Proxied (orange cloud):** Traffic routes through Cloudflare — enables CDN, WAF, DDoS protection
- **DNS-only (grey cloud):** Direct DNS resolution, no Cloudflare proxy features
- Use proxied for HTTP/HTTPS services
- Use DNS-only for MX, non-HTTP services, or when you need direct IP access

## SSL modes

| Mode | Description |
|------|-------------|
| `off` | No SSL |
| `flexible` | SSL between browser and Cloudflare only (origin is HTTP) |
| `full` | SSL end-to-end, but origin cert not validated |
| `strict` | SSL end-to-end, origin cert must be valid (recommended) |

## TTL

- `1` = automatic (Cloudflare managed, typically 300s for proxied records)
- For DNS-only records: set explicit TTL in seconds (e.g., 3600 = 1 hour)

## Rate limits

Cloudflare API: 1200 requests per 5 minutes per user. The `cf` script uses single calls per operation, so this is rarely an issue.
