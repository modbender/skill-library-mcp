# Lists and Collections

Use stable identity and lazy containers to keep lists correct and performant.

## Stable Identity

- Prefer `Identifiable` models for lists and `ForEach`.
- If not `Identifiable`, provide a stable `id:`.
- Avoid `.indices` for dynamic data; indices shift on insert/delete and break identity.

```swift
struct Item: Identifiable {
    let id: UUID
    let title: String
}

List(items) { item in
    Text(item.title)
}
```

## List vs ScrollView + LazyVStack

- Use `List` for standard scrolling, selection, swipe actions, and system row behavior.
- Use `ScrollView` + `LazyVStack` for fully custom layouts or mixed content.
- For large collections, prefer lazy containers (`List`, `LazyVStack`, `LazyVGrid`).

## Sections and Empty States

- Group related rows into `Section` for clarity.
- Provide explicit empty states when the collection is empty.

```swift
if items.isEmpty {
    ContentUnavailableView("No Items", systemImage: "tray")
} else {
    List {
        Section("Recent") {
            ForEach(items) { item in
                Row(item: item)
            }
        }
    }
}
```

## Row Composition

- Keep row views lightweight and pure.
- Move heavy work (formatting, image decoding) out of row `body` when it can be cached.
- Pass values into rows; avoid side effects inside the row body.

## Common Pitfalls

- **Identity churn:** using unstable IDs causes rows to show the wrong data.
- **Row-level side effects:** triggers repeat work during scrolling.
- **Too much per-row state:** pushes state ownership into the wrong place.
