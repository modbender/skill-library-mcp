# Mobile-First Patterns — Frontend

## Breakpoints

```css
/* Mobile first — enhance upward */
@media (min-width: 640px) { /* sm: tablet */ }
@media (min-width: 768px) { /* md: landscape tablet */ }
@media (min-width: 1024px) { /* lg: laptop */ }
@media (min-width: 1280px) { /* xl: desktop */ }
```

## Layout Transformations

| Pattern | Desktop | Mobile |
|---------|---------|--------|
| Hero with image | 2-column grid | Stack, image below |
| Feature grid | 3-4 columns | Single column |
| Sidebar + content | Side-by-side | Sheet/drawer |
| Data tables | Full table | Card view |
| Multi-column forms | Side-by-side | Stack vertically |

## Touch Targets

- Minimum **44x44px** for all interactive elements
- **8px minimum** spacing between targets
- Swipe actions need visual hints

## Font Scaling

```css
@media (max-width: 768px) {
  .hero-title { font-size: 32px; }
  .section-title { font-size: 24px; }
}
```

## Common Fixes

| Issue | Fix |
|-------|-----|
| Hero grid breaks | Use flex instead of grid on mobile |
| Horizontal scroll | Set `overflow-x: hidden` on body |
| Tiny touch targets | Add padding, not just visual size |
| Text overflow | Use `break-words` and fluid typography |
