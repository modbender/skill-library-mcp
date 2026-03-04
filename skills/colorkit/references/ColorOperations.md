# Color Operations

`ColorKit` provides a comprehensive suite of operations for manipulating and analyzing colors, primarily via the `CKColor` struct.

## Conversions & Gamut Mapping

### `converted(to:iterations:)`
Converts a color to a target color space with optional perceptual gamut mapping.
- **`to`**: Target `CKColor.ColorSpace`.
- **`iterations`**: Number of iterations for the OKLAB-based perceptual mapping (default is 0 for simple clipping, 6+ recommended for mapping).

```swift
let p3Color = CKColor(red: 1.0, green: 0.0, blue: 0.0, colorSpace: .displayP3)
let sRGB = p3Color.converted(to: .sRGB, iterations: 8) // Perceptual mapping
```

## Blending

### `blended(with:mode:opacity:)`
Blends the current color with another using a specified `CKBlendMode`.
- **`with`**: The color to blend over the current color.
- **`mode`**: One of the many Photoshop-style modes (e.g., `.multiply`, `.overlay`, `.screen`).
- **`opacity`**: Optional alpha for the layer being blended (0.0 to 1.0).

```swift
let blended = base.blended(with: highlight, mode: .overlay, opacity: 0.8)
```

## Luminance & Lightness

- **`linearLuminance`**: Returns the linear luminance (Y) using Rec. 709 coefficients. HDR-compatible.
- **`wcagLuminance`**: Returns the relative luminance clamped to the SDR range (0-1).
- **`opacity(_:)`**: Returns a new color with the specified alpha component.

## Basic Modifications

- **`inverted()`**: Returns the color with inverted RGB components.
- **`grayscale()`**: Returns a grayscale version of the color.
