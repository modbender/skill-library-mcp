# Debugging Across Platforms

## Debugging Workflow

```
1. Reproduce          → Can you reliably trigger the bug?
2. Isolate           → Find the minimal failing case
3. Analyze           → Check logs, traces, metrics
4. Hypothesize       → Form a theory
5. Test              → Verify the theory
6. Fix               → Implement the solution
7. Verify            → Ensure fix works
8. Prevent           → Add test/monitoring
```

## Request Tracing

```typescript
// Add request ID
app.use(async (req, res, next) => {
  req.id = req.headers['x-request-id'] ?? crypto.randomUUID()
  res.setHeader('x-request-id', req.id)
  next()
})

// Log with request ID
app.use((req, res, next) => {
  const start = Date.now()
  res.on('finish', () => {
    logger.info({
      requestId: req.id,
      method: req.method,
      path: req.path,
      status: res.statusCode,
      duration: Date.now() - start,
    })
  })
  next()
})
```

## Production Debugging Safety

- [ ] Never use production data in tests
- [ ] Add verbose logging temporarily
- [ ] Use read-only database connections
- [ ] Limit data exposure in logs
- [ ] Roll back changes after debugging

## Checklist

- [ ] Add request IDs
- [ ] Set up centralized logging
- [ ] Use debugging tools (Chrome DevTools, curl)
- [ ] Check network tab
- [ ] Review server logs
- [ ] Use breakpoints (local dev only)
