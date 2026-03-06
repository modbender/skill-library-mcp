---
name: domainion-ops
description: >
  Domain and DNS operations across name.com (default), GoDaddy, and Namecheap. Use for
  registering domains, flipping nameservers, managing DNS records (A, AAAA, CNAME, MX, TXT, NS, SRV),
  setting up redirects, checking domain availability, renewals, transfers, and verifying DNS propagation.
  Default provider is name.com unless the user selects GoDaddy or Namecheap. Triggers on: "register domain",
  "add DNS record", "change nameservers", "check domain availability", "transfer domain", "renew domain",
  "set up redirect", "DNS propagation check", "update MX record", "point domain to".
---

# Domainion Ops

Multi-provider domain and DNS management. Default provider: **name.com**.

## Provider Selection

| Provider | When to use | Reference |
|---|---|---|
| **name.com** (default) | Unless user specifies otherwise | `references/name-com.md` |
| **GoDaddy** | User says "GoDaddy" or has GoDaddy account | `references/godaddy.md` |
| **Namecheap** | User says "Namecheap" or has Namecheap account | `references/namecheap.md` |

Read only the relevant provider reference. Do not load all three.

## Credentials Setup

Before any operation, verify credentials exist. Store in env or `~/.domainion`:

```bash
# name.com (default)
NAMECOM_USERNAME=your_username
NAMECOM_TOKEN=your_api_token      # name.com > Account > API Settings

# GoDaddy
GODADDY_API_KEY=your_key
GODADDY_API_SECRET=your_secret   # developer.godaddy.com > API Keys

# Namecheap
NAMECHEAP_USERNAME=your_username
NAMECHEAP_API_KEY=your_api_key   # namecheap.com > Profile > Tools > API Access
NAMECHEAP_CLIENT_IP=your_ip      # Your whitelisted IP
```

If credentials are missing, prompt the user for the relevant provider's creds before proceeding.

## Common Workflows

### 1. Check domain availability
```bash
# name.com (default)
curl -u "$NAMECOM_USERNAME:$NAMECOM_TOKEN" \
  "https://api.name.com/v4/domains:checkAvailability" \
  -d '{"domainNames":["example.com"]}'
```
→ See provider reference for GoDaddy / Namecheap equivalents.

### 2. DNS record management (add/update/delete)
Load provider reference for exact API calls. General pattern:
- **List** records first to confirm state
- **Add** or **Update** with idempotency check (avoid duplicates)
- **Verify** with `dig` after change

### 3. Nameserver change
Always confirm registrar before changing NS. Wrong registrar = silent failure.
Load provider reference for exact API call.

### 4. Verify DNS propagation
```bash
# Primary check (Cloudflare resolver — fast TTL)
dig +short example.com @1.1.1.1

# Authoritative check
dig +short example.com @8.8.8.8

# Full record check
dig example.com ANY +noall +answer

# HTTP redirect verify
curl -sI https://example.com | grep -i location
```

### 5. TTL Strategy
- Lowering TTL before a change: set to 300 (5 min) at least 1 TTL cycle before
- After change confirmed: restore to 3600 or higher
- Never lower TTL after making the change — too late

## Guardrails

- Confirm domain + provider before any destructive action (NS change, record delete)
- List existing records before adding to avoid duplicates
- Prefer reversible steps; verify after each change
- Never expose API tokens/secrets in output
- For MX changes: always keep at least one valid MX record live during migration
