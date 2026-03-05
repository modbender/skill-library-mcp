---
description: "Data storage rules - in-memory with dummy data by default, SwiftData only when user explicitly requests persistence"
---
# Storage Pattern Rules

## Default: In-Memory with Sample Data
Unless the user explicitly requests persistence (words like "save", "persist", "database", "storage", "SwiftData"), use **in-memory data with rich dummy data**:

| Data Type | Storage | API |
|-----------|---------|-----|
| App data (notes, tasks, items) | In-memory (DEFAULT) | Plain `struct`, `@Observable` arrays |
| Simple flags and settings (sort order, preferred units) | UserDefaults | `@AppStorage` |
| Transient UI state (sheet shown, selected tab) | In-memory | `@State` |

## In-Memory Models (Default)
Models are plain structs with a static `sampleData` array:

```swift
import Foundation

struct Note: Identifiable {
    let id: UUID
    var title: String
    var content: String
    var createdAt: Date
    var isPinned: Bool

    init(title: String, content: String = "", isPinned: Bool = false) {
        self.id = UUID()
        self.title = title
        self.content = content
        self.createdAt = Date()
        self.isPinned = isPinned
    }

    static let sampleData: [Note] = [
        Note(title: "Meeting Notes", content: "Discuss Q2 roadmap with the team", isPinned: true),
        Note(title: "Recipe: Pasta Carbonara", content: "Eggs, pecorino, guanciale, black pepper"),
        Note(title: "Book Recommendations", content: "The Midnight Library, Project Hail Mary"),
        Note(title: "Workout Plan", content: "Mon: Upper body, Wed: Legs, Fri: Cardio"),
        Note(title: "Gift Ideas", content: "Wireless earbuds, cookbook, plant pot"),
    ]
}
```

## In-Memory ViewModel (Default)
ViewModel holds data directly — no SwiftData, no modelContext:

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

## App Entry Point (In-Memory — No Container)
```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

## @AppStorage
Use for simple key-value settings:

```swift
@AppStorage("sortOrder") private var sortOrder = "date"
@AppStorage("showCompleted") private var showCompleted = true
```

## SwiftData (ONLY when user explicitly requests persistence)
Use `@Model`, `@Query`, `.modelContainer` ONLY if user says "save", "persist", "database", "storage", or "SwiftData":

```swift
import SwiftData

@Model
class Note {
    var title: String
    var content: String
    var createdAt: Date

    init(title: String, content: String = "") {
        self.title = title
        self.content = content
        self.createdAt = Date()
    }
}
```
