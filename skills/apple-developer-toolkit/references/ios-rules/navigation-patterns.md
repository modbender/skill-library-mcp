---
description: "Navigation architecture rules - when to use NavigationStack, TabView, sheets, fullScreenCover"
---
# Navigation Pattern Rules

## Pattern Selection Guide

| Pattern | When to Use |
|---------|-------------|
| `NavigationStack` | Hierarchical drill-down (list → detail → edit) |
| `TabView` with `Tab` API | 3+ distinct top-level peer sections |
| `.sheet(item:)` | Creation forms, secondary actions, settings |
| `.fullScreenCover` | Immersive experiences (media player, onboarding) |
| `NavigationStack` + `.sheet` | Most MVPs with 2-4 features |

## NavigationStack
Use for hierarchical navigation with a back button:

```swift
NavigationStack {
    List(items) { item in
        NavigationLink(value: item) {
            ItemRow(item: item)
        }
    }
    .navigationDestination(for: Item.self) { item in
        ItemDetailView(item: item)
    }
    .navigationTitle("Items")
}
```

## TabView with Tab API
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

## Sheets
Choose the right sheet variant based on context:

- **`.sheet(item:)`** — for editing or viewing an existing item (the item drives the sheet)
- **`.sheet(isPresented:)`** — acceptable for creation forms and simple actions (no item yet)

```swift
// Editing/viewing an existing item — use item-driven
@State private var editingItem: Item?

.sheet(item: $editingItem) { item in
    EditItemView(item: item)
}

// Creating a new item — isPresented is fine
@State private var showAddItem = false

.sheet(isPresented: $showAddItem) {
    AddItemView()
}
```

## Full Screen Cover
Use for immersive content that should cover the entire screen:

```swift
@State private var showOnboarding = false

.fullScreenCover(isPresented: $showOnboarding) {
    OnboardingView()
}
```

## Type-Safe Routing
Always use `navigationDestination(for:)` for type-safe routing:

```swift
// Define route types
.navigationDestination(for: Note.self) { note in
    NoteDetailView(note: note)
}
.navigationDestination(for: Category.self) { category in
    CategoryView(category: category)
}
```
