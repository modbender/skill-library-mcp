---
description: "File organization rules - max 150 lines, body as TOC of computed properties, extension splitting"
---
# File Structure Rules

## Line Limit
- **Target**: 150 lines per file — aim for this
- **Hard limit**: 200 lines — files exceeding 200 lines MUST be split using extensions (`View+Sections.swift`)
- Files between 150-200 lines are acceptable if splitting would hurt readability

## Body as Table of Contents
The `body` property should read like a table of contents — only referencing computed properties, not containing implementation:

```swift
// Good
var body: some View {
    VStack {
        headerSection
        contentSection
        footerSection
    }
}

// Bad — implementation directly in body
var body: some View {
    VStack {
        HStack {
            Image(systemName: "person")
            Text(user.name)
                .font(.headline)
            Spacer()
            Button("Edit") { showEdit = true }
        }
        // ... 80+ more lines
    }
}
```

## Extension Splitting Pattern
When a view grows beyond 150 lines, split into extensions by section:

```swift
// ProfileView.swift — main file
struct ProfileView: View {
    @State var viewModel: ProfileViewModel

    var body: some View {
        ScrollView {
            headerSection
            statsSection
            settingsSection
        }
    }
}

// ProfileView+Sections.swift — extracted sections
extension ProfileView {
    var headerSection: some View { ... }
    var statsSection: some View { ... }
    var settingsSection: some View { ... }
}
```

## Directory Structure
```
Models/              → Data model structs (with static sampleData)
Theme/               → AppTheme.swift only
Features/<Name>/     → Co-locate View + ViewModel (e.g. Features/TodoList/TodoListView.swift)
Features/Common/     → Shared reusable views used by multiple features
App/                 → @main app entry point only
```

- NEVER use flat `Views/`, `ViewModels/`, or `Components/` top-level directories
- Every View and its ViewModel MUST live under `Features/<FeatureName>/`
- Shared components go under `Features/Common/`

## One Type Per File
- Each file contains exactly one primary type (struct, class, or enum)
- Extensions of the same type may live in separate files
- File name matches the type name: `ProfileView.swift` for `struct ProfileView`

## Naming Conventions
- Views: `{Feature}View.swift` (e.g., `NotesListView.swift`)
- ViewModels: `{Feature}ViewModel.swift` (e.g., `NotesListViewModel.swift`)
- Models: `{ModelName}.swift` (e.g., `Note.swift`)
- Theme: `AppTheme.swift`
- App entry: `{AppName}App.swift`
