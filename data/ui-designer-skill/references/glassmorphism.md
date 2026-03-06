# Glassmorphism (Transparent Depth)

Glassmorphism is based on transparency and multi-layered approaches. It creates a sense of "virtual glass" by using background blur, light borders, and subtle transparency.

## Design DNA

| Property | Value |
|---|---|
| **Transparency** | Background opacity between 5% and 20% |
| **Backdrop Blur** | 10px to 30px (main depth driver) |
| **Inner Glow** | 1px solid border with light opacity (top/left light source) |
| **Depth** | Achieved through stacking multiple blurred layers |
| **Typography** | Clear, high-contrast sans-serif |

## Technical Implementation

### The Core Glass Class
```css
.glass {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(15px);
    -webkit-backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
}
```

### The Dark Glass Variant
```css
.glass-dark {
    background: rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.05);
}
```

## Critical Rules

1. Background Requirement: Glassmorphism only works against colorful or high-detail backgrounds (blobs, gradients, photography). Against solid white/black, it just looks like a gray box.
2. The Frost Effect: Do not over-blur. The goal is to see a "hint" of what is behind.
3. Contrast Management: Ensure text is always readable by adjusting the background opacity of the glass container.

## Anti-Patterns

- Flat Borders: Always use semi-transparent borders to mimic edge refraction.
- Heavy Shadows: Use very light, large-spread shadows or skip them entirely.
- Low Performance: Avoid using more than 3-5 glass layers on a single view.
