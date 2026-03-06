---
description: "Navigation architecture, sheet presentation, and routing patterns"
---
# SwiftUI Navigation Reference

Comprehensive guide to NavigationStack, TabView, sheets, fullScreenCover, and routing patterns.

## Pattern Selection Guide

| Pattern | When to Use |
|---------|-------------|
| `NavigationStack` | Hierarchical drill-down (list → detail → edit) |
| `TabView` with `Tab` API | 3+ distinct top-level peer sections |
| `.sheet(item:)` | Creation forms, secondary actions, settings |
| `.fullScreenCover` | Immersive experiences (media player, onboarding) |
| `NavigationStack` + `.sheet` | Most MVPs with 2-4 features |

---

## NavigationStack

### Type-Safe Navigation

```swift
struct ContentView: View {
    var body: some View {
        NavigationStack {
            List {
                NavigationLink("Profile", value: Route.profile)
                NavigationLink("Settings", value: Route.settings)
            }
            .navigationDestination(for: Route.self) { route in
                switch route {
                case .profile:
                    ProfileView()
                case .settings:
                    SettingsView()
                }
            }
        }
    }
}

enum Route: Hashable {
    case profile
    case settings
}
```

### Programmatic Navigation

```swift
struct ContentView: View {
    @State private var navigationPath = NavigationPath()

    var body: some View {
        NavigationStack(path: $navigationPath) {
            List {
                Button("Go to Detail") {
                    navigationPath.append(DetailRoute.item(id: 1))
                }
            }
            .navigationDestination(for: DetailRoute.self) { route in
                switch route {
                case .item(let id):
                    ItemDetailView(id: id)
                }
            }
        }
    }
}

enum DetailRoute: Hashable {
    case item(id: Int)
}
```

---

## TabView

Use when the app has 3+ distinct, peer-level sections:

```swift
TabView {
    Tab("Home", systemImage: "house") {
        HomeView()
    }
    Tab("Search", systemImage: "magnifyingglass") {
        SearchView()
    }
    Tab("Profile", systemImage: "person") {
        ProfileView()
    }
}
```

---

## Sheet Patterns

### Item-Driven Sheets (Preferred)

```swift
// Good - item-driven
@State private var selectedItem: Item?

var body: some View {
    List(items) { item in
        Button(item.name) {
            selectedItem = item
        }
    }
    .sheet(item: $selectedItem) { item in
        ItemDetailSheet(item: item)
    }
}

// Avoid - boolean flag requires separate state
@State private var showSheet = false
@State private var selectedItem: Item?
```

**Why**: `.sheet(item:)` automatically handles presentation state and avoids optional unwrapping.

### Sheets Own Their Actions

Sheets should handle their own dismiss and actions internally.

```swift
struct EditItemSheet: View {
    @Environment(\.dismiss) private var dismiss
    @Environment(DataStore.self) private var store

    let item: Item
    @State private var name: String
    @State private var isSaving = false

    init(item: Item) {
        self.item = item
        _name = State(initialValue: item.name)
    }

    var body: some View {
        NavigationStack {
            Form {
                TextField("Name", text: $name)
            }
            .navigationTitle("Edit Item")
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button(isSaving ? "Saving..." : "Save") {
                        Task { await save() }
                    }
                    .disabled(isSaving || name.isEmpty)
                }
            }
        }
    }

    private func save() async {
        isSaving = true
        await store.updateItem(item, name: name)
        dismiss()
    }
}
```

---

## Full Screen Cover

```swift
@State private var showOnboarding = false

.fullScreenCover(isPresented: $showOnboarding) {
    OnboardingView()
}
```

---

## Popover

```swift
@State private var showPopover = false

Button("Show Popover") {
    showPopover = true
}
.popover(isPresented: $showPopover) {
    PopoverContentView()
        .presentationCompactAdaptation(.popover)
}
```

---

## Alert with Actions

```swift
.alert("Delete Item?", isPresented: $showAlert) {
    Button("Delete", role: .destructive) { deleteItem() }
    Button("Cancel", role: .cancel) { }
} message: {
    Text("This action cannot be undone.")
}
```

---

## Confirmation Dialog

```swift
.confirmationDialog("Choose an option", isPresented: $showDialog) {
    Button("Option 1") { handleOption1() }
    Button("Option 2") { handleOption2() }
    Button("Cancel", role: .cancel) { }
}
```

---

## Type-Safe Routing

Always use `navigationDestination(for:)` for type-safe routing:

```swift
.navigationDestination(for: Note.self) { note in
    NoteDetailView(note: note)
}
.navigationDestination(for: Category.self) { category in
    CategoryView(category: category)
}
```
