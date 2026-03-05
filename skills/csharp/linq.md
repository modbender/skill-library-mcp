# LINQ Traps

- Deferred execution — `Where()`, `Select()` don't run until you iterate
- Multiple enumeration — calling `.Count()` then iterating runs query twice
- Closure captures variable — `for(var i=0; i<10; i++) list.Add(() => i)` all return 10
- `First()` throws if empty — use `FirstOrDefault()` and handle null
- `Single()` throws if not exactly one — use when you expect exactly one
- `OrderBy().OrderBy()` — second replaces first, use `ThenBy()` for secondary sort
- `ToList()` materializes — changes after won't reflect, use when you need snapshot
- `AsEnumerable()` vs `AsQueryable()` — AsEnumerable runs rest in memory
- EF Core: client evaluation — complex expressions execute in memory, not SQL
