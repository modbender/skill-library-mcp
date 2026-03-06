# Claymorphism (Soft 3D Design)

Claymorphism is a design trend that evolves from neumorphism, focusing on soft, inflated, 3D-like surfaces that look like they are made of clay. It uses double inner shadows to create volume and depth without the heavy outer shadows of traditional skeuomorphism.

## Design DNA

| Property | Value |
|---|---|
| **Border Radius** | Extra Large: 32px – 48px (rounded-3xl or more) |
| **Inner Shadows** | Double: One light (top-left), one dark (bottom-right) |
| **Outer Shadow** | Large, soft, floating drop shadow with low opacity |
| **Background** | Solid pastel or vivid colors |
| **Typography** | Rounded or friendly sans-serif (Quicksand, Fredoka, or Plus Jakarta Sans) |

## Color Strategy

Claymorphism works best with vibrant backgrounds and light-colored floating cards.

| Layer | Hex Code | Purpose |
|---|---|---|
| **Primary Clay** | #FFFFFF | Default card color |
| **Pastel Blue** | #E0E7FF | Soft background |
| **Vibrant Pink** | #F472B6 | Emphasis background |

## CSS Implementation

```css
.clay-card {
    background: #ffffff;
    border-radius: 40px;
    box-shadow: 
        35px 35px 70px #bebebe,
        -35px -35px 70px #ffffff,
        inset 10px 10px 20px rgba(0,0,0,0.05),
        inset -10px -10px 20px rgba(255,255,255,0.8);
    padding: 3rem;
    transition: transform 0.3s ease;
}

.clay-card:hover {
    transform: scale(1.02) translateY(-10px);
}
```

## Anti-Patterns

- No Sharp Corners: Everything must be "inflated" and round.
- No Flat Colors: Use the inner shadows to ensure volume is visible.
- No Dark Backgrounds for Cards: Clay cards are typically light or very bright; dark clay looks like heavy stone, losing the "clay" feel.
