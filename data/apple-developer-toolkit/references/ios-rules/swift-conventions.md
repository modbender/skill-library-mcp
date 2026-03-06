---
description: "Swift 6 and iOS 26+ conventions, allowed frameworks, API preferences"
---
# Swift Conventions

## Platform Requirements
- **Swift 6** language version
- **iOS 26+** deployment target
- **SwiftUI-first** architecture. UIKit is allowed only when no viable SwiftUI equivalent exists for a required feature.
- No Storyboards or XIBs

## Allowed Frameworks
Only import from this list:
- `SwiftUI`
- `Foundation`
- `SwiftData`
- `Observation`
- `OSLog` (for logging)
- `UIKit` (only for required bridges or APIs without a SwiftUI equivalent)
- `PhotosUI` (only when the app requires photo picking)
- `AVFoundation` (only when the app requires audio/video)
- `MapKit` (only when the app requires maps)
- `CoreLocation` (only when the app requires location)

## API Preferences
Use modern APIs — avoid deprecated alternatives:

| Use This | Not This |
|----------|----------|
| `foregroundStyle()` | `foregroundColor()` |
| `clipShape(.rect(cornerRadius:))` | `.cornerRadius()` |
| `@Observable` | `ObservableObject` |
| `@State` with `@Observable` | `@StateObject` |
| `.onChange(of:) { new in }` | `.onChange(of:) { old, new in }` (iOS 17+ form) |
| `.task { await … }` | `.onAppear { Task { await … } }` (use `.task` for async work) |
| `.onAppear { }` | *(acceptable for synchronous setup like passing modelContext)* |
| `NavigationStack` | `NavigationView` |

## Swift 6 Concurrency Safety

Swift 6 enables strict concurrency checking by default. All data races are compile-time errors.

### Sendable Conformance
- All types that cross isolation boundaries MUST conform to `Sendable`.
- Value types (structs, enums) with only Sendable stored properties are implicitly Sendable.
- Reference types (classes) must be `final` and have only immutable (`let`) Sendable stored properties, OR be marked `@unchecked Sendable` with manual thread safety (mutex/lock).
- Closures that cross isolation boundaries must be `@Sendable` — they cannot capture mutable local state.

### @MainActor Isolation
- ViewModels that update `@Published` or `@Observable` state MUST be annotated `@MainActor`.
- Services that read/write UI-bound state MUST be `@MainActor`.
- SwiftUI Views are implicitly `@MainActor`, so `@State var vm: SomeViewModel` works if `SomeViewModel` is `@MainActor`.
- Use `@MainActor` on the class/actor declaration, not on individual methods — partial isolation causes confusing errors.

### nonisolated Usage
- Computed properties that return Sendable values and don't access mutable actor state should be `nonisolated`.
- Protocol conformance requirements (e.g., `Hashable.hash(into:)`, `CustomStringConvertible.description`) on `@MainActor` types must be `nonisolated`.
- Use `nonisolated(unsafe)` only as a last resort for legacy API bridging.

### Crossing Isolation Boundaries
- Do not pass `@MainActor`-isolated values directly into APIs that execute in `@concurrent` contexts.
- Snapshot required values into local Sendable variables first, perform the concurrent call, then hop back to `MainActor` for state updates:
  ```swift
  // WRONG: passing actor-isolated self.items into concurrent context
  let result = await processor.process(items)

  // RIGHT: snapshot first
  let snapshot = items  // Copy Sendable data
  let result = await processor.process(snapshot)
  await MainActor.run { self.items = result }
  ```
- The `sending` parameter keyword marks closure parameters that cross isolation boundaries — use it when writing APIs that accept callbacks from different isolation domains.

### Global Variables
- Use `static let` for shared constants — `static var` is a mutable global and violates strict concurrency.
- If mutable global state is truly needed, wrap it in an `actor` or `@MainActor`-isolated type.
- `AppIntent` static properties (title, description) MUST be `static let`.

### Actor Re-entrancy
- Actor methods can suspend and resume — do not assume state is unchanged after an `await` inside an actor.
- Re-read state after suspension points; do not rely on pre-await values.

### @preconcurrency Import
- Use `@preconcurrency import FrameworkName` for frameworks not yet annotated for Sendable (e.g., some older Apple frameworks).
- This silences warnings for types the framework hasn't updated, without losing safety for your own code.

### Translation Framework
- For `.translationTask { session in ... }` flows, do NOT call `session.translate(...)` inside `@MainActor`-isolated methods.
- Perform translation work off the main actor and hop back to `@MainActor` only for UI state updates.

## Import Rules
- Start every file with the appropriate `import` statement
- Only import what's needed — don't import `SwiftUI` in a model file that only needs `Foundation`
- ViewModels may import `SwiftUI` and `UIKit` when needed for framework types or platform bridges, but must not declare Views/UIViewControllers
