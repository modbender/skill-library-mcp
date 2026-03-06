---
name: C#
slug: csharp
version: 1.0.1
description: Write robust C# avoiding null traps, async deadlocks, and LINQ pitfalls.
metadata: {"clawdbot":{"emoji":"💜","requires":{"bins":["dotnet"]},"os":["linux","darwin","win32"]}}
---

## Quick Reference

| Topic | File |
|-------|------|
| Null reference, nullable types | `nulls.md` |
| Async/await, deadlocks | `async.md` |
| Deferred execution, closures | `linq.md` |
| Value vs reference, boxing | `types.md` |
| Iteration, equality | `collections.md` |
| IDisposable, using, finalizers | `dispose.md` |

## Critical Rules

- `?.` and `??` prevent NRE but `!` overrides warnings — still crashes if null
- `.Result` or `.Wait()` on UI thread — deadlock, use `await` or `ConfigureAwait(false)`
- LINQ is lazy — `query.Where(...)` doesn't execute until iteration
- Multiple enumeration of IEnumerable — may re-query database, call `.ToList()` first
- Closure captures variable, not value — loop variable in lambda captures last value
- Struct in async method — copied, modifications lost after await
- String comparison culture — `StringComparison.Ordinal` for code, `CurrentCulture` for UI
- `GetHashCode()` must be stable — mutable fields break dictionary lookup
- Modifying collection while iterating — throws, use `.ToList()` to iterate copy
- `decimal` for money — `float`/`double` have precision loss
- `readonly struct` prevents defensive copies — use for performance
- `sealed` prevents inheritance — enables devirtualization optimization
