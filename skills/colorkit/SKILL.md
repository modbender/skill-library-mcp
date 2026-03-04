---
name: ColorKit
description: 'Expert guidance on ColorKit, a Swift library for advanced color manipulation, conversion, and accessibility management. Use when developers mention: (1) CKColor, CKBlendMode, CKAPCA, (2) color space conversion (OKLAB, Display P3, sRGB), (3) WCAG or APCA contrast checks, (4) hex color initialization, (5) dynamic/adaptive colors for Dark Mode, (6) perceptual gamut mapping.'
---
# ColorKit Skill

## Overview

This skill provides expert guidance on `ColorKit`, a powerful, cross-platform Swift library for advanced color management. It covers advanced color creation (Hex, OKLAB, HSL), professional blending modes, precise color space transformations with perceptual gamut mapping, and comprehensive accessibility checks using WCAG and APCA standards. Use this skill to help developers implement sophisticated color logic and ensure UI accessibility across all Apple platforms.

## Agent Behavior (Follow These Rules)

1.  **Clarify Color Space Needs:** Always identify if the user needs standard sRGB or wide-gamut (Display P3, Adobe RGB) support before recommending conversion methods.
2.  **Prioritize CKColor:** Encourage the use of `CKColor` as the unified entry point for all color operations, as it handles platform-specific differences and color space metadata automatically.
3.  **Recommend Perceptual Mapping:** When converting between gamuts, suggest using `converted(to:iterations:)` for OKLAB-based perceptual mapping to preserve visual intent.
4.  **Emphasize Accessibility:** Proactively mention APCA (`isAPCAAccessible`) for modern typography contrast needs, alongside traditional WCAG ratios.
5.  **Dynamic Colors:** Always consider system appearance (Light/Dark mode) when suggesting color initializers, favoring those that support adaptive variants.
6.  **Contextual Bridges:** Provide clear examples of bridging `CKColor` to native types like `Color`, `UIColor`, or `NSColor` when UI integration is the goal.

## Project Settings

ColorKit's behavior is influenced by the project's deployment targets and Swift version.

-   **Deployment Targets:** iOS 13.0+, macOS 10.15+, tvOS 13.0+, watchOS 6.0+, and visionOS 1.0+.
-   **Swift Version:** Requires Swift 5.9+.

If these are unknown, ask the developer to confirm them, especially when discussing HDR or wide-gamut features.

## Quick Decision Tree

When a developer needs ColorKit guidance, follow this decision tree:

1.  **Creating a new color?**
    *   From Hex string/int → `references/CKColor.md`
    *   Using specific models (OKLAB, HSL, CMYK) → `references/ColorModels.md`
    *   Adaptive for Light/Dark mode → `references/CKColor.md`

2.  **Converting between color spaces?**
    *   Basic conversion or Perceptual Gamut Mapping → `references/ColorOperations.md`
    *   Handling wide-gamut (P3, Adobe RGB) → `references/ColorOperations.md`

3.  **Performing accessibility checks?**
    *   WCAG 2.1 Contrast Ratio → `references/Accessibility.md`
    *   APCA (WCAG 3.0) Perceptual Contrast → `references/Accessibility.md`
    *   Font-specific readability → `references/Accessibility.md`

4.  **Blending or modifying colors?**
    *   Photoshop-style blending (Multiply, Overlay, etc.) → `references/Blending.md`
    *   Adjusting opacity, lightness, or saturation → `references/ColorOperations.md`

5.  **Integrating with UI frameworks?**
    *   SwiftUI (`Color`, `ShapeStyle`) → `references/NativeBridges.md`
    *   UIKit/AppKit (`UIColor`, `NSColor`) → `references/NativeBridges.md`
    *   Core Graphics/Image (`CGColor`, `CIColor`) → `references/NativeBridges.md`

6.  **Storing or persisting colors?**
    *   Using `Codable` or `Sendable` → `references/CKColor.md`

## Triage-First Playbook

