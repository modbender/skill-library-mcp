# Performance Engineering

## Bottleneck Detection

```typescript
// Simple profiling
const timers = new Map<string, number>()

export function startTimer(name: string) {
  timers.set(name, Date.now())
}

export function endTimer(name: string) {
  const start = timers.get(name)
  if (!start) return
  console.log(`${name}: ${Date.now() - start}ms`)
  timers.delete(name)
}

// Usage
startTimer('db-query')
const users = await db.query('SELECT * FROM users')
endTimer('db-query')
```

## Query Optimization

```sql
-- Use EXPLAIN ANALYZE
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- Add indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_orders_user_id ON orders(user_id, created_at DESC);
```

## Caching Strategy

| Data Type | TTL | Strategy |
|-----------|-----|----------|
| User session | 24h | Redis |
| Config | 1h | Memory |
| Product catalog | 1h | Redis + CDN |
| API responses | 1min | Cache-aside |

## Checklist

- [ ] Profile critical paths
- [ ] Optimize database queries
- [ ] Add appropriate indexes
- [ ] Implement caching
- [ ] Set up load testing
- [ ] Monitor Core Web Vitals (frontend)
