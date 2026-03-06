# Scrolling and Pagination (SwiftUI)

## Overview
Use `List` for standard row-based content with selection, swipe actions, and built-in behavior.
Use `ScrollView` when you need custom layouts or non-list composition.
Use `ScrollViewReader` only when you must programmatically scroll to a specific item.

## Decision Tree

Start here:

1) Do you need row features (selection, swipe actions, edit mode, separators)?
- Yes -> Use `List`
- No -> Continue

2) Do you need custom layout (grids, mixed sections, cards, horizontal + vertical stacks)?
- Yes -> Use `ScrollView` with `LazyVStack`/`LazyHStack`
- No -> Continue

3) Do you need to programmatically scroll to an item or anchor?
- Yes -> Wrap in `ScrollViewReader`
- No -> Use `ScrollView` or `List` based on layout needs

## Safe Pagination Triggers

### Preferred: Sentinel Row
Add a dedicated footer row that appears after the list and triggers loading.

```swift
List {
    ForEach(items) { item in
        Row(item)
    }

    if hasMore {
        ProgressView()
            .frame(maxWidth: .infinity)
            .task {
                await loadNextPageIfNeeded()
            }
    }
}
```

### Alternate: Last-Item Appearance
Trigger when the last item appears, but guard against rapid re-entry.

```swift
ForEach(items) { item in
    Row(item)
        .onAppear {
            if item.id == items.last?.id {
                Task { await loadNextPageIfNeeded() }
            }
        }
}
```

### Guard Conditions (Avoid Duplicate Loads)
Always gate loading with explicit state:

- `isLoading == false`
- `hasMore == true`
- Track the last requested page or cursor

```swift
@MainActor
func loadNextPageIfNeeded() async {
    guard !isLoading, hasMore else { return }
    isLoading = true
    defer { isLoading = false }

    do {
        let page = try await fetchPage(cursor: nextCursor)
        items.append(contentsOf: page.items)
        nextCursor = page.nextCursor
        hasMore = page.hasMore
    } catch is CancellationError {
        return
    } catch {
        errorMessage = error.localizedDescription
    }
}
```

### Prefer `.task(id:)` for Filtered Loads
When pagination depends on a filter or identifier, reset and reload using `.task(id:)`.

```swift
.task(id: filter) {
    resetPagination()
    await loadNextPageIfNeeded()
}
```

## Common Pitfalls

- Side effects inside row `body` cause repeated work on every update.
- `onAppear` triggers multiple times during fast scrolling; guard with loading state.
- Starting work in `.onAppear` without cancellation can lead to overlapping loads.
- Geometry-based scroll offset triggers are noisy; prefer sentinel rows for stability.

## Notes on Async Pagination
Use cancellation-aware `.task` patterns for pagination work.
See `references/concurrency.md` for SwiftUI lifecycle and cancellation guidance.
