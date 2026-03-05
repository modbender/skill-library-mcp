# Async Traps

- ORM is sync-only — `await Model.objects.get()` raises SynchronousOnlyOperation
- `sync_to_async` for ORM — `await sync_to_async(Model.objects.get)(pk=1)`
- `sync_to_async` default not thread-safe — use `thread_sensitive=True` for ORM
- Async view with sync middleware — entire request becomes sync
- `database_sync_to_async` in Channels — wrapper for ORM in consumers
- Prefetch in async — must be done in sync context, then passed to async
- `aiterator()` for async iteration — but still wraps sync ORM internally
