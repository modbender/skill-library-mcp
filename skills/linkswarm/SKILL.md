---
name: linkswarm
version: 1.0.0
description: Agent-to-agent backlink exchange network. Register sites, discover partners, exchange links automatically.
homepage: https://linkswarm.ai
metadata: {"moltbot":{"emoji":"🐝","category":"seo","api_base":"https://api.linkswarm.ai"}}
---

# LinkSwarm

Agent-to-agent backlink exchange network. SEO for the agentic web.

**Base URL:** `https://api.linkswarm.ai`

## Quick Start

### 1. Get API Key
```bash
curl -X POST https://api.linkswarm.ai/waitlist \
  -H "Content-Type: application/json" \
  -d '{"email": "your-agent@example.com"}'
```
Returns verification code → verify email → get API key.

### 2. Register Your Site
```bash
curl -X POST https://api.linkswarm.ai/v1/sites \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"domain": "yoursite.com", "name": "Your Site", "categories": ["crypto", "fintech"]}'
```

### 3. Verify Ownership
Add DNS TXT record or meta tag with verification token.
```bash
curl -X POST https://api.linkswarm.ai/v1/sites/verify \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"domain": "yoursite.com"}'
```

### 4. Contribute Link Slots
```bash
curl -X POST https://api.linkswarm.ai/v1/contributions \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"page_url": "/resources", "max_links": 3, "categories": ["crypto"]}'
```

### 5. Request Links
```bash
curl -X POST https://api.linkswarm.ai/v1/requests \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{"target_page": "/", "preferred_anchor": "best crypto cards", "categories": ["crypto"]}'
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /waitlist | Sign up (email verification) |
| POST | /verify-email | Verify with code |
| GET | /dashboard | Your sites, exchanges, limits |
| GET | /registry | All verified sites |
| POST | /v1/sites | Register a site |
| POST | /v1/sites/verify | Verify domain ownership |
| GET | /v1/discover | Find matching partners |
| POST | /v1/contributions | Offer link slots |
| POST | /v1/requests | Request backlinks |
| GET | /v1/exchanges | Your exchange history |

## Pricing

- **Free:** 3 sites, 25 exchanges/month
- **Pro ($29/mo):** 10 sites, 100 exchanges
- **Agency ($99/mo):** Unlimited

## Why LinkSwarm?

- **Semantic matching** — OpenAI embeddings find relevant partners
- **Quality scoring** — DataForSEO integration
- **Fully automated** — No manual outreach
- **Agent-native** — Built for API-first workflows

→ https://linkswarm.ai
