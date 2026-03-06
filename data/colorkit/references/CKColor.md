# CKColor: The Core Container

`CKColor` is the primary struct in ColorKit, acting as a universal, platform-agnostic color type with advanced features.

## Initializers

### Hex Initialization
`CKColor` supports 3, 4, 6, and 8-digit hex strings, as well as integer hex values. It uniquely supports defining adaptive variants directly in the initializer.

```swift
// Basic hex
let color = CKColor(hexString: "#FF5733")

// Adaptive (Light & Dark)
let adaptive = CKColor(hexString: "#007AFF", hexStringDark: "#0A84FF")

// Full Adaptive (including High Contrast)
let full = CKColor(
    hexString: "#FFFFFF",
    hexStringDark: "#000000",
    hexStringHighContrast: "#FFFF00",
    hexStringHighContrastDark: "#00FFFF"
)
```

### Component Initialization
Initialize using standard models with optional color space and HDR headroom.

```swift
// RGB with Display P3
let p3 = CKColor(red: 1.0, green: 0.5, blue: 0.0, colorSpace: .displayP3)

// OKLAB
let oklab = CKColor(okL: 0.6, okA: 0.1, okB: 0.1)
```

## Persistence & Codable

`CKColor` is fully `Codable`. When encoded, it preserves all its dynamic variants and color space metadata. This makes it ideal for saving user preferences.

```swift
// Storing in AppStorage (via JSON encoding)
extension CKColor: RawRepresentable {
    public var rawValue: String {
        guard let data = try? JSONEncoder().encode(self),
              let result = String(data: data, encoding: .utf8) else { return "" }
        return result
    }

    public init?(rawValue: String) {
        guard let data = rawValue.data(using: .utf8),
              let result = try? JSONDecoder().decode(CKColor.self, from: data) else { return nil }
        self = result
    }
}
```

## Standard Colors

`CKColor` provides a set of standard colors that are semantically equivalent to system colors but available cross-platform:
`.red`, `.orange`, `.yellow`, `.green`, `.mint`, `.teal`, `.cyan`, `.blue`, `.indigo`, `.purple`, `.pink`, `.brown`, `.gray`, `.white`, `.black`.

## Properties

- **`color`**: Returns a SwiftUI `Color`.
- **`nativeColor`**: Returns `UIColor` (iOS/tvOS/watchOS) or `NSColor` (macOS).
- **`hexString`**: Returns the 8-digit hex representation (including alpha).
- **`isLight` / `isDark`**: Boolean checks for perceived brightness.
