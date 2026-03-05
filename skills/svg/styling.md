# SVG CSS Styling — currentColor & Theming Traps

## currentColor Inheritance

```svg
<svg fill="currentColor">
  <path d="..."/>
</svg>
```

```css
.icon { color: blue; }
.icon:hover { color: red; }  /* SVG changes too */
```

**This only works if:**
1. SVG is inline (not `<img>` or background)
2. No hardcoded fill in paths

## Hardcoded Fill Trap

```svg
<!-- ❌ Can't theme — fill is hardcoded -->
<svg>
  <path fill="#000000" d="..."/>
</svg>

<!-- ✅ Themeable — inherits from CSS -->
<svg fill="currentColor">
  <path d="..."/>
</svg>
```

**Figma/Illustrator exports** often hardcode fills. Remove them.

## CSS Custom Properties

For multi-color icons:

```svg
<svg>
  <style>
    .primary { fill: var(--icon-primary, currentColor); }
    .secondary { fill: var(--icon-secondary, #ccc); }
  </style>
  <path class="primary" d="..."/>
  <path class="secondary" d="..."/>
</svg>
```

```css
/* Theme from outside */
.dark-mode svg {
  --icon-primary: white;
  --icon-secondary: #666;
}
```

## Stroke vs Fill

```svg
<!-- Fill-based icon -->
<svg fill="currentColor" stroke="none">

<!-- Stroke-based icon -->
<svg fill="none" stroke="currentColor" stroke-width="2">
```

**Trap:** Mixing stroke and fill on same icon with `currentColor` — both become same color.

## Important: CSS Specificity

Inline `style` or `fill` attributes beat external CSS:

```svg
<!-- ❌ CSS can't override this -->
<path style="fill: black" d="..."/>

<!-- ✅ CSS can style this -->
<path d="..."/>
```

Clean SVG exports before using in design systems.
