# Performance, SEO, and Accessibility

## Core Web Vitals

| Metric | Target | How to improve |
|--------|--------|----------------|
| LCP (Largest Contentful Paint) | < 2.5s | Preload hero image, optimize server response, avoid render-blocking JS |
| FID (First Input Delay) | < 100ms | Break up long tasks, defer non-critical JS, use web workers |
| CLS (Cumulative Layout Shift) | < 0.1 | Set explicit image dimensions, reserve space for ads/embeds |

## Image Optimization

- **Format** — Use WebP/AVIF with fallbacks; JPEG for photos, PNG only for transparency
- **Sizing** — Serve appropriately sized images; don't scale 2000px to 200px in CSS
- **Lazy loading** — Add `loading="lazy"` to below-fold images
- **Dimensions** — Always include `width` and `height` attributes to prevent CLS
- **Next.js Image** — Use `<Image>` component for automatic optimization and formats

## JavaScript Performance

- **Defer non-critical** — Use `defer` or `async` on scripts; or load at end of body
- **Code split** — Lazy-load routes and heavy components
- **Tree shake** — Use ES modules; avoid default exports from barrel files
- **Avoid layout thrashing** — Batch DOM reads before writes; avoid interleaved read-write

## SEO Essentials

- **Unique title per page** — 50-60 characters, include primary keyword
- **Meta description** — 150-160 characters, compelling for click-through
- **Semantic HTML** — `<h1>` once per page, proper heading hierarchy
- **Canonical URL** — Set `<link rel="canonical">` to prevent duplicate content
- **Open Graph tags** — `og:title`, `og:description`, `og:image` for social sharing
- **Sitemap** — Generate `sitemap.xml`, submit to Search Console
- **Robots.txt** — Don't accidentally block important pages

## Accessibility (a11y)

- **Keyboard navigation** — All interactive elements focusable and operable with keyboard
- **Color contrast** — 4.5:1 minimum for normal text, 3:1 for large text
- **Alt text** — Descriptive for content images, empty for decorative
- **Focus indicators** — Don't remove outlines; use `:focus-visible` for keyboard-only
- **ARIA labels** — Use when semantic HTML isn't enough; `aria-label`, `aria-describedby`
- **Form labels** — Every input needs associated `<label>` or `aria-label`
- **Heading order** — Don't skip levels; `<h1>` → `<h2>` → `<h3>`, not `<h1>` → `<h3>`
