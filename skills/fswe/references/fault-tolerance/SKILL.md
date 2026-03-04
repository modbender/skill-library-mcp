# Fault Tolerance & Resilience

## Retry Strategies

```typescript
async function withRetry<T>(
  fn: () => Promise<T>,
  options: { attempts: number; delay: number } = { attempts: 3, delay: 1000 }
): Promise<T> {
  for (let i = 0; i < options.attempts; i++) {
    try {
      return await fn()
    } catch (err) {
      if (i === options.attempts - 1) throw err
      await new Promise(r => setTimeout(r, options.delay * Math.pow(2, i)))
    }
  }
  throw new Error('Unreachable')
}
```

## Circuit Breaker

```typescript
class CircuitBreaker {
  private failures = 0
  private state: 'closed' | 'open' | 'half-open' = 'closed'
  
  async call<T>(fn: () => Promise<T>): Promise<T> {
    if (this.state === 'open') {
      throw new Error('Circuit open')
    }
    
    try {
      const result = await fn()
      this.failures = 0
      this.state = 'closed'
      return result
    } catch (err) {
      this.failures++
      if (this.failures >= 5) {
        this.state = 'open'
        setTimeout(() => this.state = 'half-open', 30000)
      }
      throw err
    }
  }
}
```

## Timeout Management

```typescript
// Request timeout
app.use((req, res, next) => {
  res.setTimeout(30000, () => {
    res.status(503).json({ error: 'Request timeout' })
  })
  next()
})
```

## Checklist

- [ ] Implement retry with exponential backoff
- [ ] Add circuit breaker
- [ ] Set proper timeouts
- [ ] Handle graceful degradation
- [ ] Set up dead-letter queues
