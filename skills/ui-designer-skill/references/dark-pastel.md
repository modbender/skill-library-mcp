# Dark Pastel (Midnight Tones)

A sophisticated design language that combines the comfort of Dark Mode with the softness of Pastel palettes. It avoids pure black (#000000) to reduce eye strain, opting for deep, desaturated midnight tones.

## Design DNA

| Property | Value |
|---|---|
| **Base Background** | Deep Midnight: #0A0C10 or #111827 |
| **Surface Color** | Lighter Midnight: #1F2937 (Glass effect often applied) |
| **Accents** | Muted Pastels (Low saturation, high value) |
| **Borders** | Subtle rules: 1px solid rgba(255, 255, 255, 0.05) |
| **Typography** | Inter or Geist. High contrast for body text (Zinc 100-300). |

## Midnight Palette

| Component | Hex Code | Usage |
|---|---|---|
| **Canvas** | #0A0B0E | Body background |
| **Surface** | #161B22 | Card/Sidebar background |
| **Pastel Mint** | #98FB98 | Success/Primary action |
| **Pastel Rose** | #FFB6C1 | Error/Secondary action |
| **Pastel Lavender** | #E6E6FA | Metadata/Informational |

## Component Logic

### Dark Glass Card
```css
.dark-glass {
    background: rgba(31, 41, 55, 0.4);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 24px;
    color: #F3F4F6;
}
```

### Glowing Text
```css
.glow-text-mint {
    color: #98FB98;
    text-shadow: 0 0 15px rgba(152, 251, 152, 0.3);
}
```

## Layout Strategy

1. Depth through Layers: Use slightly lighter backgrounds for nested elements instead of shadows.
2. Controlled Vibrancy: Only one pastel accent per screen to maintain the "Midnight" vibe.
3. Typography Weight: Use medium to semibold for headings to ensure they "pop" against the dark background.
