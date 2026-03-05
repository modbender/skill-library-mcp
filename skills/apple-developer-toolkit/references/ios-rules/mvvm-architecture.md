---
description: "MVVM architecture rules - @Observable ViewModels with in-memory data by default, View responsibilities, data access patterns"
---
# MVVM Architecture Rules

## ViewModel Pattern (In-Memory Default)
Every ViewModel follows this exact pattern:

```swift
import SwiftUI

@Observable
@MainActor
class NotesListViewModel {
    var notes: [Note] = Note.sampleData
    var searchText = ""

    var filteredNotes: [Note] {
        if searchText.isEmpty { return notes }
        return notes.filter { $0.title.localizedCaseInsensitiveContains(searchText) }
    }

    func addNote(title: String) {
        let note = Note(title: title)
        notes.insert(note, at: 0)
    }

    func deleteNote(_ note: Note) {
        notes.removeAll { $0.id == note.id }
    }
}
```

## ViewModel Rules
- Annotate with `@Observable` and `@MainActor`
- ViewModel files contain **ONLY** the `@Observable` class — no other type declarations
- Handle business logic: CRUD, filtering, sorting, validation
- Initialize data arrays from model's `static sampleData` so app looks alive on first launch
- May import `SwiftUI` and `UIKit` when needed for framework types, animation helpers, or required platform bridges
- Must NOT contain Views, `UIView`/`UIViewController` declarations, `body`, or `#Preview`

## View Responsibilities
- Views own `@State` for **local UI state** (sheet presented, text field binding, animation flags)
- Views reference ViewModels via `@State var viewModel = SomeViewModel()`
- Every View file **MUST** include a `#Preview` block with sample data

## Data Access Patterns
| What | Where | How |
|------|-------|-----|
| App data (default) | ViewModel | In-memory arrays initialized from sampleData |
| Simple flags/settings | View or ViewModel | `@AppStorage` |
| Transient UI state | View | `@State` |
| Persistent data (only if user asks) | ViewModel | SwiftData `@Query` / `modelContext` |
