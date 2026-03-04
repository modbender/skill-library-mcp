# Performance (SwiftUI)

Use this reference to apply a baseline checklist first, then consider safe, SwiftUI-specific optimizations.

## Performance baseline

Start here before suggesting changes:

- Expensive work in `body` (formatters, parsing, sorting, image decoding).
- Unstable list identity (indices or non-unique IDs) causing row churn.
- Heavy work on the main thread (blocking file/network/JSON work).
- Async work detached from the view lifecycle (duplicate or stale tasks).

If issues persist after baseline fixes, profiling tools like Instruments can help identify hot paths.

## Safe optimizations

Consider these when the baseline checklist points to them:

- **Identity stability:** use stable IDs in `ForEach` and `List`. See `references/lists-collections.md`.
- **Lazy containers:** use `List`, `LazyVStack`, or `LazyVGrid` for long collections. See `references/scrolling.md`.
- **Expensive-work avoidance:** move formatters, parsing, and derived values out of `body` so they are not recreated every render.

## SwiftUI lifecycle for async work

Prefer `.task` to tie async work to view lifecycle, and check cancellation in long-running tasks.
Use `.task(id:)` when work depends on inputs like filters, IDs, or search terms.

## SwiftUI snippets

### Stable identity in `ForEach`
```swift
ForEach(items, id: \.id) { item in
    Row(item: item)
}
```

### Move formatter out of `body`
```swift
private let formatter: DateFormatter = {
    let f = DateFormatter()
    f.dateStyle = .medium
    return f
}()

var body: some View {
    Text(formatter.string(from: date))
}
```

### Tie async work to view lifecycle
```swift
.task(id: userID) {
    try Task.checkCancellation()
    await loadUser(id: userID)
}
```

## Risk cues (split refactors)

If any of these change, split the refactor or add tests first:

- State ownership moves between views or wrappers.
- List identity or ordering changes.
- Async work moves between `body`, `.task`, or other lifecycle hooks.

## Related references

- `references/lists-collections.md` for stable identity guidance.
- `references/scrolling.md` for lazy containers and pagination patterns.
