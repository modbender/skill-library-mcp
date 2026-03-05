---
name: cloudflare
description: Manage Cloudflare domains, DNS records, SSL settings, zone configuration, firewall rules, tunnels, and analytics via the Cloudflare API. Use when the user asks to set up a domain, add/edit/delete DNS records, configure SSL, check zone settings, manage Cloudflare Tunnels, view analytics, or any Cloudflare account management task.
metadata: {"openclaw":{"primaryEnv":"CLOUDFLARE_API_TOKEN","requires":{"env":["CLOUDFLARE_API_TOKEN"],"bins":["curl","jq","openssl"]}}}
---

# Cloudflare

Manage Cloudflare zones, DNS, SSL, tunnels, and settings via the bundled `scripts/cf.sh` bash script.

## Prerequisites

- `curl`, `jq`, and `openssl` must be available on the system
- Set `CLOUDFLARE_API_TOKEN` environment variable
- Optionally set `CLOUDFLARE_ACCOUNT_ID` for tunnel operations

## CLI: `scripts/cf.sh`

All operations go through the bundled `scripts/cf.sh` bash script (included in this skill). No external downloads needed.

```bash
# Run from skill directory
./scripts/cf.sh <command> [args...]
# Or reference by absolute path
/path/to/skills/cloudflare/scripts/cf.sh <command> [args...]
```

### Commands

| Command | Args | Description |
|---------|------|-------------|
| `help` | | Show all commands |
| `verify` | | Verify API token is valid |
| `zones` | `[domain]` | List zones (optionally filter by domain name) |
| `zone-get` | `<zone_id>` | Get zone details |
| `zone-id` | `<domain>` | Get zone ID from domain name |
| `dns-list` | `<zone_id> [type] [name]` | List DNS records |
| `dns-create` | `<zone_id> <type> <name> <content> [proxied] [ttl]` | Create DNS record |
| `dns-update` | `<zone_id> <record_id> <type> <name> <content> [proxied] [ttl]` | Update DNS record |
| `dns-delete` | `<zone_id> <record_id>` | Delete DNS record |
| `dns-export` | `<zone_id>` | Export all records as JSON |
| `dns-import` | `<zone_id> <file.json>` | Import records from JSON |
| `settings-list` | `<zone_id>` | List all zone settings |
| `setting-get` | `<zone_id> <setting>` | Get specific setting |
| `setting-set` | `<zone_id> <setting> <value>` | Update a setting |
| `ssl-get` | `<zone_id>` | Get current SSL mode |
| `ssl-set` | `<zone_id> <mode>` | Set SSL mode (off/flexible/full/strict) |
| `cache-purge` | `<zone_id> [url1 url2 ...]` | Purge specific URLs or everything |
| `pagerules-list` | `<zone_id>` | List page rules |
| `firewall-list` | `<zone_id>` | List firewall rules |
| `tunnels-list` | | List Cloudflare Tunnels (needs ACCOUNT_ID) |
| `tunnel-get` | `<tunnel_id>` | Get tunnel details |
| `tunnel-create` | `<name>` | Create a tunnel (needs ACCOUNT_ID) |
| `tunnel-delete` | `<tunnel_id>` | Delete a tunnel (needs ACCOUNT_ID) |
| `analytics` | `<zone_id> [since_minutes]` | Zone analytics (default: last 24h) |

### Proxied flag

- `true` — orange cloud, traffic through Cloudflare (CDN, WAF, DDoS)
- `false` — grey cloud, DNS-only (use for MX, non-HTTP services)

### TTL

- `1` = automatic (Cloudflare-managed)
- Set explicit seconds for DNS-only records (e.g., `3600`)

## Typical workflows

### Point domain to server
```bash
# Find zone ID
cf zones example.com
# Create A record (proxied)
cf dns-create <zone_id> A example.com 1.2.3.4 true
# Create www CNAME
cf dns-create <zone_id> CNAME www.example.com example.com true
```

### Set up email (MX + SPF)
```bash
cf dns-create <zone_id> MX example.com "mx.provider.com" false 1
cf dns-create <zone_id> TXT example.com "v=spf1 include:provider.com ~all" false
```

### Enable strict SSL
```bash
cf ssl-set <zone_id> strict
```

## Safety rules

**Always confirm with the user before:**
- Deleting DNS records (`dns-delete`)
- Changing SSL mode
- Modifying firewall rules
- Any destructive operation

**Safe to do freely:**
- Listing/reading zones, records, settings, analytics
- Verifying token

## Reference

For DNS record types, SSL modes, and API details: see `references/api-guide.md`
