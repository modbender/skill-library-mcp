---
description: "Implementation rules for iOS gesture patterns and user interactions"
---
# Gestures

STANDARD GESTURE TABLE:

| Gesture    | SwiftUI API           | Use Case                         |
|------------|-----------------------|----------------------------------|
| Tap        | Button()              | Primary actions, navigation      |
| Long press | .contextMenu          | Secondary actions, previews      |
| Swipe      | .swipeActions         | List row actions (delete, edit)  |
| Drag       | .draggable/.dropDest  | Reorder, drag-and-drop           |
| Pull       | .refreshable          | Refresh content                  |
| Pinch      | MagnifyGesture        | Zoom images/maps                 |
| Rotate     | RotateGesture         | Rotate content                   |

BUTTON VS ONTAPGESTURE:
- ALWAYS use Button() for tappable UI elements. Never .onTapGesture on Text/Image/VStack.
- Button provides: accessibility labels, hit testing, highlight states, VoiceOver support.
- .onTapGesture only for non-button interactions (dismiss, background tap).

SWIPE ACTIONS (list rows):
- Trailing side: destructive actions (delete, archive).
- Leading side: positive/toggle actions (pin, favorite, mark read).
- Use .tint() to color-code actions.
- Destructive actions: .role(.destructive) for red styling.
```swift
.swipeActions(edge: .trailing, allowsFullSwipe: true) {
    Button(role: .destructive) {
        deleteItem(item)
    } label: {
        Label("Delete", systemImage: "trash")
    }
}
.swipeActions(edge: .leading) {
    Button {
        toggleFavorite(item)
    } label: {
        Label(item.isFavorite ? "Unfavorite" : "Favorite",
              systemImage: item.isFavorite ? "star.slash" : "star.fill")
    }
    .tint(.yellow)
}
```

CONTEXT MENUS:
- Use for secondary actions on any element (not just list rows).
- Group related actions, use Divider() between groups.
- Destructive actions go LAST with .role(.destructive).
```swift
.contextMenu {
    Button("Edit", systemImage: "pencil") { edit(item) }
    Button("Share", systemImage: "square.and.arrow.up") { share(item) }
    Divider()
    Button("Delete", systemImage: "trash", role: .destructive) { delete(item) }
}
```

GESTURE PRIORITY:
- Default: child gestures take priority over parent.
- .highPriorityGesture(): parent gesture overrides child.
- .simultaneousGesture(): both recognize at the same time.
- Use .simultaneousGesture for scroll + pinch zoom combinations.

HAPTIC FEEDBACK PAIRING:
- Tap actions: UIImpactFeedbackGenerator(style: .light) for subtle confirmation.
- Toggle/switch: UIImpactFeedbackGenerator(style: .medium).
- Destructive action: UINotificationFeedbackGenerator().notificationOccurred(.warning).
- Success completion: UINotificationFeedbackGenerator().notificationOccurred(.success).
- Selection change (picker/list): UISelectionFeedbackGenerator().selectionChanged().
- Drag start/end: UIImpactFeedbackGenerator(style: .medium).

CONFIRMATION FOR DESTRUCTIVE ACTIONS:
- Always confirm before destructive actions (delete, remove, clear all).
- Use .confirmationDialog for choices, .alert for single confirmation.
```swift
.confirmationDialog("Delete Item?", isPresented: $showDelete) {
    Button("Delete", role: .destructive) { delete(item) }
    Button("Cancel", role: .cancel) { }
}
```

PULL-TO-REFRESH:
- Use .refreshable {} on List or ScrollView for refresh.
- SwiftUI handles the indicator automatically.
- The closure should be async — SwiftUI shows/hides spinner based on task completion.

SCROLL GESTURES:
- ScrollView handles scroll automatically.
- .scrollDismissesKeyboard(.interactively) for forms with keyboard.
- .scrollIndicators(.hidden) only when indicators are visually distracting.
