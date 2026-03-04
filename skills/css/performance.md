# Performance Optimization

## Render Pipeline Understanding

- Style → Layout → Paint → Composite—changes early in pipeline are expensive
- `transform` and `opacity` only trigger composite—cheapest animations
- `width`, `height`, `margin` trigger layout—expensive, avoid animating
- `background-color`, `box-shadow` trigger paint—moderate cost

## Containment

- `contain: layout` isolates layout calculations—changes inside don't affect outside
- `contain: paint` creates paint boundary—clips like overflow:hidden
- `contain: strict` is all containment—maximum isolation, use on independent widgets
- `content-visibility: auto` skips rendering offscreen—huge savings on long pages

## Animation Performance

- Only animate `transform` and `opacity`—everything else causes repaint
- Use `will-change: transform` to hint—but creates layer, uses memory
- Don't overuse `will-change`—hundreds of layers = memory issues
- `transform: translateZ(0)` to force layer—but prefer `will-change`

## Layout Thrashing

- Reading layout property forces synchronous layout—batch reads together
- Write all changes, then read if needed—don't interleave
- Use `requestAnimationFrame` for visual changes—batches with next frame
- Virtual DOM frameworks handle this—but still know the concept

## Selector Performance

- Right-to-left matching—browser finds all matches of rightmost, filters up
- Qualified selectors slower—`div.class` slower than `.class`
- Deep nesting expensive—`.a .b .c .d .e` searches a lot
- ID selectors fastest but least reusable

## Font Loading

- FOUT (Flash of Unstyled Text) with `font-display: swap`—shows fallback first
- FOIT (Flash of Invisible Text) with `block`—text hidden until loaded
- `font-display: optional` best for performance—may not show custom font
- Preload critical fonts: `<link rel="preload" as="font" crossorigin>`

## CSS File Optimization

- Unused CSS still downloaded and parsed—audit and remove
- `@import` is render-blocking—use `<link>` tags instead
- Critical CSS inline in `<head>`—rest can load async
- Consider CSS-in-JS tradeoffs—runtime cost vs HTTP cache

## Paint Optimization

- `box-shadow` on scroll elements is expensive—moves repaint on scroll
- Large `border-radius` with overflow can be costly
- `filter: blur()` on large elements expensive
- Use compositor-only properties when possible

## Measuring Performance

- Chrome DevTools Performance panel—see paint, layout, script timing
- "Show paint rectangles"—visualize what's being repainted
- Lighthouse for overall audit—catches common issues
- Test on real low-end devices—your MacBook is not representative
