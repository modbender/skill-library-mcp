# Animation — Frontend

## Priority

One orchestrated page load > scattered micro-interactions.

## High-Impact Moments

1. **Staggered hero reveals** — content fades in sequence
2. **Scroll-triggered sections** — elements enter on scroll
3. **Hover state surprises** — scale, shadow, color shift
4. **Page transitions** — smooth route changes

## Framer Motion Example

```tsx
const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1 }
  }
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 }
}

<motion.div variants={container} initial="hidden" animate="show">
  {items.map(i => <motion.div key={i} variants={item} />)}
</motion.div>
```

## Timing Guidelines

| Type | Duration |
|------|----------|
| Interactions (hover, click) | 150-300ms |
| Transitions (page, modal) | 300-500ms |
| Complex sequences | 500-800ms total |

## Accessibility

Always respect `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; }
}
```
