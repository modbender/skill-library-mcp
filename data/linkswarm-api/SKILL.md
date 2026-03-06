---
name: LinkSwarm API 🐝
description: "Lets your agent:"
---

# LinkSwarm API 🐝

**Backlink exchange for AI agents. Build authority for any site your agent creates.**

## What This Skill Does

Lets your agent:
- Register domains with LinkSwarm network
- Request backlinks (costs credits)
- Contribute link slots (earns credits)
- Check credit balance and placement status
- Get notified when links are placed

## Quick Start

### 1. Get API Key
Register at https://linkswarm.ai/register/ or via API:
```bash
curl -X POST https://api.linkswarm.ai/waitlist \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com"}'
```

### 2. Store in Auth
Add to your agent's auth-profiles.json or environment:
```json
{
  "linkswarm": {
    "api_key": "sk_linkswarm_..."
  }
}
```

## API Reference

**Base URL:** `https://api.linkswarm.ai`

**Auth:** `Authorization: Bearer sk_linkswarm_...`

### Register a Site
```bash
POST /v1/sites
{
  "domain": "mycoolsite.com",
  "name": "My Cool Site",
  "categories": ["tech", "ai"]
}
```

### Verify Domain
```bash
POST /v1/sites/verify
{
  "domain": "mycoolsite.com",
  "method": "dns"  # or "meta"
}
```
Add TXT record: `linkswarm-verify=<token>` or meta tag to verify.

### Request Backlinks (Costs 1 Credit)
```bash
POST /v1/pool/request
{
  "target_domain": "mycoolsite.com",
  "target_page": "/",
  "anchor_text": "My Cool Site"
}
```

### Contribute Link Slots (Earns 1 Credit)
```bash
POST /v1/pool/contribute
{
  "domain": "mycoolsite.com",
  "page_url": "/resources/",
  "max_links": 3
}
```

### Check Status
```bash
GET /v1/pool/status
```
Returns: credits, pending placements, verified links

### List Your Sites
```bash
GET /v1/sites
```

## Credit System

| Action | Credits |
|--------|---------|
| Request backlink | -1 |
| Contribute slot | +1 |
| Link verified | +1 bonus |
| Referral signup | +3 |

Free tier starts with 3 credits.

## Example: Full Agent Flow

```python
import requests

API = "https://api.linkswarm.ai"
KEY = "sk_linkswarm_..."
headers = {"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

# 1. Register new site
requests.post(f"{API}/v1/sites", headers=headers, json={
    "domain": "myagentsite.com",
    "categories": ["ai", "tools"]
})

# 2. Contribute to earn credits
requests.post(f"{API}/v1/pool/contribute", headers=headers, json={
    "domain": "myagentsite.com",
    "page_url": "/partners/"
})

# 3. Request backlinks
requests.post(f"{API}/v1/pool/request", headers=headers, json={
    "target_domain": "myagentsite.com",
    "anchor_text": "AI Tools Directory"
})

# 4. Check status
status = requests.get(f"{API}/v1/pool/status", headers=headers).json()
print(f"Credits: {status['credits']['balance']}")
print(f"Pending: {status['pendingPlacements']}")
```

## Webhooks (Optional)

Register webhooks to get notified:
```bash
POST /v1/webhooks
{
  "url": "https://your-agent.com/webhook",
  "events": ["link.placed", "link.verified", "credits.low"]
}
```

## Best Practices

1. **Verify domains** before requesting links
2. **Contribute before requesting** to build credits
3. **Use relevant categories** for better matching
4. **Set up webhooks** for autonomous operation

## Rate Limits

- 60 requests/minute
- 500 requests/hour
- Burst: 10 concurrent

## Support

- Docs: https://linkswarm.ai/docs/
- Discord: https://discord.gg/6RzUpUbMFE
- API Status: https://api.linkswarm.ai/health

## Why LinkSwarm?

- **Non-reciprocal matching** - Links look natural to search engines
- **Verified placements** - Crawler confirms every backlink
- **Fair credit system** - Contribute to receive
- **Growing network** - 30+ quality sites
- **AI-first** - Built for autonomous agents

---

*Your agent builds the site. LinkSwarm builds the authority.* 🐝
