# Concurrency & Synchronization

## Concurrency
- `volatile` ensures visibility, not atomicity — `count++` still needs synchronization
- `synchronized` on method locks `this` — static synchronized locks class object
- Double-checked locking broken without volatile — use holder pattern or enum for singletons
- `ConcurrentHashMap` safe but not atomic for compound ops — use `computeIfAbsent()`
- Thread pool: don't create threads manually — use `ExecutorService`

## Exception Handling
- Checked exceptions must be caught or declared — unchecked (RuntimeException) don't
- Try-with-resources auto-closes — implement `AutoCloseable`, Java 7+
- Catch specific exceptions first — more general catch later or unreachable code error
- Don't catch `Throwable` — includes `Error` which shouldn't be caught
- `finally` always runs — even on return, but return in finally overrides try's return
