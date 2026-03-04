# SVG Accessibility — Real Screen Reader Traps

## Informative vs Decorative

**Informative (conveys meaning):**
```html
<svg role="img" aria-labelledby="chart-title">
  <title id="chart-title">Sales increased 25% in Q4</title>
  <!-- paths -->
</svg>
```

**Decorative (purely visual):**
```html
<svg aria-hidden="true" focusable="false">
  <!-- paths -->
</svg>
```

## Critical Rules

| Element | Requirement |
|---------|-------------|
| `role="img"` | Required — ensures AT treats as image |
| `<title>` | Must be **first child** of `<svg>` |
| `aria-labelledby` | More reliable than `aria-label` for SVG |
| `focusable="false"` | Prevents tab stops in IE/Edge |

## ID Collision Trap

IDs must be unique across **all** inline SVGs on page:

```html
<!-- ❌ Breaks when both icons on same page -->
<svg><title id="icon">Home</title>...</svg>
<svg><title id="icon">Settings</title>...</svg>

<!-- ✅ Unique IDs -->
<svg><title id="icon-home">Home</title>...</svg>
<svg><title id="icon-settings">Settings</title>...</svg>
```

## Complex Graphics

For charts/diagrams, add `<desc>` with detailed description:

```html
<svg role="img" aria-labelledby="chart-title chart-desc">
  <title id="chart-title">Q4 Revenue</title>
  <desc id="chart-desc">Bar chart showing revenue grew from $2M to $2.5M</desc>
</svg>
```

## img Tag Trap

```html
<!-- ❌ Screen readers may announce filename -->
<img src="chart.svg">

<!-- ✅ Proper alt text -->
<img src="chart.svg" alt="Sales chart showing 25% growth">
```

When using `<img>`, accessibility comes from `alt`, not internal `<title>`.
