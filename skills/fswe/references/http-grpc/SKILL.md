# HTTP & gRPC Deep Understanding

## REST Best Practices

### URL Design
```
GET    /api/v1/users          → List
POST   /api/v1/users          → Create
GET    /api/v1/users/:id      → Read
PATCH  /api/v1/users/:id      → Update
DELETE /api/v1/users/:id      → Delete
```

### Status Codes
| Code | Usage |
|------|-------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 429 | Rate Limited |
| 500 | Server Error |

## gRPC vs REST

| Aspect | REST | gRPC |
|--------|------|------|
| Format | JSON | Protocol Buffers |
| Speed | Medium | Fast |
| Browser Support | Native | Requires gRPC-Web |
| Streaming | Limited | Full support |
| Code Gen | OpenAPI | Built-in |

## Idempotency

```typescript
// Idempotent POST with idempotency key
app.post('/payments', async (req, res) => {
  const idempotencyKey = req.headers['idempotency-key']
  
  // Check if already processed
  const existing = await cache.get(`idempotency:${idempotencyKey}`)
  if (existing) return existing
  
  // Process payment
  const result = await processPayment(req.body)
  
  // Cache result
  await cache.set(`idempotency:${idempotencyKey}`, result, { ttl: 86400 })
  
  return result
})
```

## Checklist

- [ ] Use proper HTTP methods
- [ ] Return correct status codes
- [ ] Implement idempotency for mutations
- [ ] Version API from v1
- [ ] Document with OpenAPI
