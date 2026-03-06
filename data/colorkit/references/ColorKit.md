# ColorKit Overview

The `ColorKit` package is a comprehensive Swift library designed for advanced color management across all Apple platforms. It extends beyond standard system colors to provide a unified API for wide-gamut color spaces, perceptual gamut mapping, HDR support, and advanced blending modes.

## Key Capabilities

- **Universal API**: A single `CKColor` type that works seamlessly across iOS, macOS, watchOS, tvOS, and visionOS.
- **Advanced Color Spaces**: Full support for sRGB, Display P3, Adobe RGB, ROMM RGB (ProPhoto), CIE L*a*b*, OKLAB, LCH, HSL, and CMYK.
- **Perceptual Accuracy**: Uses OKLAB-based gamut mapping to preserve hue and perceptual lightness when converting between wide and narrow gamuts.
- **Accessibility First**: Built-in support for WCAG 2.1 contrast ratios and the modern APCA (WCAG 3.0) algorithm for precise readability checks.
- **Dynamic & Semantic**: Define colors with variants for Light, Dark, and High Contrast modes in a single object.
- **Persistence Ready**: Full `Codable` and `Sendable` conformance for easy storage.
- **SwiftUI Integration**: Conforms to `ShapeStyle`, allowing direct use in SwiftUI views.

## Target Use Cases

- **Design Tools**: Precise color manipulation and professional blending modes.
- **Theming Systems**: Adaptive color themes that persist across user sessions.
- **Accessibility-Focused Apps**: Ensuring high standards of readability.
- **Cross-Platform Development**: Sharing color logic between iOS and macOS targets.

## Basic Example

```swift
import SwiftUI
import ColorKit

struct ColorExampleView: View {
    // A dynamic color that supports Light and Dark modes
    let brandColor = CKColor(hexString: "#007AFF", hexStringDark: "#0A84FF")
    
    var body: some View {
        VStack {
            Circle()
                .fill(brandColor) // CKColor works as a ShapeStyle
                .frame(width: 100, height: 100)
            
            Text("Perceptual Contrast")
                .foregroundColor(brandColor.color)
                .onAppear {
                    let bg = CKColor.white
                    let readable = brandColor.isAPCAAccessible(on: bg, size: 16, weight: .regular)
                    print("Is readable: \(readable)")
                }
        }
    }
}
```
