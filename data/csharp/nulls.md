# Null Traps

- `!` (null-forgiving) silences warnings but doesn't prevent NRE — actual null still crashes
- `Nullable<T>.Value` throws if null — check `HasValue` or use `GetValueOrDefault()`
- `as` returns null on failure, `(Type)` throws — choose based on expected case
- `??=` assigns only if null — `x ??= y` is `x = x ?? y`
- `?.` short-circuits — `obj?.Method()?.Property` returns null if any part is null
- Nullable reference types are compile-time only — no runtime enforcement
- `default(T)` for reference types is null — even with NRT enabled
- Null in dictionary — `dict[key]` throws if missing, use `TryGetValue`
