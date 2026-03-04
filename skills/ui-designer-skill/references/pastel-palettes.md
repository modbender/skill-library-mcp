# Pastel Palettes (Soft Color Theory)

Pastel colors are high-value, low-saturation tones that create a sense of calmness, creativity, and premium softness. They are essential for modern dashboard systems (M3 Pastel) and minimalist interfaces.

## Design DNA

| Property | Value |
|---|---|
| **Saturation** | Low (10% – 40%) |
| **Value (Brightness)** | High (85% – 98%) |
| **Mood** | Airy, professional, creative, non-aggressive |

## Tonal Swatches

### The "Studio Blue" Set
- Primary: #D1E4FF
- Container: #E6F0FF
- Accent: #00497D

### The "Creative Purple" Set
- Primary: #F7D8FF
- Container: #FBEAFF
- Accent: #550066

### The "Success Mint" Set
- Primary: #C4EED0
- Container: #E1F7E8
- Accent: #00210E

## Color Rules

1. Background Interaction: Always use a neutral off-white background (Slate-50 or Zinc-50) when using pastel primary colors to prevent the UI from looking "muddy."
2. Contrast Check: Ensure that the "On-Container" text color (the dark version of the pastel) has a contrast ratio of at least 4.5:1.
3. Limited Spectrum: Use no more than 3 distinct pastel hues in a single view to maintain professional clarity.

## CSS Variable Implementation

```css
:root {
    --p-blue-200: #D1E4FF;
    --p-blue-900: #003258;
    
    --p-rose-200: #FCE7F3;
    --p-rose-900: #701A75;
}

.card-pastel {
    background: var(--p-blue-200);
    color: var(--p-blue-900);
    border-radius: 20px;
    padding: 1.5rem;
}
```

## Anti-Patterns

- Neon Overload: If the color hurts the eyes, it is not a pastel.
- Black Text on Pastel: Prefer a very dark version of the same hue (e.g., Deep Navy on Pastel Blue) instead of pure black for a more "expensive" feel.
