# Selectors and Specificity

## Specificity Rules

- Inline styles: 1000, ID: 100, Class: 10, Element: 1—cumulative
- `:where()` has ZERO specificity—great for defaults that are easy to override
- `:is()` takes HIGHEST specificity of its arguments—can surprise you
- `!important` beats all—but avoid in component styles, breaks cascade

## Modern Selector Patterns

- `:is(h1, h2, h3)` for grouping—less repetition than commas
- `:where(.btn, .link):hover` for low-specificity shared styles
- `:has(.error)` parent selector—style parent based on child
- `:focus-visible` instead of `:focus`—keyboard only, no outline on click

## :has() Patterns

- `.card:has(img)` style card based on contents—true parent selector
- `form:has(:invalid)` style form when any input invalid
- `.item:has(+ .active)` select item BEFORE active—previous sibling
- Performance cost—use sparingly on large documents

## Pseudo-class Traps

- `:nth-child` vs `:nth-of-type`—child counts all siblings, type only same element
- `:first-child` inside wrapper—first child of wrapper, not first matching element
- `:empty` is strict—whitespace text nodes count as content, element not empty
- `:not()` doesn't add specificity in old syntax—does in modern syntax with complex selectors

## Pseudo-element Patterns

- `::before`/`::after` need `content: ""`—empty string at minimum
- Can't add pseudo-elements to `<img>`, `<input>`—replaced elements
- Double colon `::` is CSS3—single `:` still works but deprecated
- `::placeholder` for input placeholders—needs vendor prefixes in older browsers

## Attribute Selectors

- `[disabled]` has attribute—regardless of value
- `[href^="https"]` starts with—external links
- `[href$=".pdf"]` ends with—PDF downloads
- `[data-state="active" i]` case-insensitive match—the `i` flag

## Combinator Performance

- Browser matches selectors right-to-left—`.nav li a` finds all `a`, then filters
- Deep descendant selectors can be slow—`.a .b .c .d .e` is expensive
- Direct child `>` is more efficient—limits search scope
- ID selectors are fastest—but poor for reusable components

## Specificity Management

- Use BEM or similar—keeps specificity flat and predictable
- Layer: reset, base, components, utilities—utilities can override
- CSS custom properties ignore specificity—great for theming
- Use `@layer` for explicit cascade ordering—modern approach
