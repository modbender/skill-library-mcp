# NavigationStack Guidance

Use value-based navigation with a single source of truth. Keep navigation state in one place without mandating a coordinator pattern.

## Core Patterns

- Prefer `NavigationStack` over legacy navigation APIs.
- Use `NavigationLink(value:)` with `navigationDestination(for:)`.
- Keep navigation state in one owner (root view, feature root, or environment model).
- Avoid nested `NavigationStack` instances in the same flow.

## Basic Structure

```swift
enum Route: Hashable {
    case detail(Item.ID)
}

struct RootView: View {
    @State private var path: [Route] = []

    var body: some View {
        NavigationStack(path: $path) {
            List(items) { item in
                NavigationLink(value: Route.detail(item.id)) {
                    Text(item.title)
                }
            }
            .navigationDestination(for: Route.self) { route in
                switch route {
                case .detail(let id):
                    DetailView(id: id)
                }
            }
        }
    }
}
```

## Navigation State Ownership

- Use `@State` for simple paths local to a flow.
- For shared navigation state, store the path in a shared model injected through the environment.
- Keep programmatic navigation scoped to a single owner to avoid conflicting updates.

## Sheets and Full-Screen Presentation

- Use `sheet(item:)` when a selection drives presentation.
- Use `sheet(isPresented:)` for simple toggles.
- Use `fullScreenCover` for full-screen flows.
- Dismiss with `@Environment(\.dismiss)` from within the presented view.

```swift
struct ContentView: View {
    @State private var selectedItem: Item?

    var body: some View {
        List(items) { item in
            Button(item.title) { selectedItem = item }
        }
        .sheet(item: $selectedItem) { item in
            DetailSheet(item: item)
        }
    }
}

struct DetailSheet: View {
    let item: Item
    @Environment(\.dismiss) private var dismiss

    var body: some View {
        NavigationStack {
            DetailView(id: item.id)
                .toolbar {
                    ToolbarItem(placement: .cancellationAction) {
                        Button("Close") { dismiss() }
                    }
                }
        }
    }
}
```

## Avoid These Patterns

- Nested `NavigationStack` inside a view that is already in a stack.
- Mixing `NavigationView` and `NavigationStack` in the same flow.
- Scattering navigation state across multiple views.

## Consider When Needed (Optional)

- Use `NavigationPath` for dynamic, multi-type navigation stacks.
- Consider deep-link parsing and path restoration only when the product needs it.

## Modern Replacements

For legacy navigation API replacements, see `references/modern-swiftui-apis.md`.
