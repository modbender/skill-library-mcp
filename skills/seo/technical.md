# Technical SEO

## Core Web Vitals
- **LCP** (Largest Contentful Paint): < 2.5s — largest visible element load time
- **INP** (Interaction to Next Paint): < 200ms — response to user interaction
- **CLS** (Cumulative Layout Shift): < 0.1 — visual stability, no jumping content
- Test with PageSpeed Insights — field data from real users matters more than lab
- Poor CWV = ranking demotion in competitive queries

## Crawlability
- robots.txt: `Disallow: /admin/` blocks crawlers — check with `robots.txt Tester` in GSC
- NEVER block CSS/JS in robots.txt — Google needs them to render JavaScript
- Crawl budget: large sites (>10K pages) must prioritize important pages
- Orphan pages (no internal links) won't get crawled regularly
- XML sitemap: max 50K URLs or 50MB per file, link in robots.txt

## Indexing
- `noindex` meta tag: prevents indexing but wastes crawl budget
- `canonical` URL: self-referencing on all pages, cross-domain for syndicated content
- Parameter URLs (`?sort=price`) need canonical to main version
- Pagination: use rel="next"/"prev" or canonical to page 1, depending on content
- Check indexing in GSC: URL Inspection tool shows render and index status

## Mobile
- Mobile-first indexing: Google indexes mobile version, desktop secondary
- Viewport meta tag required: `<meta name="viewport" content="width=device-width, initial-scale=1">`
- Touch targets minimum 48x48px — failing this hurts mobile usability score
- No intrusive interstitials — popups that block content get demoted
- Test with Mobile-Friendly Test — failing blocks ranking in mobile search

## HTTPS
- Required for rankings — HTTP sites show "Not Secure" warning
- Mixed content (HTTP resources on HTTPS page) breaks padlock
- HSTS header: tells browsers to always use HTTPS
- After migration: 301 redirect all HTTP to HTTPS, update canonical URLs

## Speed
- TTFB < 200ms — server response time, hosting matters
- Render-blocking CSS: inline critical CSS, defer rest
- JavaScript: async/defer attributes, avoid blocking main thread
- Images: lazy load, responsive srcset, modern formats (WebP/AVIF)
- Fonts: font-display: swap prevents invisible text during load
- CDN for static assets — reduces latency globally
