# ORM Traps

- Iterating QuerySet twice hits DB twice — `list(qs)` to cache
- `exists()` vs `bool(qs)` — bool fetches all rows, exists() is O(1)
- `count()` vs `len(qs)` — len() fetches all, count() uses SQL COUNT
- No `select_related` in loop = N+1 — one query per FK access
- `prefetch_related` after filter — invalidates cache, N+1 returns
- `update()` skips signals — no `post_save`, no `auto_now` fields
- `F()` required for atomicity — `obj.count += 1` has race condition
- `distinct()` after `values()` — duplicates without it
- `transaction.atomic()` doesn't swallow exceptions — rollback happens, error still raises
- `select_for_update()` without transaction — raises error, must be in `atomic()`
- `iterator()` breaks prefetch — can't cache M2M with iterator
