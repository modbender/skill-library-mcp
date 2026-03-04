# Reusable SwiftUI Patterns

Building blocks for common SwiftUI scenarios. Use these patterns as starting points, not rigid templates.

## Container Views

Wrap content with loading/error states to avoid repeating conditional logic.

```swift
struct AsyncContentView<Content: View>: View {
    let isLoading: Bool
    let error: Error?
    @ViewBuilder let content: () -> Content
    let retry: () -> Void

    var body: some View {
        if isLoading {
            ProgressView()
        } else if let error {
            ContentUnavailableView {
                Label("Error", systemImage: "exclamationmark.triangle")
            } description: {
                Text(error.localizedDescription)
            } actions: {
                Button("Retry", action: retry)
            }
        } else {
            content()
        }
    }
}

// Usage
AsyncContentView(
    isLoading: viewModel.isLoading,
    error: viewModel.error,
    content: { UserList(users: viewModel.users) },
    retry: { Task { await viewModel.load() } }
)
```

## ViewModifiers for Reusable Styling

Extract repeated styling into modifiers instead of copying view code.

```swift
struct CardStyle: ViewModifier {
    func body(content: Content) -> some View {
        content
            .padding()
            .background(Color(.systemBackground))
            .clipShape(RoundedRectangle(cornerRadius: 12))
            .shadow(color: .black.opacity(0.1), radius: 5, y: 2)
    }
}

extension View {
    func cardStyle() -> some View {
        modifier(CardStyle())
    }
}

// Usage
Text("Hello").cardStyle()
```

## Environment-Based Dependency Injection

Use custom environment keys for app-wide dependencies.

```swift
// Define the key
private struct UserServiceKey: EnvironmentKey {
    static let defaultValue: UserServiceProtocol = UserService()
}

extension EnvironmentValues {
    var userService: UserServiceProtocol {
        get { self[UserServiceKey.self] }
        set { self[UserServiceKey.self] = newValue }
    }
}

// Inject at app root
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.userService, UserService())
        }
    }
}

// Use in views
struct ContentView: View {
    @Environment(\.userService) private var userService

    var body: some View {
        Text("Hello")
            .task {
                let users = try? await userService.fetchUsers()
            }
    }
}
```

## PreferenceKeys for Child-to-Parent Communication

Pass values up the view hierarchy when callbacks aren't practical.

```swift
struct ScrollOffsetPreferenceKey: PreferenceKey {
    static var defaultValue: CGFloat = 0
    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) {
        value = nextValue()
    }
}

struct ContentView: View {
    @State private var scrollOffset: CGFloat = 0

    var body: some View {
        ScrollView {
            VStack {
                ForEach(0..<50, id: \.self) { i in
                    Text("Item \(i)")
                }
            }
            .background(
                GeometryReader { geometry in
                    Color.clear.preference(
                        key: ScrollOffsetPreferenceKey.self,
                        value: geometry.frame(in: .named("scroll")).minY
                    )
                }
            )
        }
        .coordinateSpace(name: "scroll")
        .onPreferenceChange(ScrollOffsetPreferenceKey.self) { value in
            scrollOffset = value
        }
    }
}
```

## When to Use Each Pattern

- **Container views**: Loading states, error handling, empty states, permission gates
- **ViewModifiers**: Repeated styling, conditional appearance, reusable animations
- **Environment DI**: Services, repositories, feature flags, app-wide configuration
- **PreferenceKeys**: Scroll position, child geometry, aggregating values from children
