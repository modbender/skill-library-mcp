# Protocol Gotchas

- Protocol extensions don't override — static dispatch ignores subclass implementation
- `Self` requirement prevents use as type — `protocol Animal` vs `any Animal`
- `@objc` required for optional protocol methods
- Associated types can't use with `any` without constraints — use generics or type erasure
- Witness matching is exact — `func foo(_: Int)` doesn't satisfy `func foo(_: some Numeric)`

# String Traps

- Characters can be multiple Unicode scalars — emoji count isn't byte count
- Subscripting is O(n) — use indices, not integers
- `String.Index` from one string invalid on another — even if contents match
- Empty string is not nil — check `.isEmpty`, not `== nil`
- `contains()` is case-sensitive — use `localizedCaseInsensitiveContains` for user search

# Collection Edge Cases

- `first` and `last` are optional — empty collection returns nil
- `removeFirst()` crashes on empty, `popFirst()` returns nil
- `index(of:)` is O(n) — for frequent lookups use Set or Dictionary
- Mutating while iterating crashes — copy first or use `reversed()` for removal
- `ArraySlice` indices don't start at 0 — use `startIndex`

# Error Handling

- `try?` swallows error details — use only when error type doesn't matter
- `try!` crashes on any error — never use in production paths
- Throwing from closure requires explicit `throws` in closure type
- `rethrows` only works if closure throws — prevents unnecessary `try` at callsite
- Error must conform to `Error` — plain `throw "message"` doesn't compile

# Build and Runtime

- Generic code bloat — specialized for each type, increases binary size
- `@inlinable` exposes implementation to other modules — ABI stability consideration
- Dynamic casting `as?` can be slow — prefer static typing
- Reflection with `Mirror` is slow — not for hot paths
- `print()` builds strings even in release — remove or use os_log
