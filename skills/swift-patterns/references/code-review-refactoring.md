# Code Smells & Anti-Patterns (SwiftUI)

Common issues to look for when reviewing or refactoring SwiftUI code.

## SwiftUI Code Smells

- **Duplicate source of truth:** `@State` and model both hold the same value.
- **Stored derived state:** Computing and storing values that could be computed properties.
- **Side effects in body:** Mutations or async work triggered during view rendering.
- **Unstable list identity:** Using `.indices` or non-unique IDs for dynamic `ForEach`.
- **Competing navigation sources:** Multiple `NavigationStack` roots or duplicated path state.
- **Heavy work in body:** Formatters, parsing, or sorting recreated every render.
- **Silent error handling:** Swallowing errors without user feedback.

## Examples

### Duplicate Source of Truth
```swift
// Bad: state duplicated
struct PlayerView: View {
    @State private var isPlaying = false
    let model: PlayerModel

    var body: some View {
        Toggle("Playing", isOn: $isPlaying)
            .onChange(of: isPlaying) { model.isPlaying = $0 }
    }
}

// Good: single source of truth
struct PlayerView: View {
    @Binding var isPlaying: Bool

    var body: some View {
        Toggle("Playing", isOn: $isPlaying)
    }
}
```

### Unstable List Identity
```swift
// Bad: indices shift on insert/delete
ForEach(items.indices, id: \.self) { index in
    RowView(item: items[index])
}

// Good: stable identity from model
ForEach(items, id: \.id) { item in
    RowView(item: item)
}
```

### Stored Derived State
```swift
// Bad: derived value stored and manually synced
struct CheckoutView: View {
    let subtotal: Decimal
    @State private var total: Decimal = 0

    var body: some View {
        Text("Total: \(total)")
            .onAppear { total = subtotal * 1.08 }
    }
}

// Good: compute directly
struct CheckoutView: View {
    let subtotal: Decimal
    var total: Decimal { subtotal * 1.08 }

    var body: some View {
        Text("Total: \(total)")
    }
}
```

## Anti-Patterns

- Global mutable state accessed by multiple views without clear ownership.
- Navigation driven by both view state and model state (competing sources).
- Copying view state into models without ownership boundaries.
- Silent error handling that hides failures from users.
- Over-abstraction that reduces testability without clear benefit.
