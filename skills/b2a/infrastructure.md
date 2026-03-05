# B2A Infrastructure — Technical Implementation

## Protocols & Standards

### MCP (Model Context Protocol)
Anthropic's protocol for agent-to-tool communication:
```json
{
  "tools": [{
    "name": "get_product",
    "description": "Retrieve product by ID",
    "inputSchema": {
      "type": "object",
      "properties": {
        "product_id": {"type": "string"}
      },
      "required": ["product_id"]
    }
  }]
}
```

### OpenAPI 3.1
Critical for agent discovery:
- Use descriptive `operationId` (agents use these to understand capabilities)
- Include examples for every endpoint
- Document all error codes semantically
- Provide `x-agent-hints` for optimization

### Schema.org / JSON-LD
For product discoverability:
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Widget Pro",
  "sku": "WP-001",
  "offers": {
    "@type": "Offer",
    "price": 99.99,
    "priceCurrency": "USD",
    "availability": "InStock"
  }
}
```

## Authentication for Agents

### Client Credentials Flow (OAuth 2.0)
Agents can't do interactive login:
```bash
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials&
client_id=agent_123&
client_secret=xxx&
scope=products:read orders:create
```

### API Keys with Scopes
- Per-capability keys (read vs write)
- Rate limiting by agent identity, not IP
- Audit logging per agent

### Agent Identity Verification
How to know a request comes from a legitimate agent:
- Signed requests (JWT with agent identity)
- Callback verification to agent's registered URL
- Reputation lookup in public registries

## Payment Integration

### Stripe Agent Toolkit
```python
# Agent requests payment
stripe.PaymentIntent.create(
    amount=9999,
    currency="usd",
    metadata={"agent_id": "agent_123", "user_id": "user_456"},
    # Pre-authorized by user
    confirm=True
)
```

### Agent Wallet Patterns
- **Pre-authorized budget**: User gives agent $X to spend
- **Per-transaction approval**: Agent requests, user approves (async)
- **Escrow**: Payment held until delivery confirmed

### Payment Webhooks
Agents need programmatic confirmation:
```json
{
  "event": "payment.succeeded",
  "order_id": "ord_123",
  "amount": 9999,
  "currency": "usd",
  "timestamp": "2026-02-16T23:00:00Z"
}
```

## Error Handling

### Machine-Readable Errors
```json
{
  "error": {
    "code": "INSUFFICIENT_STOCK",
    "message": "Only 3 units available",
    "available_quantity": 3,
    "requested_quantity": 10,
    "retry_after_seconds": 3600
  }
}
```

Never return HTML error pages. Agents can't parse them.

### Error Codes for Agents
| Code | Meaning | Agent Action |
|------|---------|--------------|
| PRICE_CHANGED | Price differs from quoted | Re-query and decide |
| INSUFFICIENT_STOCK | Not enough inventory | Reduce quantity or skip |
| CAPABILITY_UNAVAILABLE | Service temporarily down | Retry with backoff |
| AUTHORIZATION_EXPIRED | Token needs refresh | Re-authenticate |

## Testing Agent Interactions

### Sandbox Environment
- Synthetic data that mirrors production structure
- Reset-able state for repeatable tests
- Rate limits matching production

### Agent Personas for Testing
Simulate different agent behaviors:
- **Aggressive**: Rapid-fire queries, price-focused
- **Cautious**: Multiple verification steps, trust-focused
- **Malicious**: Edge cases, injection attempts

### Metrics to Track
- p99 latency (agents are impatient)
- Parse success rate (can agent understand response?)
- Decision success rate (did agent complete the task?)

## Versioning & Deprecation

### Agent-Friendly Deprecation
Agents don't read emails. Deprecation must be in-band:
```http
HTTP/1.1 200 OK
Sunset: Sat, 01 Jun 2026 00:00:00 GMT
Deprecation: true
Link: </v2/products>; rel="successor-version"
```

### Changelog API
```json
GET /api/changelog
{
  "versions": [{
    "version": "2.0.0",
    "released": "2026-02-01",
    "breaking_changes": ["price_field_renamed"],
    "migration_guide": "/docs/v2-migration"
  }]
}
```

## Security Considerations

### Blast Radius Limiting
If an agent is compromised, limit damage:
- Per-agent spending limits
- Action rate limiting
- Anomaly detection on agent behavior

### Authorization Chain
Verify: Agent → User delegation → Action scope
- Agent must prove user authorized this specific action
- Scope narrowing: agent can only do what user allowed

### Audit Trail
Log everything an agent does:
- Which agent, which user it represents
- What action, what data accessed
- Timestamp, IP, result
