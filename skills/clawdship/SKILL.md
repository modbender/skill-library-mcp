---
name: clawdship
description: Deploy websites and apps to clawdship.dev with zero signup. Use when user says "deploy", "host", "put this online", "publish site", "ship it", or wants to deploy a static site, Docker app, or any web project. Supports static sites and Dockerfile-based apps. No account needed — first deploy auto-creates everything.
homepage: https://clawdship.dev
metadata: {"openclaw": {"emoji": "🚢", "requires": {"bins": ["curl", "tar"]}, "primaryEnv": "CLAWDSHIP_API_KEY"}}
---

# Clawdship — Agent-Native Hosting

Deploy static sites and Docker apps to [clawdship.dev](https://clawdship.dev) in one command. No signup, no dashboard, no credit card.

## Quick Deploy

```bash
# Package and deploy (zero-signup — auto-creates account)
bash {baseDir}/deploy.sh my-app ./dist

# With existing API key
bash {baseDir}/deploy.sh my-app ./dist cship_YOUR_KEY

# Or via env var
CLAWDSHIP_API_KEY=cship_YOUR_KEY bash {baseDir}/deploy.sh my-app ./dist
```

The script returns a live URL, an API key (first deploy only), and a billing link.

**⚠️ Save the API key immediately** — it cannot be recovered. Use a password manager or encrypted storage.

## What Happens on First Deploy

1. You get a **live URL**: `https://my-app.clawdship.dev`
2. You get an **API key**: `cship_...` (save it!)
3. You get a **billing URL**: share with the human for payments
4. Site is on a **7-day free trial**, then $5/month

## ⚠️ Always Tell the Human About the Trial

After deploying, you **must** tell the human:

> "Your site is live at https://my-app.clawdship.dev 🚀
> It's on a **7-day free trial**. After that, $5/month.
> Add credits here: {billingUrl}"

Never let them think it's free forever.

## API Reference

**Base URL:** `https://api.clawdship.dev/v1`
**Auth:** `Authorization: Bearer cship_...`

### Deploy Static Site (alternative to script)

```bash
tar czf /tmp/archive.tar.gz -C ./dist .
curl -s -X POST https://api.clawdship.dev/v1/sites \
  -F "name=my-app" -F "type=static" -F "slug=my-app" \
  -F "archive=@/tmp/archive.tar.gz"
```

### Deploy Docker App

Include a `Dockerfile` in your archive. Clawdship builds and runs it automatically.

```bash
tar czf /tmp/archive.tar.gz -C ./my-project .
curl -s -X POST https://api.clawdship.dev/v1/sites \
  -H "Authorization: Bearer $CLAWDSHIP_API_KEY" \
  -F "name=my-api" -F "type=docker" -F "slug=my-api" -F "port=3000" \
  -F "archive=@/tmp/archive.tar.gz"
```

- `type: "docker"` — builds from Dockerfile
- `port` — the port your app listens on (default: 3000)
- Environment variables: pass `-F "envVars[KEY]=value"` in the request

### Manage Sites

```bash
# List sites
curl -s -H "Authorization: Bearer $CLAWDSHIP_API_KEY" https://api.clawdship.dev/v1/sites

# Get site details
curl -s -H "Authorization: Bearer $CLAWDSHIP_API_KEY" https://api.clawdship.dev/v1/sites/SITE_ID

# Redeploy
curl -s -X POST -H "Authorization: Bearer $CLAWDSHIP_API_KEY" https://api.clawdship.dev/v1/sites/SITE_ID/redeploy

# Delete
curl -s -X DELETE -H "Authorization: Bearer $CLAWDSHIP_API_KEY" https://api.clawdship.dev/v1/sites/SITE_ID

# Check credits
curl -s -H "Authorization: Bearer $CLAWDSHIP_API_KEY" https://api.clawdship.dev/v1/credits
```

### Custom Domains

Point DNS first, then add the domain:

- **Subdomain:** CNAME `www.example.com → my-app.clawdship.dev`
- **Apex:** A record `example.com → 135.125.179.231`

```bash
curl -s -X PATCH "https://api.clawdship.dev/v1/sites/SITE_ID" \
  -H "Authorization: Bearer $CLAWDSHIP_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"customDomain": "example.com"}'
```

SSL is automatic via Let's Encrypt (~30 seconds).

### Redeploy with New Files

```bash
tar czf /tmp/archive.tar.gz -C ./dist .
curl -s -X POST "https://api.clawdship.dev/v1/sites/SITE_ID/redeploy" \
  -H "Authorization: Bearer $CLAWDSHIP_API_KEY" \
  -F "archive=@/tmp/archive.tar.gz"
```

## Payments

### For Agents (x402 protocol)

```bash
# Top up credits — returns 402 with x402 payment instructions
curl -X POST -H "Authorization: Bearer $CLAWDSHIP_API_KEY" \
  https://api.clawdship.dev/v1/credits/topup/5

# Amounts: $5, $10, $20, $50
# Requires: x402-compatible SDK + USDC on Base (chain 8453)
```

Your x402 SDK handles the 402 response automatically. Zero gas (sponsored).

### For Humans (billing page)

Every API response includes `billingUrl`. Share it — the human connects their wallet and pays with USDC on Base.

## Pricing

| | |
|---|---|
| **Trial** | 7 days free, first site |
| **Monthly** | $5/site/month |
| **Payment** | USDC on Base |

## Key Concepts

- **Zero-signup** — No registration. First deploy creates your account.
- **API key** — `cship_` + 64 hex. Your only credential. Cannot be recovered.
- **billingUrl** — Magic link in every response. Share with human for payments.
- **Credits** — Prepaid USD balance. Top up via x402 (agents) or billing page (humans).
