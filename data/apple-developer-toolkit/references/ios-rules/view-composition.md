---
description: "View composition rules - @ViewBuilder computed properties, section naming, extraction guidelines"
---
# View Composition Rules

## @ViewBuilder Computed Properties
Every meaningful section of a view should be a `@ViewBuilder` computed property:

```swift
struct TaskListView: View {
    var body: some View {
        NavigationStack {
            VStack {
                headerView
                taskList
                addButton
            }
        }
    }

    private var headerView: some View {
        Text("My Tasks")
            .font(.largeTitle)
            .padding()
    }

    private var taskList: some View {
        List(tasks) { task in
            TaskRow(task: task)
        }
    }

    private var addButton: some View {
        Button("Add Task") {
            showAddSheet = true
        }
        .buttonStyle(.borderedProminent)
    }
}
```

## Size Guidelines
- Each computed property: **15-40 lines**
- If a section exceeds 40 lines, extract it to a separate struct
- If a section is reused in multiple views, extract to a separate file

## Section Naming Pattern
Use descriptive suffixes:
- `headerSection`, `headerView` — top area
- `contentSection`, `contentView` — main content
- `footerSection` — bottom area
- `{feature}Section` — feature-specific (e.g., `profileSection`, `statsSection`)
- `{action}Button` — action buttons (e.g., `addButton`, `saveButton`)

## When to Extract to Separate Struct
Extract a section into its own `View` struct when:
1. It exceeds **40 lines** of code
2. It's **reused** across multiple views
3. It has its own **state** (needs `@State` or `@Binding`)
4. It represents a **distinct UI component** (e.g., a card, a row)

## Body Should Only Contain Property References
The `body` property should be a composition of computed properties — not raw implementation:

```swift
// Good — body is a clear outline
var body: some View {
    ScrollView {
        headerSection
        featureCards
        recentActivity
    }
}

// Bad — body contains raw implementation
var body: some View {
    ScrollView {
        VStack(alignment: .leading) {
            Text("Welcome")
                .font(.largeTitle)
            // ... 50 more lines
        }
    }
}
```
