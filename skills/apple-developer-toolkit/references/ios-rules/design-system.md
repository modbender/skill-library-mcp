---
description: "Design system rules - AppTheme pattern, system fonts, SF Symbols, spacing conventions"
---
# Design System Rules

## AppTheme Pattern
Every app **MUST** use a centralized theme with **nested enums** for `Colors`, `Fonts`, and `Spacing`. Do NOT use a flat enum with top-level static properties.

```swift
// REQUIRED — always use nested enums
import SwiftUI

enum AppTheme {
    enum Colors {
        static let accent = Color.blue       // one accent per app
        static let textPrimary = Color.primary
        static let textSecondary = Color.secondary
        static let background = Color(.systemBackground)
        static let surface = Color(.secondarySystemBackground)
        static let cardBackground = Color(.secondarySystemGroupedBackground)
    }

    enum Fonts {
        static let largeTitle = Font.largeTitle
        static let title = Font.title
        static let headline = Font.headline
        static let body = Font.body
        static let caption = Font.caption
    }

    enum Spacing {
        static let small: CGFloat = 8
        static let medium: CGFloat = 16
        static let large: CGFloat = 24
        static let cornerRadius: CGFloat = 12
    }
}
```

```swift
// FORBIDDEN — never use flat structure
enum AppTheme {
    static let accentColor = Color.blue   // ❌ wrong
    static let spacing: CGFloat = 8       // ❌ wrong
}
```

Reference as: `AppTheme.Colors.accent`, `AppTheme.Fonts.headline`, `AppTheme.Spacing.medium`

## Typography
- **System fonts only** — use SwiftUI font styles: `.largeTitle`, `.title`, `.headline`, `.body`, `.caption`
- No custom fonts, no downloaded fonts
- Use `AppTheme.Fonts` for consistent sizing

## Icons (SF Symbols)
- **SF Symbols only** for all icons — required for every list row, button, empty state, and tab
- Reference via `Image(systemName: "symbol.name")`
- Pick domain-appropriate symbols (e.g. "checkmark.circle.fill" for todos, "note.text" for notes, "heart.fill" for favorites)
- Use `.symbolRenderingMode(.hierarchical)` or `.symbolRenderingMode(.palette)` for visual depth
- No custom icon assets unless the app concept specifically requires them

## Colors
- **One accent color** that fits the app's purpose
- Use semantic colors: `.primary`, `.secondary`, `Color(.systemBackground)`
- Do NOT add dark mode support, colorScheme checks, or custom dark/light color handling unless the user explicitly requests it

## Spacing Standards
- **16pt** standard padding (outer margins, section spacing)
- **8pt** compact spacing (between related elements)
- **24pt** large spacing (between major sections)
- Use `AppTheme.Spacing` constants throughout

## Empty States
Every list or collection MUST have an empty state. Use `ContentUnavailableView` (iOS 17+) for a polished look:

```swift
// Required — show when collection is empty
if items.isEmpty {
    ContentUnavailableView(
        "No Notes Yet",
        systemImage: "note.text",
        description: Text("Tap + to create your first note")
    )
} else {
    // Show the list
}
```

For custom empty states, use a styled VStack with SF Symbol + descriptive text:

```swift
VStack(spacing: 16) {
    Image(systemName: "tray")
        .font(.system(size: 48))
        .foregroundStyle(.secondary)
    Text("Nothing here yet")
        .font(.title3)
    Text("Add your first item to get started")
        .font(.subheadline)
        .foregroundStyle(.secondary)
}
```

## Animations
Use subtle, purposeful animations for state changes and list mutations:

```swift
// Toggle/complete actions — spring animation
withAnimation(.spring) {
    item.isComplete.toggle()
}

// List insertions/removals — combine opacity + scale
.transition(.opacity.combined(with: .scale))

// Numeric text changes
.contentTransition(.numericText())

// Filter/tab changes
.animation(.default, value: selectedFilter)
```

Rules:
- **Always** use `withAnimation(.spring)` for toggle/complete state changes
- **Always** add `.transition(.opacity.combined(with: .scale))` for list add/remove
- **Never** add gratuitous motion that slows down interaction
- Keep animations subtle — `.spring` and `.default` curves only