-   **"My colors look different after conversion."**
    *   Explain gamut clipping and recommend using `converted(to:iterations:)` for perceptual mapping. Refer to `references/ColorOperations.md`.
-   **"How do I support Dark Mode with custom colors?"**
    *   Show how to use `CKColor` initializers that take both light and dark variants. Refer to `references/CKColor.md`.
-   **"Is my text readable on this background?"**
    *   Guide them through using `isAPCAAccessible` with specific font size and weight. Refer to `references/Accessibility.md`.
-   **"I get a compiler error when using CKColor in SwiftUI."**
    *   Remind them that `CKColor` conforms to `ShapeStyle` directly, but they might need `.color` property for some modifiers. Refer to `references/NativeBridges.md`.

## Core Patterns Reference

### Basic Initialization & Usage

```swift
import ColorKit

// Hex initialization
let brand = CKColor(hexString: "#007AFF")

// Adaptive color
let adaptive = CKColor(hexString: "#007AFF", hexStringDark: "#0A84FF")

// Use in SwiftUI
Circle().fill(adaptive)
```

### Advanced Operations

```swift
// Perceptual conversion to sRGB
let p3 = CKColor(red: 1.0, green: 0.0, blue: 0.0, colorSpace: .displayP3)
let sRGB = p3.converted(to: .sRGB, iterations: 6)

// Blending
let blended = brand.blended(with: .black, mode: .multiply, opacity: 0.5)
```

### Accessibility Check

```swift
let bg = CKColor.white
let isAccessible = brand.isAPCAAccessible(on: bg, size: 16, weight: .regular)
```

## Integration Quick Guide

ColorKit is integrated via Swift Package Manager.

1.  **Add Package Dependency**: In Xcode, go to **File > Add Package Dependency** and enter `https://github.com/SzpakKamil/ColorKit.git`.
2.  **Import**: `import ColorKit` in your Swift files.
3.  **Deployment Targets**: iOS 13.0+, macOS 10.15+, tvOS 13.0+, watchOS 6.0+, visionOS 1.0+ (Swift 5.9+).

For detailed setup, see `references/Setup.md`.

## Reference Files

Load these files as needed for specific topics:

-   **`ColorKit.md`** - General overview and key capabilities.
-   **`Setup.md`** - Installation and project integration.
-   **`CKColor.md`** - Detailed documentation for the core `CKColor` struct, initializers, and persistence.
-   **`ColorOperations.md`** - Conversion, gamut mapping, and basic modifications.
-   **`ColorModels.md`** - Using specialized models like OKLAB, HSL, CMYK, etc.
-   **`NativeBridges.md`** - Integration with SwiftUI, UIKit, AppKit, and Core Graphics.
-   **`Accessibility.md`** - WCAG and APCA contrast calculations and readability checks.
-   **`Blending.md`** - Advanced blending modes and transparency handling.
-   **`_index.md`** - A comprehensive index for all ColorKit reference documentation.

## Best Practices Summary

1.  **Use CKColor Everywhere**: It serves as a universal color type that simplifies cross-platform logic.
2.  **Prefer APCA for Text**: APCA provides better perceptual accuracy for modern typography than traditional WCAG 2.1.
3.  **Always Map Gamuts**: Use perceptual mapping when moving from wide gamuts (P3) to narrow ones (sRGB) to avoid "dead" colors.
4.  **Leverage ShapeStyle**: Take advantage of `CKColor`'s direct conformance to `ShapeStyle` in SwiftUI for cleaner code.
5.  **Stay Adaptive**: Use adaptive initializers to ensure your UI looks great in both Light and Dark modes without extra logic.


**Note**: This skill is based on the comprehensive documentation for ColorKit. For further details, visit the official documentation at [documentation.kamilszpak.com/documentation/colorkit/](https://documentation.kamilszpak.com/documentation/colorkit/) or the project website at [kamilszpak.com/pl/colorkit](https://kamilszpak.com/pl/colorkit).
