# Blending & Compositing

ColorKit includes a professional blending engine that supports common Photoshop-style blend modes. These operations are performed in a device-independent color space to ensure consistent results.

## `CKBlendMode`

The following modes are supported via the `CKBlendMode` enum:

- **`.normal`**: Simple alpha compositing.
- **`.multiply`**: Multiplies the base and blend color. Always results in a darker color.
- **`.screen`**: Inverts, multiplies, and inverts again. Always results in a lighter color.
- **`.overlay`**: Combines Multiply and Screen. Preserves highlights and shadows.
- **`.darken` / `.lighten`**: Selects the darker or lighter of the two colors.
- **`.colorDodge` / `.colorBurn`**: Brightens or darkens the base color based on the blend color.
- **`.softLight` / `.hardLight`**: Variations of overlay for softer or harsher results.
- **`.difference` / `.exclusion`**: Subtracts one color from another, useful for finding variations.

## Usage

Use the `blended(with:mode:opacity:)` modifier on any `CKColor`.

```swift
let base = CKColor.gray
let highlight = CKColor.yellow.opacity(0.3)

let result = base.blended(with: highlight, mode: .overlay)
```

## Opacity & Alpha
ColorKit handles alpha correctly across all blend modes, ensuring that semi-transparent layers composite as expected.
