# Dispose Traps

- Missing `using` — resource leak for files, connections, streams
- `using` with null — throws, use `using var x = maybeNull;` (C# 8+ handles null)
- `Dispose()` not called on exception — `using` or try/finally required
- Finalizer runs on GC thread — don't access other managed objects
- `IAsyncDisposable` — use `await using` for async cleanup
- Double dispose — should be safe (no-op), but some implementations throw
- Dispose in constructor failure — if constructor throws, Dispose not called
- `HttpClient` — don't dispose per request, reuse or use `IHttpClientFactory`
