# M3 Pastel Glass (Hybrid Design System)

A premium design system combining Material You (M3) geometry, Glassmorphism depth, and soft Pastel tones. Perfect for high-end dashboards and studio management tools.

---

## Design DNA

| Property | Value |
|---|---|
| **Border Radius** | Normal: 28px (M3 Large), Interactive: 12px – 16px |
| **Backdrop Blur** | 12px to 20px for glass surfaces |
| **Border** | 1px solid rgba(255, 255, 255, 0.15) (inner glow effect) |
| **Typography** | Plus Jakarta Sans or Outfit. Medium weight for clarity. |
| **Color Base** | Soft Pastels with low saturation and high value. |

---

## Color Palettes (The Pastel Spectrum)

### Pastel Blue (The Studio Theme)
```css
:root {
    --m3-blue-primary: #D1E4FF;
    --m3-blue-on-primary: #003258;
    --m3-blue-container: rgba(209, 228, 255, 0.1);
    --m3-blue-glass: rgba(209, 228, 255, 0.05);
}
```

### Pastel Purple (The Creative Theme)
```css
:root {
    --m3-purple-primary: #F7D8FF;
    --m3-purple-on-primary: #550066;
    --m3-purple-container: rgba(247, 216, 255, 0.1);
    --m3-purple-glass: rgba(247, 216, 255, 0.05);
}
```

## Component Logic

### 1. The Glass Sidebar
```css
.sidebar-glass {
    background: rgba(255, 255, 255, 0.02);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}
```

### 2. The Morphing M3 Tile
```css
.m3-tile {
    transition: all 0.4s cubic-bezier(0.2, 0, 0, 1);
    border-radius: 28px;
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(16px);
}
.m3-tile:hover {
    border-radius: 16px;
    transform: translateY(-6px) scale(1.01);
}
```

## Anti-Patterns

- Hard Blacks: Avoid #000000. Use deep navy or charcoal (#0A0B0E).
- High Saturation: Avoid neon colors. Keep everything dusty or creamy.
- Sharp Corners in Idle: M3 is fundamentally round.
- Stacking Blurs: Avoid more than 3 layers of backdrop-filter for performance.
