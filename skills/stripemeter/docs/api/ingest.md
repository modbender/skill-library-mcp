# API — Ingest (v0.3.0)

[← Back to Welcome](../welcome.md)

POST /v1/events/ingest

Headers
- Content-Type: application/json
- Idempotency-Key (string, optional): Custom idempotency key for the entire batch
  - Precedence: `event.idempotencyKey` in the body takes priority over the header. If the body event lacks `idempotencyKey`, the header value is applied. If neither are provided, the server deterministically generates one.

Request Body
```json
{
  "events": [
    {
      "tenantId": "demo",
      "metric": "requests",
      "customerRef": "cus_123",
      "resourceId": "res_1",
      "quantity": 100,
      "ts": "2025-01-16T14:30:00Z",
      "source": "api",
      "meta": {
        "endpoint": "/v1/search",
        "region": "us-east-1"
      }
    }
  ]
}
```

Response (per-event results)
```json
{
  "accepted": 1,
  "duplicates": 0,
  "requestId": "req-123",
  "results": [
    {
      "idempotencyKey": "evt_abc123",
      "status": "accepted"
    }
  ],
  "errors": []
}
```

Examples
```bash
# Send a single event with idempotency
curl -X POST http://localhost:3000/v1/events/ingest \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: my-batch-123" \
  -d '{
    "events": [{
      "tenantId": "demo",
      "metric": "requests",
      "customerRef": "cus_123",
      "quantity": 100,
      "ts": "2025-01-16T14:30:00Z"
    }]
  }'

# Send the same event again (should be deduplicated)
curl -X POST http://localhost:3000/v1/events/ingest \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: my-batch-123" \
  -d '{
    "events": [{
      "tenantId": "demo",
      "metric": "requests",
      "customerRef": "cus_123",
      "quantity": 100,
      "ts": "2025-01-16T14:30:00Z"
    }]
  }'
```

Notes
- Events with the same idempotency key are counted exactly once
- Precedence: body `idempotencyKey` > `Idempotency-Key` header > server-generated key
- If no `Idempotency-Key` header or body key is provided, one is generated from the event fields
- The `ts` field should be in ISO 8601 format
- `meta` can contain any additional JSON data for the event
- Batch size limit: 1000 events per request
