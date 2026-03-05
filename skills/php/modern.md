# PHP 8+ Traps

- Named args break rename — `foo(name: $x)` breaks if param renamed
- Match is exhaustive — no matching arm throws `UnhandledMatchError`
- Nullsafe `?->` — returns null, doesn't short-circuit further ops
- Union types null — `int|null` not same as `?int` in some contexts
- Attributes reflection — `#[Attr]` needs ReflectionAttribute to read
- Constructor promotion + default — `public int $x = 0` in signature
- `str_contains`/`str_starts_with` — PHP 8+, polyfill for older
- Enums can't extend — backed enums need type, cases are singletons
