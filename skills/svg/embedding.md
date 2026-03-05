# SVG Embedding Methods — Choosing Wrong = No Styling

## Method Comparison

| Method | CSS Styling | Caching | Animation | JS Access |
|--------|-------------|---------|-----------|-----------|
| Inline `<svg>` | ✅ Full | ❌ No | ✅ Yes | ✅ Yes |
| `<img src>` | ❌ No | ✅ Yes | ❌ No | ❌ No |
| `<use>` sprite | ⚠️ Partial | ✅ Yes | ⚠️ Limited | ❌ No |
| CSS background | ❌ No | ✅ Yes | ❌ No | ❌ No |
| `<object>` | ⚠️ Scoped | ✅ Yes | ✅ Yes | ⚠️ Complex |

## The Styling Trap

```html
<!-- ❌ Cannot change color with CSS -->
<img src="icon.svg" class="icon">

<!-- ❌ Cannot change color with CSS -->
<div style="background-image: url(icon.svg)"></div>

<!-- ✅ Full CSS control -->
<svg class="icon">...</svg>
```

**Rule:** If you need CSS styling → must use inline SVG or `<use>` sprites.

## xmlns Requirement

External `.svg` files **require** xmlns:

```svg
<!-- ✅ Works as external file -->
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">

<!-- ❌ May fail when loaded externally -->
<svg viewBox="0 0 24 24">
```

Inline SVG in HTML5 doesn't require xmlns (but doesn't hurt).

## Symbol Sprite Pattern

```html
<!-- Hidden sprite (once in page) -->
<svg style="display:none">
  <symbol id="icon-home" viewBox="0 0 24 24">
    <path d="..."/>
  </symbol>
</svg>

<!-- Use anywhere -->
<svg class="icon"><use href="#icon-home"/></svg>
```

**Trap:** `xlink:href` is deprecated. Use `href` for modern browsers.

## External Sprite CORS

```html
<!-- ❌ Fails cross-origin without CORS -->
<use href="https://cdn.example.com/sprites.svg#icon"/>
```

External sprites must be same-origin or CORS-enabled.
