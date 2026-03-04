---
description: "Implementation rules for UI component patterns (buttons, cards, inputs, loading)"
---
# Component Patterns

BUTTON HIERARCHY (one primary per screen/section):

| Level      | Style                | Use Case                          | Code                                              |
|------------|----------------------|-----------------------------------|----------------------------------------------------|
| Primary    | .borderedProminent   | Main action (Save, Submit, Start) | .buttonStyle(.borderedProminent).controlSize(.large)|
| Secondary  | .bordered            | Alternative action (Cancel, Edit) | .buttonStyle(.bordered)                            |
| Tertiary   | .borderless          | Low-emphasis (Skip, Learn More)   | .buttonStyle(.borderless)                          |
| Destructive| .borderedProminent   | Delete, Remove                    | .buttonStyle(.borderedProminent).tint(.red)        |

- ONE .borderedProminent per screen/section — multiple primaries confuse the user.
- Full-width primary: .controlSize(.large).frame(maxWidth: .infinity).
- ALWAYS use Button() — never .onTapGesture for actions.
- Disabled buttons: .disabled(condition) — SwiftUI auto-handles opacity.

CARD DESIGN PATTERN:
```swift
VStack(alignment: .leading, spacing: AppTheme.Spacing.xSmall) {
    HStack {
        Image(systemName: "icon.name")
            .font(.title3)
            .foregroundStyle(AppTheme.Colors.primary)
        Spacer()
        Text("metadata")
            .font(.caption)
            .foregroundStyle(.secondary)
    }
    Text("Title")
        .font(.headline)
    Text("Description text goes here")
        .font(.subheadline)
        .foregroundStyle(.secondary)
}
.padding(AppTheme.Spacing.medium)
.background(AppTheme.Colors.surface)
.clipShape(RoundedRectangle(cornerRadius: AppTheme.Style.cornerRadius))
.shadow(color: .black.opacity(0.06), radius: 8, y: 4)
```

INPUT FIELD STATES:
- Normal: TextField with .textFieldStyle(.roundedBorder).
- Focused: @FocusState with visual highlight (border color change or underline).
- Error: red border + error message below field.
```swift
TextField("Email", text: $email)
    .textFieldStyle(.roundedBorder)
    .overlay(
        RoundedRectangle(cornerRadius: 8)
            .stroke(emailError != nil ? .red : .clear, lineWidth: 1)
    )
if let error = emailError {
    Text(error)
        .font(.caption)
        .foregroundStyle(.red)
}
```
- Disabled: .disabled(true) — auto grays out.
- Form grouping: use Form or GroupBox for related fields.

LOADING STATES:

| Pattern           | Use Case                          | Code                                    |
|-------------------|-----------------------------------|-----------------------------------------|
| Inline spinner    | Button action, single item        | ProgressView().controlSize(.small)      |
| Full-screen       | Initial data load                 | ProgressView("Loading...")              |
| Pull-to-refresh   | List refresh                      | .refreshable { await refresh() }        |
| Skeleton          | Content placeholder               | .redacted(reason: .placeholder)         |
| Overlay           | Blocking operation                | .overlay { if loading { ProgressView() } } |

- Disable the triggering button while loading to prevent double-taps.
- Show loading for operations > 300ms. Instant operations need no indicator.

BADGE/CHIP PATTERN:
```swift
Text("Label")
    .font(.caption)
    .fontWeight(.medium)
    .padding(.horizontal, 8)
    .padding(.vertical, 4)
    .background(AppTheme.Colors.primary.opacity(0.15))
    .foregroundStyle(AppTheme.Colors.primary)
    .clipShape(Capsule())
```

TOGGLE/SWITCH:
- Use Toggle for binary settings with immediate effect.
- Label must clearly describe the ON state.
- Group related toggles in a Section with a header.

PICKER PATTERNS:
- 2-4 options: Picker with .segmentedStyle.
- 5+ options: Picker with default menu style or NavigationLink to selection list.
- Date selection: DatePicker with appropriate displayedComponents.

EMPTY STATES:
- Always use ContentUnavailableView for empty lists/collections.
- Include: icon (SF Symbol), title, description, and action button if applicable.
- Never show a blank screen — empty state guides the user to the first action.

DIVIDERS:
- Use sparingly — prefer spacing to create visual separation.
- In lists: SwiftUI List provides dividers automatically.
- Custom dividers: Divider() with .padding(.horizontal) for inset style.
