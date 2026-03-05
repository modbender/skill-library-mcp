---
description: "Performance optimization, lazy loading, image patterns, and concurrency"
---
# SwiftUI Performance Reference

Comprehensive guide to performance optimization, lazy loading, image handling, and concurrency patterns.

## Avoid Redundant State Updates

```swift
// BAD - triggers update even if value unchanged
.onReceive(publisher) { value in
    self.currentValue = value
}

// GOOD - only update when different
.onReceive(publisher) { value in
    if self.currentValue != value {
        self.currentValue = value
    }
}
```

---

## Optimize Hot Paths

```swift
// GOOD - only update when threshold crossed
.onPreferenceChange(ScrollOffsetKey.self) { offset in
    let shouldShow = offset.y <= -32
    if shouldShow != shouldShowTitle {
        shouldShowTitle = shouldShow
    }
}
```

---

## Pass Only What Views Need

```swift
// Good - pass specific values
struct SettingsView: View {
    @State private var config = AppConfig()

    var body: some View {
        VStack {
            ThemeSelector(theme: config.theme)
            FontSizeSlider(fontSize: config.fontSize)
        }
    }
}
```

---

## Equatable Views

For views with expensive bodies:

```swift
struct ExpensiveView: View, Equatable {
    let data: SomeData

    static func == (lhs: Self, rhs: Self) -> Bool {
        lhs.data.id == rhs.data.id
    }

    var body: some View { /* Expensive */ }
}

ExpensiveView(data: data).equatable()
```

---

## POD Views for Fast Diffing

POD (Plain Old Data) views use `memcmp` for fastest diffing — only simple value types, no property wrappers.

```swift
// POD view - fastest diffing
struct FastView: View {
    let title: String
    let count: Int
    var body: some View { Text("\(title): \(count)") }
}
```

**Advanced**: Wrap expensive non-POD views in POD parent views.

---

## Lazy Loading

```swift
// GOOD - creates views on demand
ScrollView {
    LazyVStack {
        ForEach(items) { item in
            ExpensiveRow(item: item)
        }
    }
}
```

---

## Task Cancellation

```swift
struct DataView: View {
    @State private var data: [Item] = []

    var body: some View {
        List(data) { item in Text(item.name) }
        .task {
            data = await fetchData()  // Auto-cancelled on disappear
        }
    }
}
```

---

## Debug View Updates

```swift
var body: some View {
    let _ = Self._printChanges()  // Prints what caused body to be called
    VStack { Text("Count: \(count)") }
}
```

---

## Eliminate Unnecessary Dependencies

```swift
// Good - narrow dependency
struct ItemRow: View {
    let item: Item
    let themeColor: Color  // Only depends on what it needs
    var body: some View {
        Text(item.name).foregroundStyle(themeColor)
    }
}
```

---

## Anti-Patterns

### Creating Objects in Body

```swift
// BAD
var body: some View {
    let formatter = DateFormatter()  // Created every body call!
    return Text(formatter.string(from: date))
}

// GOOD
private static let dateFormatter: DateFormatter = {
    let f = DateFormatter(); f.dateStyle = .long; return f
}()
```

### Heavy Computation in Body

```swift
// BAD - sorts array every body call
List(items.sorted { $0.name < $1.name }) { item in Text(item.name) }

// GOOD - compute in model
@Observable @MainActor
final class ItemsViewModel {
    var items: [Item] = []
    var sortedItems: [Item] { items.sorted { $0.name < $1.name } }
}
```

### Unnecessary State

```swift
// BAD - derived state stored separately
@State private var items: [Item] = []
@State private var itemCount: Int = 0  // Unnecessary!

// GOOD - compute derived values
var itemCount: Int { items.count }
```

---

## AsyncImage Best Practices

```swift
AsyncImage(url: imageURL) { phase in
    switch phase {
    case .empty:
        ProgressView()
    case .success(let image):
        image
            .resizable()
            .aspectRatio(contentMode: .fit)
    case .failure:
        Image(systemName: "photo")
            .foregroundStyle(.secondary)
    @unknown default:
        EmptyView()
    }
}
.frame(width: 200, height: 200)
```

---

## Image Downsampling (Optional Optimization)

When you encounter `UIImage(data:)` in scrollable lists or grids:

```swift
struct OptimizedImageView: View {
    let imageData: Data
    let targetSize: CGSize
    @State private var processedImage: UIImage?

    var body: some View {
        Group {
            if let processedImage {
                Image(uiImage: processedImage)
                    .resizable()
                    .aspectRatio(contentMode: .fit)
            } else {
                ProgressView()
            }
        }
        .task {
            processedImage = await decodeAndDownsample(imageData, targetSize: targetSize)
        }
    }

    private func decodeAndDownsample(_ data: Data, targetSize: CGSize) async -> UIImage? {
        await Task.detached {
            guard let source = CGImageSourceCreateWithData(data as CFData, nil) else { return nil }
            let options: [CFString: Any] = [
                kCGImageSourceThumbnailMaxPixelSize: max(targetSize.width, targetSize.height),
                kCGImageSourceCreateThumbnailFromImageAlways: true,
                kCGImageSourceCreateThumbnailWithTransform: true
            ]
            guard let cgImage = CGImageSourceCreateThumbnailAtIndex(source, 0, options as CFDictionary) else { return nil }
            return UIImage(cgImage: cgImage)
        }.value
    }
}
```

---

## SF Symbols

```swift
Image(systemName: "star.fill")
    .foregroundStyle(.yellow)

Image(systemName: "heart.fill")
    .symbolRenderingMode(.multicolor)

// Animated symbols (iOS 17+)
Image(systemName: "antenna.radiowaves.left.and.right")
    .symbolEffect(.variableColor)
```

---

## Common Performance Issues

- View invalidation storms from broad state changes
- Unstable identity in lists causing excessive diffing
- Heavy work in `body` (formatting, sorting, image decoding)
- Layout thrash from deep stacks or preference chains

When performance issues arise, suggest profiling with Instruments (SwiftUI template).
