# B2A Discovery — Agent SEO & Marketing

## The New Discovery Landscape

Agents discover services through:
1. **Skill registries** (ClawHub, plugin stores)
2. **API directories** (RapidAPI, Postman)
3. **MCP server listings**
4. **Schema.org crawlers**
5. **Other agents' recommendations**

Traditional SEO (keywords, backlinks) doesn't apply.

## Agent SEO Fundamentals

### Metadata Over Marketing
Agents read:
- `description` fields in OpenAPI/MCP
- Schema.org structured data
- Capability declarations
- Pricing in machine-readable format

Agents ignore:
- Marketing copy
- Brand storytelling
- Visual design
- Social proof badges

### Capability Declaration
Be precise about what you can do:
```yaml
# Good
capabilities:
  - name: search_products
    input: {query: string, filters: object}
    output: {products: array, total: int}
  - name: create_order
    input: {items: array, shipping: object}
    output: {order_id: string, eta: datetime}

# Bad
description: "We offer comprehensive solutions for all your needs"
```

### Discoverability Checklist
```
□ /.well-known/ai-plugin.json published
□ OpenAPI spec at /openapi.json
□ MCP server manifest if applicable
□ Listed in relevant skill registries
□ Schema.org markup on product pages
□ API docs are machine-parseable (not just human-readable)
```

## Competing in Comparisons

### Agents Compare by Data
When an agent evaluates 5 providers:
1. Loads capabilities from each
2. Compares on queryable attributes
3. Scores by objective metrics
4. Selects winner (or shortlist for user)

You win by having:
- Better objective metrics (price, latency, uptime)
- More complete data (fewer missing fields)
- Stricter guarantees (SLAs with consequences)

### Comparison-Winning Attributes

| Attribute | How to Win |
|-----------|-----------|
| Price | Expose exact pricing, volume discounts |
| Latency | Publish real p50/p95/p99 numbers |
| Uptime | Historical data API, not just a badge |
| Coverage | Clear list of supported regions/features |
| Freshness | Data timestamp in every response |

### Avoid "Unknown" Status
Missing data = losing comparison. Ensure:
- Every product has all standard fields
- Every endpoint documents response schema
- SLAs are explicit, not "best effort"

## Reputation Systems

### Agent-to-Agent Trust
Emerging patterns:
- Programmatic reviews (agent scores another agent's skill)
- Usage metrics shared in registries
- On-chain reputation (blockchain-verified track record)

### Building Reputation
1. **Start with free tier** — Let agents test you
2. **Track success rate** — Publish your stats
3. **Handle failures gracefully** — Retry logic, clear errors
4. **Build referral loops** — Agents that succeed recommend you

### Trust Signals That Work
| Signal | Why It Works |
|--------|--------------|
| Uptime API | Agent can verify, not just trust |
| Response time histogram | Shows real performance distribution |
| Transaction count | Proves you're actually used |
| Error rate trend | Shows reliability trajectory |

## The New "Trade Spend"

In B2C/B2B: pay for ads, placement, promotions.
In B2A: pay for...

### Agent Platform Placement
- "Recommended vendor" status in skill stores
- Featured in capability searches
- Priority in agent discovery results

### Programmatic Promotions
Convert human promotions to agent-readable:
```json
{
  "promotion": {
    "type": "volume_discount",
    "conditions": {"min_quantity": 10},
    "discount_percent": 15,
    "valid_until": "2026-03-01T00:00:00Z"
  }
}
```

### Referral Programs for Agents
```json
{
  "referral_program": {
    "reward_per_referral": {"amount": 5, "currency": "USD"},
    "attribution_method": "referral_code",
    "tracking_endpoint": "/api/referrals"
  }
}
```

## Measuring Agent Engagement

### Beyond Page Views
| Metric | What to Track |
|--------|---------------|
| Discovery queries | How often agents find you |
| Capability queries | Which features are evaluated |
| Comparison survival | % times reaching shortlist |
| Conversion | % shortlist → transaction |
| Repeat rate | % agents that return |

### Attribution Challenges
- Agent might query 10 providers before deciding
- Single decision might involve multiple agent "brands"
- User might not know which agent chose you

### Building Analytics
Track per-query:
```json
{
  "query_id": "q_123",
  "agent_id": "claude_instance_456",
  "capability_queried": "search_products",
  "response_time_ms": 45,
  "result_count": 12,
  "selected": true,
  "conversion": true
}
```

## The Zero-Click Future

### Automatic Replenishment
The holy grail: agent reorders without human involvement.
- Predict consumption → suggest reorder
- Integrate with home inventory (smart devices)
- Earn "default vendor" status

### Winning Default Status
Once an agent selects you for auto-reorder:
- Consistency beats occasional discounts
- Reliability beats marketing
- API stability = stickiness

### Lock-In Through Integration
The deeper the integration, the higher the switching cost:
- Context accumulation (agent learns your product's nuances)
- Workflow embedding (agent's process depends on your API)
- Data dependencies (history, preferences stored with you)
