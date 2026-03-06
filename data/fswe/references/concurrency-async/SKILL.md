# Concurrency & Async Programming

## Event Loop Model

```
┌─────────────┐
ers    ││   Tim ← setTimeout, setInterval
├─────────────┤
│   Pending   │ ← I/O callbacks
├─────────────┤
│   Idle      │ ← node internal
├─────────────┤
│   Poll      │ ← I/O
├─────────────┤
│   Check     │ ← setImmediate
├─────────────┤
│  Close CB   │ ← socket.close
└─────────────┘
```

## Promise Patterns

```typescript
// Parallel execution
const [users, posts, comments] = await Promise.all([
  getUsers(),
  getPosts(),
  getComments(),
])

// Race condition prevention
async function fetchWithTimeout(url: string, ms: number) {
  const timeout = new Promise((_, reject) => 
    setTimeout(() => reject(new Error('Timeout')), ms)
  )
  return Promise.race([fetch(url), timeout])
}

// Retry with backoff
async function retry<T>(
  fn: () => Promise<T>,
  attempts = 3,
  delay = 1000
): Promise<T> {
  try {
    return await fn()
  } catch (err) {
    if (attempts <= 1) throw err
    await new Promise(r => setTimeout(r, delay))
    return retry(fn, attempts - 1, delay * 2)
  }
}
```

## Async Error Handling

```typescript
// Always catch async errors
app.get('/users', async (req, res, next) => {
  try {
    const users = await getUsers()
    res.json(users)
  } catch (err) {
    next(err) // Pass to error middleware
  }
})
```

## Checklist

- [ ] Understand event loop phases
- [ ] Use Promise.all for parallel ops
- [ ] Handle promise rejections
- [ ] Implement timeouts
- [ ] Add retry logic
