# B2A for Retail & Ecommerce

## The Invisible Shelf

In B2C: win the shelf → win the sale.
In B2A: win the API → win the sale.

Agents don't see:
- Product photography
- Shelf placement
- Eye-level positioning
- Packaging design

Agents see:
- Structured product data
- Availability APIs
- Pricing feeds
- Fulfillment specs

## Catalog Optimization

### Required Attributes
Every product must have machine-readable:

| Attribute | Format | Example |
|-----------|--------|---------|
| SKU | string | "WP-001" |
| price | {amount, currency} | {"amount": 9.99, "currency": "USD"} |
| availability | enum | "in_stock" / "out_of_stock" / "pre_order" |
| quantity_available | int | 847 |
| shipping_days_min | int | 1 |
| shipping_days_max | int | 3 |
| weight_kg | float | 0.5 |
| dimensions_cm | {l,w,h} | {"l": 10, "w": 5, "h": 3} |

### Normalization Rules
Agents compare across retailers. Use standard units:
- Weights: kilograms (not "half a pound")
- Dimensions: centimeters
- Volumes: milliliters
- Prices: explicit currency code

### Product Data Quality Score
Audit each product:
```
□ All required attributes present
□ Units are standard
□ Values are realistic (not placeholder zeros)
□ Images have alt-text with product name
□ Category matches industry standards
```

## Inventory APIs

### What to Expose
```json
GET /api/inventory/{sku}
{
  "sku": "WP-001",
  "available": 847,
  "reserved": 23,
  "incoming": 500,
  "incoming_eta": "2026-02-20",
  "locations": [
    {"warehouse": "NYC", "available": 400},
    {"warehouse": "LA", "available": 447}
  ],
  "low_stock_threshold": 50,
  "updated_at": "2026-02-16T23:30:00Z"
}
```

### Real-Time Updates
Agents expect fresh data:
- Websocket for inventory changes
- Polling endpoint with If-Modified-Since
- Max staleness < 5 minutes for fast-moving items

### What NOT to Expose
Competitive intelligence protection:
- Don't reveal total inventory strategy
- Don't expose supplier information
- Rate-limit bulk inventory queries
- Require authentication for detailed data

## Zero-Click Replenishment

### The Opportunity
An agent that auto-reorders is a locked customer:
- User says "keep me stocked on paper towels"
- Agent monitors consumption (smart home, past orders)
- Agent reorders when threshold hit
- No human decision point

### Winning the Default
To become the auto-reorder vendor:
1. **First mover**: Be selected for first successful reorder
2. **Consistency**: Never stockout, never late
3. **Price stability**: Don't spike prices after lock-in
4. **API reliability**: Agent trusts your uptime

### Replenishment API
```json
POST /api/subscriptions
{
  "user_id": "user_456",
  "agent_id": "agent_123",
  "sku": "WP-001",
  "trigger": {"type": "low_stock", "threshold": 2},
  "quantity": 10,
  "max_price": 12.99,
  "shipping": "standard"
}

GET /api/subscriptions/{id}/status
{
  "next_reorder_estimate": "2026-02-25",
  "consumption_rate": 0.3,
  "unit": "per_day"
}
```

## Promotions for Agents

### Machine-Readable Promotions
Convert human promotions:

| Human Version | Agent Version |
|--------------|---------------|
| "Buy 2, get 1 free" | `{"type": "bundle", "buy": 2, "free": 1}` |
| "20% off this week" | `{"type": "discount", "percent": 20, "expires": "2026-02-23"}` |
| "Free shipping over $50" | `{"type": "shipping_threshold", "min_order": 50}` |

### Promotion API
```json
GET /api/promotions?sku=WP-001
{
  "promotions": [
    {
      "id": "promo_123",
      "type": "volume_discount",
      "tiers": [
        {"min_qty": 5, "discount_percent": 10},
        {"min_qty": 10, "discount_percent": 15}
      ],
      "stackable": false,
      "valid_until": "2026-03-01T00:00:00Z"
    }
  ]
}
```

### Agent-Targeted Incentives
New category: promotions aimed at agents, not users:
- Referral fees for agents that bring orders
- Bonus for agents maintaining subscription customers
- "Preferred vendor" status for high-volume agents

## Fulfillment Data

### What Agents Need
```json
{
  "fulfillment_options": [
    {
      "method": "standard",
      "days_min": 3,
      "days_max": 5,
      "cost": 5.99,
      "cutoff_time": "14:00:00-05:00"
    },
    {
      "method": "express",
      "days_min": 1,
      "days_max": 2,
      "cost": 12.99,
      "cutoff_time": "18:00:00-05:00"
    }
  ],
  "origin_warehouse": "NYC",
  "destination_zip": "90210"
}
```

### Performance Metrics to Publish
- On-time delivery rate (last 30/90/365 days)
- Average delivery time by method
- Damage/loss rate
- Return processing time

## Analytics & Attribution

### Agent Channel Identification
Track whether a sale came from:
- Direct human purchase
- Agent-mediated (human approved)
- Agent-autonomous (auto-reorder)

### Required Tracking
| Field | Purpose |
|-------|---------|
| agent_id | Which agent placed order |
| user_id | Which human the agent represents |
| discovery_source | How agent found you |
| comparison_set | Who else agent evaluated |
| decision_time_ms | How long agent took to decide |

### Conversion Funnel for Agents
```
Catalog Query → Product View → Add to Cart → Checkout → Complete
    |              |              |            |           |
  90,000       45,000        12,000       8,000      7,500
```

Optimize each drop-off point.

## Competitive Intelligence

### What to Monitor
- Competitors' API availability and latency
- Their promotion structures (queryable)
- Their inventory patterns (what's often out of stock)
- Their fulfillment speeds

### Protect Your Intelligence
- Rate-limit catalog queries
- Require authentication for detailed data
- Monitor for scraping patterns
- Delay bulk exports
