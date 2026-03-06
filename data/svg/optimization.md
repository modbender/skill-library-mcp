# SVG Optimization — SVGO Traps & Performance

## SVGO Destructive Defaults

SVGO default config **breaks** functionality. Always override:

```javascript
// svgo.config.mjs
export default {
  plugins: [{
    name: 'preset-default',
    params: {
      overrides: {
        removeViewBox: false,      // NEVER remove
        removeTitle: false,        // Breaks accessibility
        removeDesc: false,         // Breaks accessibility
        cleanupIds: false,         // Breaks CSS/JS references
      }
    }
  }]
};
```

**Always verify output** — check viewBox and title exist after optimization.

## Safe to Remove

- Editor metadata (Illustrator, Sketch cruft)
- XML comments
- Empty groups `<g></g>`
- Unused `<defs>`
- Redundant attributes

Typical reduction: **50-80%** for Illustrator/Figma exports.

## Performance by Embedding Method

Benchmark (1000 icons):

| Method | Time | Use Case |
|--------|------|----------|
| `<img>` data URI | 67ms | Fastest, static |
| Inline optimized | 75ms | Dynamic styling |
| Symbol sprite | 99ms | Icon systems |
| External sprite | 126ms | Avoid in Chrome |

## Icon System Strategy

- **< 10 icons:** Inline SVG is fine
- **10-50 icons:** Symbol sprite recommended
- **> 50 icons:** Consider font icons or lazy loading

## Checking File Size

```bash
# Before
ls -la icon.svg  # 12KB

# After SVGO
npx svgo icon.svg
ls -la icon.svg  # 2KB
```

If reduction is < 30%, source was already clean.
