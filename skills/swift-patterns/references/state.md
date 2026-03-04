# State Ownership

Use ownership to choose the right property wrapper. Keep a single source of truth and pass state down through bindings or immutable values.

## Decision Tree

1. Does this view own the value and it can reset when the view goes away?
   - Yes: use `@State`.
2. Does a parent own the value and this view only edits it?
   - Yes: use `@Binding`.
3. Is this value shared across many views or the app lifecycle?
   - Yes: inject through `@Environment` or a shared model in the environment.
4. Is this a reference-type model with derived state and logic?
   - iOS 17+: prefer `@Observable` models.
   - Earlier OS support: use `ObservableObject` with `@StateObject` (owner) or `@ObservedObject` (observer).

## Wrapper Cheatsheet

- `@State`: view-owned, ephemeral value types.
- `@Binding`: child edits parent-owned state.
- `@Environment`: shared values supplied by the system or the app.
- `@Observable`: modern reference models (iOS 17+).
- `ObservableObject`: compatibility fallback for earlier OSes.

## Ownership Rules

- One owner, many readers. Avoid duplicate sources of truth.
- If a child edits a value, pass a `Binding` instead of copying.
- Keep shared models in the environment when many views need access.
- Hoist state up only when multiple siblings need it; otherwise keep it local.

## Examples

### Parent owns, child edits
```swift
struct ParentView: View {
    @State private var count = 0

    var body: some View {
        CounterView(count: $count)
    }
}

struct CounterView: View {
    @Binding var count: Int

    var body: some View {
        Button("Count: \(count)") { count += 1 }
    }
}
```

### Shared model in environment
```swift
@Observable
final class SessionModel {
    var isSignedIn = false
}

struct RootView: View {
    @State private var session = SessionModel()

    var body: some View {
        ContentView()
            .environment(session)
    }
}
```

## Observation Notes

- `@Observable` is preferred for new code on iOS 17+.
- For earlier OS support, use `ObservableObject` with `@StateObject` or `@ObservedObject`.
- `@Observable` models that mutate UI-facing state may need `@MainActor` depending on project isolation.
