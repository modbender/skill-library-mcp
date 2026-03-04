---
description: "Implementation rules for iOS accessibility (VoiceOver, Reduce Motion, Dynamic Type)"
---
# Accessibility

REDUCE MOTION:
- Check: @Environment(\.accessibilityReduceMotion) var reduceMotion
- When enabled:
  - Replace .spring() with .easeInOut(duration: 0.2)
  - Replace slide transitions with .opacity
  - Disable auto-playing animations
  - Keep functional animations (progress bars), remove decorative ones
```swift
withAnimation(reduceMotion ? .easeInOut(duration: 0.2) : .spring(response: 0.3)) {
    // state change
}
.transition(reduceMotion ? .opacity : .slide)
```

REDUCE TRANSPARENCY:
- Check: @Environment(\.accessibilityReduceTransparency) var reduceTransparency
- When enabled: use opaque backgrounds instead of materials/blur.
```swift
.background(reduceTransparency ? Color(AppTheme.Colors.surface) : .ultraThinMaterial)
```

VOICEOVER LABELS:
- All interactive elements: .accessibilityLabel("descriptive text").
- Non-obvious actions: .accessibilityHint("Double tap to delete this item").
- Decorative images: .accessibilityHidden(true).
- Informative images: .accessibilityLabel("Profile photo of John").
- Icon-only buttons: MUST have .accessibilityLabel().
```swift
Button(action: addItem) {
    Image(systemName: "plus")
}
.accessibilityLabel("Add new item")
```

GROUPING & COMBINING:
- Related content (icon + label + value): .accessibilityElement(children: .combine).
- Custom read order: .accessibilityElement(children: .ignore) + manual .accessibilityLabel.
- Cards with multiple elements: combine into single accessible element.
```swift
HStack {
    Image(systemName: "heart.fill")
    Text("Favorites")
    Spacer()
    Text("12")
}
.accessibilityElement(children: .combine)
```

ACCESSIBILITY TRAITS:
- Section headers: .accessibilityAddTraits(.isHeader)
- Buttons that play media: .accessibilityAddTraits(.startsMediaSession)
- Summary/aggregate values: .accessibilityAddTraits(.isSummaryElement)
- Selected items: .accessibilityAddTraits(.isSelected)

FOCUS MANAGEMENT:
- Use @FocusState with field enum for form navigation.
- .submitLabel(.next) to show "Next" on keyboard, .submitLabel(.done) for last field.
- Chain fields with .onSubmit { focusedField = .nextField }.
```swift
enum Field: Hashable { case name, email, password }
@FocusState private var focusedField: Field?

TextField("Name", text: $name)
    .focused($focusedField, equals: .name)
    .submitLabel(.next)
    .onSubmit { focusedField = .email }
```

DYNAMIC TYPE:
- System text styles (.body, .headline, etc.) scale automatically.
- NEVER use .font(.system(size:)) — it opts out of Dynamic Type.
- If layout breaks at large sizes: .minimumScaleFactor(0.8) as last resort.
- Test with Xcode Environment Overrides at the largest accessibility size.
- ScrollView wraps content that may overflow at large type sizes.

COLOR & CONTRAST:
- Don't use color alone for status — always pair with icon + text.
- Minimum 4.5:1 contrast for normal text, 3:1 for large text.
- .foregroundStyle(.secondary) for de-emphasized text (maintains adaptive contrast).

ACCESSIBLE CUSTOM CONTROLS:
- Custom sliders/steppers: .accessibilityValue(), .accessibilityAdjustableAction().
- Custom toggles: .accessibilityAddTraits(.isToggle), .accessibilityValue(isOn ? "on" : "off").
- Progress indicators: .accessibilityValue("\(Int(progress * 100)) percent").
