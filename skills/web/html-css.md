# HTML/CSS Patterns and Traps

## HTML

- **Semantic elements for SEO/a11y** — Use `<main>`, `<article>`, `<nav>`, `<header>`, `<footer>`; screen readers depend on them
- **`<button>` vs `<a>`** — Buttons for actions, anchors for navigation; mixing breaks keyboard/screen reader UX
- **`<img alt="">`** — Decorative images need empty alt (not missing); screen readers announce filename otherwise
- **Self-closing tags** — In HTML5, `<br/>` works but `<br>` is canonical; `<div/>` is WRONG (not self-closing)
- **ID must be unique** — Duplicate IDs break `querySelector`, labels, and ARIA; use classes for styling
- **`<input type="number">`** — Allows `e`, `+`, `-` characters; validate server-side for real numbers
- **Hidden content still in DOM** — `display: none` hides from screen readers; `visibility: hidden` doesn't remove from flow

## CSS

- **`margin: auto` needs width** — Won't center without explicit `width` or `max-width` on block elements
- **`z-index` needs position** — Only works on positioned elements (`relative`, `absolute`, `fixed`, `sticky`)
- **Flexbox gap support** — `gap` works in flexbox in all modern browsers; no need for margin hacks
- **Grid auto-fit vs auto-fill** — `auto-fit` collapses empty tracks; `auto-fill` preserves them
- **`100vh` on mobile** — Includes address bar; use `100dvh` or JS for true viewport height
- **`:focus-visible`** — Shows focus ring only for keyboard users; cleaner than removing `:focus` outlines
- **Cascade layers** — `@layer` controls specificity across files; newer than `!important` hacks
- **Custom properties scope** — CSS variables cascade; define on `:root` for global, on element for local
- **`calc()` whitespace** — `calc(100% -20px)` fails; needs spaces: `calc(100% - 20px)`
- **Transform origin** — Default is center; for corner rotations, set `transform-origin: top left`
