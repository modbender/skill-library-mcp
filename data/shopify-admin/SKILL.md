---
name: shopify-admin
version: 1.0.0
description: Shopify Admin API CLI for orders, products, customers, and store management. Uses REST and GraphQL APIs with environment-based authentication.
metadata:
  openclaw:
    requires:
      env:
        - SHOPIFY_STORE_DOMAIN
        - SHOPIFY_ACCESS_TOKEN
      bins:
        - curl
        - jq
---

# shopify-admin - Shopify Admin API

Interact with Shopify Admin API for order management, product operations, customer data, and store analytics.

## Prerequisites

**Required binaries:** `curl`, `jq` (must be installed and on PATH).

**Environment:** The script uses **only** the process environment. It does **not** source any file (no `~/.openclaw/.env` or other dotenv). Set these variables where the OpenClaw agent/gateway runs (e.g. export in shell, or in a file that your gateway loads at startup):

```bash
SHOPIFY_STORE_DOMAIN=your-store.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxx
```

If the script is run by the agent, ensure the gateway process has these vars (many setups load `~/.openclaw/.env` when starting the gateway — then the agent inherits them; the script itself does not read that file).

## API Endpoints

### REST API
Base URL: `https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/`

### GraphQL API
Endpoint: `https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/graphql.json`

## Common Operations

### Orders

**List orders:**
```bash
curl -s "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/orders.json?status=any&limit=10" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

**Get specific order:**
```bash
curl -s "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/orders/{order_id}.json" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN"
```

### Products

**List products:**
```bash
curl -s "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/products.json?limit=50" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN"
```

**Search products:**
```bash
curl -s "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/products.json?title={title}" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN"
```

**Delete product:**
```bash
curl -s -X DELETE "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/products/{product_id}.json" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN"
```

### Customers

**List customers:**
```bash
curl -s "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/customers.json?limit=50" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN"
```

**Get customer:**
```bash
curl -s "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/customers/{customer_id}.json" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN"
```

### GraphQL Queries

**Get order with customer details:**
```bash
curl -s -X POST "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/graphql.json" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { order(id: \"gid://shopify/Order/{order_id}\") { id name customer { firstName lastName email } } }"
  }'
```

## Marketing & Analytics

### Marketing Events

**List marketing events (campaigns, UTMs):**
```bash
curl -s "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/marketing_events.json?limit=50" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN"
```

**Get specific marketing event:**
```bash
curl -s "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/marketing_events/{event_id}.json" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN"
```

**Create marketing event (track campaign):**
```bash
curl -s -X POST "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/marketing_events.json" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "marketing_event": {
      "event_type": "ad",
      "utm_campaign": "spring_sale",
      "utm_source": "facebook",
      "utm_medium": "cpc",
      "started_at": "2026-01-15T00:00:00Z"
    }
  }'
```

### Reports & Analytics

**List available reports:**
```bash
curl -s "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/reports.json" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN"
```

**Get report (sales, traffic, etc.):**
```bash
curl -s "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/reports/{report_id}.json" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN"
```

### Shop Analytics (Sessions, Traffic)

**Get shop analytics/sessions data via GraphQL:**
```bash
curl -s -X POST "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/graphql.json" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { shop { name analytics { onlineStoreSessions { count } } } }"
  }'
```

**Get online store sessions (REST):**
```bash
# Note: Sessions data is typically available via Shopify Analytics API or Reports
curl -s "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/shop.json" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN" | jq '.shop'
```

### Order Attribution (UTM tracking)

**Get order with attribution data:**
```bash
curl -s "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/orders/{order_id}.json" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN" | jq '.order | {id, name, referring_site, landing_site, source_name}'
```

**List orders with UTM parameters:**
```bash
curl -s "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/orders.json?fields=id,name,referring_site,landing_site,source_name,created_at&limit=50" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN"
```

### Customer Events (Behavior tracking)

**List customer events (visits, actions):**
```bash
curl -s "https://$SHOPIFY_STORE_DOMAIN/admin/api/2026-01/customers/{customer_id}/events.json" \
  -H "X-Shopify-Access-Token: $SHOPIFY_ACCESS_TOKEN"
```

## Important Notes

### PII Access Limitations
- Customer names, emails, addresses require **Shopify plan or higher**
- Basic plan: PII fields return `null` via API
- Web UI always shows full customer data
- Workaround: Use webhooks to capture PII before masking

### API Versions
- Current: 2026-01
- Update version in URL for newer features

### Rate Limits
- REST: 2 calls/second (Shopify plan)
- GraphQL: Same bucket as REST
- Check `X-Shopify-Shop-Api-Call-Limit` header

### Response Codes
- 200: Success
- 201: Created
- 204: Deleted (no body)
- 429: Rate limited
- 403: Permission denied (check scopes)

## Scopes Required

- `read_orders`, `write_orders`
- `read_products`, `write_products`
- `read_customers`, `write_customers`
- `read_analytics`
- `read_marketing_events`, `write_marketing_events`
- `read_customer_events`
- `read_reports`

## Tips

- Use `jq` for JSON parsing: `| jq '.orders[0]'`
- Add `-w "\nHTTP: %{http_code}"` to curl for status codes
- Use GraphQL for complex nested queries
- REST is simpler for basic CRUD operations
