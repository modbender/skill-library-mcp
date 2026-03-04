# Material You (M3 Design Principles)

Google's Material Design 3 focus on personal, adaptive, and expressive design. It emphasizes dynamic color, organic shapes, and a systematic approach to elevation and hierarchy.

## Design DNA

| Property | Value |
|---|---|
| **Corner Radius** | Small: 8px, Medium: 12px, Large: 28px, Extra Large: 32px |
| **Elevation** | Surface tinting (tonal palettes) instead of heavy shadows |
| **Icons** | Material Symbols (Outlined, Rounded, or Sharp) |
| **Grid** | 4px Baseline grid, 8px spacing steps |
| **Typography** | Roboto or Product Sans (Google Sans) |

## Tonal Palette Logic

Hierarchy is defined by the container's tone rather than its shadow depth.

| Level | Role | Usage |
|---|---|---|
| **Primary** | Key Actions | Most prominent buttons and highlights |
| **Secondary** | Less Prominent | Supporting UI elements |
| **Tertiary** | Accent/Contrast | Contrasting elements for visual interest |
| **Surface** | Backgrounds | Main canvas and non-interactive areas |

## Components

### Floating Action Button (FAB)
```html
<button class="w-14 h-14 bg-m3-primary-container text-m3-on-primary-container rounded-[16px] shadow-md flex items-center justify-center">
    <i class="fa-solid fa-plus"></i>
</button>
```

### Large Card (M3 Standard)
```css
.m3-card-large {
    background: var(--md-sys-color-surface-variant);
    border-radius: 28px;
    padding: 1.5rem;
    border: none;
}
```

## Motion Guidelines

- Duration: Transitions typically range from 200ms to 500ms.
- Easing: Use "Emphasized" easing (`cubic-bezier(0.2, 0, 0, 1)`) for expressive movements.
- Feedback: Every interaction should trigger a ripple or scale effect.

## Anti-Patterns

- Tiny Border Radius: M3 is fundamentally based on large, comfortable curves.
- High Saturation: Unless for specific emphasis, stick to tonal ranges of a single seed color.
- Static Layouts: Design for flexibility and adaptive spacing.
