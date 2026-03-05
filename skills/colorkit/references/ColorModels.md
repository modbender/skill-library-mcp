# Color Models

ColorKit supports a wide range of color models for creation and analysis. Each model is represented by a dedicated struct and has corresponding methods on `CKColor` to extract components.

## Supported Models

### RGBA
The standard Red, Green, Blue, and Alpha model.
- `CKColor/RGBA`
- `CKColor.rgbComponents()`

### HSL
Hue, Saturation, and Lightness.
- `CKColor/HSL`
- `CKColor.hslComponents()`

### OKLAB
A perceptually uniform color space designed for human vision. Highly recommended for gamut mapping and gradients.
- `CKColor/OKLAB`
- `CKColor.okLabComponents()`

### LAB (CIE L*a*b*)
The classic device-independent color space.
- `CKColor/LAB`
- `CKColor.labComponents()`

### LCH
Luminance, Chroma, and Hue. A more intuitive way to work with LAB/OKLAB.
- `CKColor/LCH`
- `CKColor.lchComponents()`

### CMYK
Cyan, Magenta, Yellow, and Key (Black). Useful for print-related calculations.
- `CKColor/CMYK`
- `CKColor.cmykComponents()`

## Usage Example

```swift
let color = CKColor.blue

// Extract HSL components
let hsl = color.hslComponents()
print("Hue: \(hsl.hue), Saturation: \(hsl.saturation), Lightness: \(hsl.lightness)")

// Create from OKLAB
let softPink = CKColor(okL: 0.8, okA: 0.1, okB: 0.05)
```
