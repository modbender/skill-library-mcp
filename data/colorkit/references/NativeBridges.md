# Native Bridges & UI Integration

ColorKit is designed to be the "glue" between your color logic and Apple's UI frameworks.

## SwiftUI Integration

### `ShapeStyle` Conformance
On supported platforms (iOS 15+, macOS 12+), `CKColor` conforms to `ShapeStyle` and `HierarchicalShapeStyle`. You can use it directly in `.fill()`, `.foregroundStyle()`, etc.

```swift
Circle()
    .fill(CKColor.blue)
```

### SwiftUI `Color`
Use the `.color` property to get a native SwiftUI `Color` object.

```swift
Text("Hello")
    .foregroundColor(myCKColor.color)
```

## UIKit & AppKit

### `nativeColor`
Returns the platform-specific color type: `UIColor` on iOS/tvOS/watchOS and `NSColor` on macOS.

```swift
view.backgroundColor = myCKColor.nativeColor
```

## Core Graphics & Core Image

- **`cgColor`**: Returns a `CGColor` representation.
- **`ciColor`**: Returns a `CIColor` representation.

```swift
let layer = CALayer()
layer.backgroundColor = myCKColor.cgColor
```

## Native Color Extension
You can also initialize a `CKColor` from any native color:

```swift
let fromSwiftUI = CKColor(Color.red)
let fromUIKit = CKColor(uiColor: .systemBlue)
```
