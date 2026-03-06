# Minimalism (Functional Elegance)

Minimalist design is the art of extreme intentionality. It focuses on essential elements, high-quality typography, and purposeful whitespace to create clarity.

---

## Design DNA

| Property | Value |
|---|---|
| **Border Radius** | Subtle: 6px – 12px |
| **Borders** | Rare. Use 0.5px or 1px with low-contrast colors (e.g., #f1f1f1) |
| **Shadows** | Ambient only. Very large blur, very low opacity (2%-5%) |
| **Typography** | Inter, Geist, or Plus Jakarta Sans. Strict size scale |
| **Spacing** | Generous. gap-12, p-20. Spacing is the divider |

---

## The Quiet Palette

- Snow White: #FFFFFF
- Soft Graphite: #18181B
- Ghost Text: #71717A
- Deep Ink: #09090B

---

## Component Logic

### 1. The Border-less Content Section
```html
<section class="max-w-3xl mx-auto py-32 px-8">
    <span class="text-xs font-bold uppercase tracking-widest text-zinc-400 mb-4 block">Process</span>
    <h2 class="text-4xl font-bold tracking-tight mb-8">Refining the core.</h2>
    <p class="text-lg text-zinc-500 leading-relaxed">
        Strip away the noise until only the essence remains.
    </p>
</section>
```

### 2. The Subtle Button
```css
.btn-minimal {
    padding: 0.75rem 1.5rem;
    border-radius: 99px;
    background: #000;
    color: #fff;
    font-weight: 600;
}
```

## Layout Strategy

1. Focus on the 80/20 Rule: Only show the essential 20% of information.
2. Invisible Dividers: Use margins instead of lines.
3. Contrast as Guide: Use varying shades of gray to communicate hierarchy.

## Anti-Patterns

- Drop Shadows with Color: Shadows should always be neutral.
- Nested Boxes: Avoid "a box inside a box". Use white space.
- Icons for Everything: Use text when it is clearer.
