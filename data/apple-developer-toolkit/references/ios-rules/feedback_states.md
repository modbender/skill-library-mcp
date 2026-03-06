---
description: "Implementation rules for loading states, error handling, and user feedback"
---
# Feedback States

LOADING PATTERNS:

1. Inline button spinner (action on single element):
```swift
Button {
    Task { await save() }
} label: {
    if isSaving {
        ProgressView()
            .controlSize(.small)
    } else {
        Text("Save")
    }
}
.disabled(isSaving)
```

2. Full-screen loading (initial data load):
```swift
if isLoading {
    ProgressView("Loading...")
} else {
    ContentView()
}
```

3. Skeleton loading (content placeholders):
```swift
ForEach(Item.sampleData) { item in
    ItemRow(item: item)
}
.redacted(reason: .placeholder)
```

4. Pull-to-refresh (list content):
```swift
List { ... }
    .refreshable { await viewModel.refresh() }
```

5. Overlay loading (blocking operation):
```swift
.overlay {
    if isProcessing {
        ZStack {
            Color.black.opacity(0.3)
            ProgressView()
                .controlSize(.large)
                .tint(.white)
        }
        .ignoresSafeArea()
    }
}
```

LOADING RULES:
- Show indicator for operations > 300ms.
- ALWAYS disable the triggering button while loading (prevents double-taps).
- Never block the entire UI for a partial operation — use inline spinner.
- Match loading style to scope: button-level → inline, screen-level → full-screen.

ERROR HANDLING UI:

1. Inline validation (below form fields):
```swift
if let error = emailError {
    HStack(spacing: 4) {
        Image(systemName: "exclamationmark.circle.fill")
        Text(error)
    }
    .font(.caption)
    .foregroundStyle(.red)
}
```

2. Alert for blocking errors (require user acknowledgment):
```swift
.alert("Error", isPresented: $showError) {
    Button("Retry") { Task { await retry() } }
    Button("Cancel", role: .cancel) { }
} message: {
    Text(errorMessage)
}
```

3. Banner for non-blocking errors (dismissible):
```swift
if let error = bannerError {
    HStack {
        Image(systemName: "exclamationmark.triangle.fill")
            .foregroundStyle(.orange)
        Text(error)
            .font(.subheadline)
        Spacer()
        Button("Dismiss") { bannerError = nil }
            .font(.caption)
    }
    .padding(AppTheme.Spacing.small)
    .background(.orange.opacity(0.1))
    .clipShape(RoundedRectangle(cornerRadius: 8))
    .padding(.horizontal, AppTheme.Spacing.medium)
}
```

ERROR HANDLING RULES:
- Inline validation: show immediately as user types or on field blur.
- Alert: use for errors that block progress (network failure, permission denied).
- Banner: use for non-critical errors (sync failed, partial data).
- ALWAYS provide a retry path — never leave users stuck.
- Error messages: describe what happened + what the user can do.

SUCCESS FEEDBACK:
- Haptic: UINotificationFeedbackGenerator().notificationOccurred(.success).
- Visual: brief animation (checkmark, scale bounce, color flash).
- NEVER use modal alert for success — too disruptive.
- Subtle confirmation: toast, inline checkmark, or haptic alone.
```swift
// Brief success animation
withAnimation(.spring(response: 0.3)) {
    showSuccess = true
}
DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
    withAnimation { showSuccess = false }
}
```

DISABLED STATE:
- .disabled(condition) — SwiftUI auto-handles opacity reduction.
- Always explain WHY something is disabled (tooltip, caption text, or label).
- Example: "Fill in all required fields to continue" below a disabled button.
- Don't hide actions — show them disabled with explanation.

NETWORK/SYSTEM ERROR PATTERN (ViewModel):
```swift
@MainActor @Observable
class ItemViewModel {
    var items: [Item] = []
    var isLoading = false
    var error: String?

    func loadItems() async {
        isLoading = true
        error = nil
        do {
            items = try await fetchItems()
        } catch {
            self.error = "Couldn't load items. Pull to refresh to try again."
        }
        isLoading = false
    }
}
```

EMPTY VS ERROR VS LOADING:
- Loading: ProgressView or .redacted skeleton.
- Empty (no data yet): ContentUnavailableView with action to create first item.
- Error (load failed): error message + retry button.
- These are three distinct states — never conflate them.
