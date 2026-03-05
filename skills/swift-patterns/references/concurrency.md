# SwiftUI Concurrency (Lifecycle-Scoped)

## Overview
This reference focuses on SwiftUI-friendly async patterns: `.task`, `.task(id:)`, cancellation checks, and safe UI updates with `@MainActor`.
It intentionally avoids deep concurrency patterns and architecture mandates.

## Decision Tree: `.task` vs `.onAppear` vs `.onChange`

1) Do you need async work tied to the view lifecycle?
- Yes -> Use `.task`

2) Does the async work depend on a changing identifier or filter?
- Yes -> Use `.task(id:)` to auto-cancel and restart when the value changes

3) Do you need to react to a value change (possibly multiple times)?
- Yes -> Use `.onChange` and start async work inside a `Task`

4) Do you only need lightweight, non-async setup when a view appears?
- Yes -> Use `.onAppear` with a guard to avoid duplicate work

## Core Patterns

### Basic `.task` for View-Scoped Loading
```swift
struct DetailView: View {
    @State private var item: Item?

    var body: some View {
        Group {
            if let item {
                Text(item.title)
            } else {
                ProgressView()
            }
        }
        .task {
            await loadItem()
        }
    }

    @MainActor
    private func loadItem() async {
        item = await fetchItem()
    }
}
```

### `.task(id:)` for ID-Driven Reloads
```swift
struct FilteredList: View {
    @State private var items: [Item] = []
    let filter: Filter

    var body: some View {
        List(items) { item in
            Text(item.title)
        }
        .task(id: filter) {
            await load(filter: filter)
        }
    }

    @MainActor
    private func load(filter: Filter) async {
        items = await fetchItems(filter: filter)
    }
}
```

### `.onChange` for Value-Driven Async Work
```swift
.onChange(of: query) { _, newValue in
    Task {
        await performSearch(query: newValue)
    }
}
```

## Cancellation Awareness
SwiftUI cancels `.task` when the view disappears or the id changes. Long-running work should check cancellation.

```swift
func loadPages() async throws {
    for page in pages {
        try Task.checkCancellation()
        try await fetchPage(page)
    }
}
```

## `@MainActor` for UI Updates
Update UI state on the main actor.

- Use `@MainActor` on functions that mutate view state.
- If your project uses default actor isolation, explicit `@MainActor` may not be required.

```swift
@MainActor
func updateState(with items: [Item]) {
    self.items = items
}
```

## Common Pitfalls

- Starting async work in `body` causes repeated execution on every render.
- Using `.onAppear` for network loads without guards leads to duplicate requests.
- Ignoring cancellation can result in stale or out-of-order UI updates.
- Updating UI state off the main actor can cause crashes or warnings.
