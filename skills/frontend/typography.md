# Typography — Frontend

## Font Selection

**AVOID**: Inter, Roboto, Arial, Open Sans — overused, generic

**USE** distinctive fonts:

| Use Case | Recommendations |
|----------|-----------------|
| Display/Headlines | Clash Display, Cabinet Grotesk, Satoshi, Playfair Display |
| Body Text | Plus Jakarta Sans, Instrument Sans, General Sans |
| Monospace | JetBrains Mono, IBM Plex Mono, Fira Code |

## Size Scale

Use dramatic jumps, not timid increments:

```css
fontSize: {
  'base': '1rem',       /* 16px */
  '2xl': '1.5rem',      /* 24px */
  '4xl': '2.5rem',      /* 40px */
  '5xl': '3.5rem',      /* 56px — hero */
  '6xl': '4.5rem',      /* 72px — statement */
}
```

## Hierarchy Rules

1. **One hero size per page** — don't compete for attention
2. **Body text 16-18px minimum** — readability
3. **Line height 1.5-1.7 for body** — dense for headlines (1.1-1.2)
4. **Max width 65-75 characters** — optimal reading measure

## Pairing Strategy

- Contrast weights: thin display + bold body
- Contrast styles: serif headlines + geometric sans body
- Never use more than 2 font families
