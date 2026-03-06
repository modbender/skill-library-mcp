# Neo-Brutalism (Digital Rawness)

A bold, high-contrast evolution of traditional brutalism, optimized for high visibility and playful digital experiences. It rejects the softness of modern web design in favor of raw energy and mathematical honesty.

---

## Design DNA

| Property | Value |
|---|---|
| **Border Radius** | Mixed: 0px (sharp) or 8px-12px (rounded-but-thick) |
| **Borders** | Mandatory: 2px – 4px Solid Black (#000000) |
| **Shadows** | Hard Offset only. No blur. shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] |
| **Typography** | Lexend, Space Grotesk, or Archivo Black. Font-black (900). |
| **Colors** | High-saturation primaries: #FFD600 (Yellow), #FF006B (Pink). |

---

## Technical Components

### 1. The Tactile Button
```html
<button class="bg-[#A3FF00] border-2 border-black px-6 py-3 font-black uppercase shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] active:shadow-none active:translate-x-[4px] active:translate-y-[4px] transition-all">
    Push Me
</button>
```

### 2. The Overlapped Card
```css
.brutal-card {
    background: #fff;
    border: 3px solid #000;
    padding: 2rem;
    box-shadow: 12px 12px 0px 0px #000;
}
.brutal-card:hover {
    transform: translate(-4px, -4px);
    box-shadow: 16px 16px 0px 0px #000;
}
```

## Motion Guidelines

- Snappy Transitions: Use cubic-bezier(0.175, 0.885, 0.32, 1.275).
- No Fades: Prefer instant color swaps or hard-edged slides.
- Micro-Hover: Elements should jump toward the user on hover.

## Anti-Patterns

- Gradients: Gradients are for soft designs. Neo-brutalism is flat.
- Blurred Shadows: If it is not hard-edged, it is not brutal.
- Subtle Borders: 1px borders will get lost. Use 2px or 4px.
