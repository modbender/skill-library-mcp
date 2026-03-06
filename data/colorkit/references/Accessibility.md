# Accessibility & Contrast

ColorKit provides industry-leading tools for ensuring UI accessibility, supporting both legacy WCAG 2.1 and modern APCA (Advanced Perceptual Contrast Algorithm) standards.

## APCA (Modern Standard)

APCA is the recommended algorithm for text contrast in modern UI design (planned for WCAG 3.0). It accounts for font size, weight, and the non-linear way humans perceive light.

### `isAPCAAccessible(on:size:weight:)`
The most powerful way to check readability.
- **`on`**: The background color.
- **`size`**: Font size in points.
- **`weight`**: Font weight (e.g., `.regular`, `.bold`).

```swift
let text = CKColor.white
let bg = CKColor.blue

if text.isAPCAAccessible(on: bg, size: 16, weight: .regular) {
    print("Readable!")
}
```

### `apcaContrast(on:)`
Returns the raw Lc (lightness contrast) value.

## WCAG 2.1 (Legacy Standard)

Used for meeting current legal requirements (AA/AAA ratings).

### `contrastRatio(with:)`
Calculates the standard contrast ratio (from 1:1 to 21:1).

```swift
let ratio = text.contrastRatio(with: bg)
// AA Large: 3.0, AA: 4.5, AAA: 7.0
```

## Luminance Helpers

- **`wcagLuminance`**: Relative luminance as defined by WCAG (0.0 to 1.0).
- **`linearLuminance`**: Physical luminance, supporting HDR values above 1.0.
