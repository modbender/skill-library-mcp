# Web Performance Engine

Complete web performance optimization system. Audit, diagnose, fix, and monitor — no external tools required (but integrates with Lighthouse, WebPageTest, Chrome DevTools when available).

## Phase 1: Performance Audit

### Quick Health Check

Run these checks in order. Stop when you find the bottleneck tier.

**Tier 1 — Critical (blocks rendering):**
- [ ] Time to First Byte (TTFB) > 800ms → server problem
- [ ] First Contentful Paint (FCP) > 1.8s → render-blocking resources
- [ ] Largest Contentful Paint (LCP) > 2.5s → hero element problem
- [ ] Total Blocking Time (TBT) > 200ms → JavaScript problem
- [ ] Cumulative Layout Shift (CLS) > 0.1 → layout instability
- [ ] Interaction to Next Paint (INP) > 200ms → event handler problem

**Tier 2 — Important (affects experience):**
- [ ] Page weight > 2MB
- [ ] Requests > 80
- [ ] JavaScript > 500KB (compressed)
- [ ] Images > 1MB total
- [ ] No compression (gzip/brotli)
- [ ] No caching headers

**Tier 3 — Polish (competitive edge):**
- [ ] Speed Index > 3.4s
- [ ] Time to Interactive > 3.8s
- [ ] Font loading causes flash
- [ ] Third-party scripts > 30% of JS

### Audit Brief Template

```yaml
audit:
  url: ""
  device: "mobile"  # mobile | desktop | both
  connection: "4G"  # 3G | 4G | fiber
  region: ""        # closest to target users
  
scores:
  performance: null  # 0-100
  fcp_ms: null
  lcp_ms: null
  tbt_ms: null
  cls: null
  inp_ms: null
  ttfb_ms: null
  
page_weight:
  total_kb: null
  html_kb: null
  css_kb: null
  js_kb: null
  images_kb: null
  fonts_kb: null
  other_kb: null
  
requests:
  total: null
  by_type: {}
  third_party_count: null
  third_party_kb: null
```

### Getting Metrics Without Tools

If no Lighthouse/DevTools available, use web-based tools:
1. `web_fetch "https://pagespeed.web.dev/analysis?url={encoded_url}"` — Google's free tool
2. `web_search "webpagetest {url}"` — find cached results
3. `web_search "site:{domain} core web vitals"` — find CrUX data
4. Check `<head>` for obvious issues: render-blocking CSS/JS, missing preloads, no meta viewport

## Phase 2: Diagnosis — The Performance Waterfall

### Critical Rendering Path Analysis

```
DNS → TCP → TLS → TTFB → HTML Parse → CSSOM → Render Tree → FCP → LCP
                                ↓
                         JS Download → Parse → Execute → INP
```

**Bottleneck Decision Tree:**

```
High TTFB (>800ms)?
├─ YES → Phase 3A: Server optimization
└─ NO → High FCP (>1.8s)?
    ├─ YES → Phase 3B: Render-blocking resources
    └─ NO → High LCP (>2.5s)?
        ├─ YES → Phase 3C: Hero element optimization
        └─ NO → High TBT (>200ms)?
            ├─ YES → Phase 3D: JavaScript optimization
            └─ NO → High CLS (>0.1)?
                ├─ YES → Phase 3E: Layout stability
                └─ NO → High INP (>200ms)?
                    ├─ YES → Phase 3F: Interaction optimization
                    └─ NO → ✅ Performance is good!
```

### Resource Impact Scoring

Rate each resource by impact:

| Factor | Weight | Score 1 | Score 3 | Score 5 |
|--------|--------|---------|---------|---------|
| Size (KB) | 3x | <10 | 10-100 | >100 |
| Render-blocking | 5x | No | Partial | Full |
| Above-fold impact | 4x | None | Indirect | Direct |
| Cacheable | 2x | Long cache | Short cache | No cache |
| Compressible | 2x | Already done | Possible | Not compressed |

**Priority = Sum(Factor × Weight). Fix highest scores first.**

## Phase 3: Fix Playbooks

### 3A: Server Optimization (TTFB)

**Quick wins:**
```
# CDN: If no CDN, this is #1 priority
# Check: curl -sI {url} | grep -i 'x-cache\|cf-cache\|x-cdn'

# Compression: Must have brotli or gzip
# Check: curl -sI -H "Accept-Encoding: br,gzip" {url} | grep -i content-encoding

# HTTP/2 or HTTP/3
# Check: curl -sI --http2 {url} | head -1
```

**Server-side checklist:**
- [ ] CDN in front (Cloudflare, Fastly, CloudFront)
- [ ] Brotli compression enabled (20-30% smaller than gzip)
- [ ] HTTP/2 minimum, HTTP/3 if possible
- [ ] Server-side caching (Redis, Varnish)
- [ ] Database query optimization (<50ms per query)
- [ ] Connection pooling enabled
- [ ] Edge computing for dynamic content (Workers, Lambda@Edge)

**Cache headers template:**
```
# Static assets (CSS, JS, images, fonts)
Cache-Control: public, max-age=31536000, immutable

# HTML pages
Cache-Control: public, max-age=0, must-revalidate

# API responses
Cache-Control: private, max-age=60, stale-while-revalidate=300
```

### 3B: Render-Blocking Resources (FCP)

**CSS optimization:**
```html
<!-- BEFORE: Render-blocking -->
<link rel="stylesheet" href="styles.css">

<!-- AFTER: Critical CSS inline + async load -->
<style>/* Critical above-fold CSS here (< 14KB) */</style>
<link rel="preload" href="styles.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="styles.css"></noscript>
```

**Rules:**
- Inline critical CSS (above-fold styles, < 14KB)
- Defer non-critical CSS
- Remove unused CSS (typical savings: 60-90%)
- Combine media queries
- Avoid `@import` (creates sequential loading)

**JavaScript optimization:**
```html
<!-- BEFORE: Render-blocking -->
<script src="app.js"></script>

<!-- AFTER: Non-blocking -->
<script src="app.js" defer></script>

<!-- OR: Independent scripts -->
<script src="analytics.js" async></script>
```

**Rules:**
- `defer` for app scripts (maintains order, runs after parse)
- `async` for independent scripts (analytics, ads)
- Never put `<script>` in `<head>` without defer/async
- Inline small scripts (< 1KB)

### 3C: Hero Element Optimization (LCP)

**LCP element types and fixes:**

| LCP Element | Fix |
|------------|-----|
| `<img>` | Preload + responsive + modern format |
| `<video>` poster | Preload poster image |
| CSS `background-image` | Preload + inline critical CSS |
| Text block | Preload font + font-display: optional |

**Image optimization checklist:**
```html
<!-- Optimal hero image -->
<link rel="preload" as="image" href="hero.webp" 
      imagesrcset="hero-400.webp 400w, hero-800.webp 800w, hero-1200.webp 1200w"
      imagesizes="100vw">

<img src="hero.webp" 
     srcset="hero-400.webp 400w, hero-800.webp 800w, hero-1200.webp 1200w"
     sizes="100vw"
     width="1200" height="600"
     alt="Hero description"
     fetchpriority="high"
     decoding="async">
```

**Image format decision:**
```
Photo/complex image? → WebP (25-35% smaller than JPEG)
                     → AVIF (50% smaller, but slower encode)
Simple graphic/logo? → SVG (scalable, tiny)
                    → PNG only if transparency needed
Animation?          → WebM/MP4 video (not GIF — 90% smaller)
```

**Image size targets:**
| Viewport | Max width | Target KB |
|----------|-----------|-----------|
| Mobile | 400px | < 50KB |
| Tablet | 800px | < 100KB |
| Desktop | 1200px | < 150KB |
| Hero/banner | 1600px | < 200KB |

### 3D: JavaScript Optimization (TBT)

**Bundle analysis approach:**
1. Check total JS size: `web_fetch` the page, count `<script>` tags
2. Identify large libraries (React, Lodash, Moment.js)
3. Check for duplicate code across bundles
4. Identify unused exports

**Common JS bloat and replacements:**

| Library | Size | Alternative | Size |
|---------|------|-------------|------|
| moment.js | 67KB | date-fns | 2-10KB |
| lodash (full) | 71KB | lodash-es (tree-shake) | 2-5KB |
| jQuery | 87KB | vanilla JS | 0KB |
| animate.css | 80KB | CSS animations | 1-2KB |
| chart.js | 60KB | lightweight-charts | 40KB |

**Code splitting rules:**
- Route-based splitting (each page loads its own JS)
- Component-level splitting for heavy components (modals, editors, charts)
- Dynamic import for below-fold features: `const Chart = lazy(() => import('./Chart'))`
- Vendor chunk for stable dependencies (changes rarely = long cache)

**Long task breaking:**
```javascript
// BEFORE: Blocks main thread 200ms+
function processLargeList(items) {
  items.forEach(item => heavyComputation(item));
}

// AFTER: Yields to main thread
async function processLargeList(items) {
  for (const item of items) {
    heavyComputation(item);
    // Yield every 50ms
    if (performance.now() - start > 50) {
      await scheduler.yield(); // or setTimeout(0)
      start = performance.now();
    }
  }
}
```

### 3E: Layout Stability (CLS)

**Top CLS causes and fixes:**

| Cause | Fix |
|-------|-----|
| Images without dimensions | Always set `width` + `height` |
| Ads/embeds without space | Reserve space with `aspect-ratio` or `min-height` |
| Dynamic content injection | Use CSS `contain` or reserved space |
| Web fonts causing reflow | `font-display: optional` or `swap` with size-adjust |
| Late-loading CSS | Inline critical CSS |

**Anti-CLS patterns:**
```css
/* Reserve space for dynamic content */
.ad-slot { min-height: 250px; }
.embed-container { aspect-ratio: 16/9; }

/* Prevent font swap reflow */
@font-face {
  font-family: 'Brand';
  src: url('brand.woff2') format('woff2');
  font-display: optional; /* No swap = no shift */
  size-adjust: 105%; /* Match fallback metrics */
}

/* Contain layout shifts */
.dynamic-widget {
  contain: layout;
  min-height: 200px;
}
```

### 3F: Interaction Optimization (INP)

**Event handler rules:**
- Keep handlers < 50ms
- Debounce scroll/resize (100-150ms)
- Use `requestAnimationFrame` for visual updates
- Offload heavy computation to Web Workers
- Use `content-visibility: auto` for off-screen content

**Input responsiveness:**
```javascript
// BEFORE: Blocks during type
input.addEventListener('input', (e) => {
  expensiveFilter(e.target.value); // 100ms+ 
});

// AFTER: Debounced + visual feedback
input.addEventListener('input', (e) => {
  showSpinner(); // Instant visual feedback
  debounce(() => expensiveFilter(e.target.value), 150);
});
```

## Phase 4: Resource Loading Strategy

### Preload / Prefetch / Preconnect Decision

```html
<!-- Preconnect: Third-party origins you'll need soon -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://cdn.example.com" crossorigin>

<!-- DNS-prefetch: Third-party origins you might need -->
<link rel="dns-prefetch" href="https://analytics.example.com">

<!-- Preload: Critical resources for THIS page -->
<link rel="preload" href="critical.css" as="style">
<link rel="preload" href="hero.webp" as="image">
<link rel="preload" href="brand.woff2" as="font" type="font/woff2" crossorigin>

<!-- Prefetch: Resources for NEXT page (low priority) -->
<link rel="prefetch" href="/next-page.js">

<!-- Modulepreload: ES modules -->
<link rel="modulepreload" href="app.mjs">
```

**Rules:**
- Max 3-5 preloads per page (more = competing priorities)
- Always preload: LCP image, critical font, above-fold CSS
- Preconnect to known third-party origins (max 4-6)
- Prefetch only on fast connections

### Lazy Loading Strategy

```
Above fold (viewport):     fetchpriority="high", no lazy
Below fold (1-2 screens):  loading="lazy", decoding="async"
Way below fold:            Intersection Observer, load on demand
Off-screen widgets:        content-visibility: auto
```

### Font Loading Optimization

```css
/* Optimal font loading */
@font-face {
  font-family: 'Brand';
  src: url('brand.woff2') format('woff2');
  font-display: swap;
  unicode-range: U+0000-00FF; /* Latin only if applicable */
}
```

**Font checklist:**
- [ ] WOFF2 format only (best compression)
- [ ] Subset fonts (Latin, extended only if needed)
- [ ] Max 2-3 font families
- [ ] Max 4 font files total (regular, bold, italic, bold-italic)
- [ ] Preload critical font files
- [ ] Consider system font stack for body text

**System font stacks:**
```css
/* Modern system fonts — zero network cost */
font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

/* Monospace */
font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, monospace;
```

## Phase 5: Third-Party Script Management

### Impact Assessment

```yaml
third_party_audit:
  - script: "Google Analytics 4"
    size_kb: 45
    blocks_render: false
    loads_more_scripts: true
    total_impact_kb: 90
    essential: true
    mitigation: "gtag async, delay until interaction"
    
  - script: "Intercom chat widget"
    size_kb: 200
    blocks_render: false
    loads_more_scripts: true
    total_impact_kb: 450
    essential: false
    mitigation: "Load on scroll/click, not page load"
```

**Third-party loading strategies:**
```javascript
// Strategy 1: Load on interaction
document.addEventListener('scroll', () => {
  loadThirdParty('chat-widget.js');
}, { once: true });

// Strategy 2: Load after page is idle
requestIdleCallback(() => {
  loadThirdParty('analytics.js');
});

// Strategy 3: Facade pattern (show placeholder until needed)
chatButton.addEventListener('click', () => {
  loadThirdParty('intercom.js').then(() => Intercom('show'));
});
```

**Rules:**
- Audit ALL third-party scripts quarterly
- Every script needs a business justification
- If a script loads >100KB, it needs a loading strategy
- Self-host what you can (fonts, analytics alternatives)
- Use `rel="noopener"` on all external links

## Phase 6: Mobile Performance

### Mobile-Specific Optimization

**Targets (mobile on 4G):**
| Metric | Good | Needs Work | Poor |
|--------|------|------------|------|
| FCP | < 1.8s | 1.8-3.0s | > 3.0s |
| LCP | < 2.5s | 2.5-4.0s | > 4.0s |
| TBT | < 200ms | 200-600ms | > 600ms |
| CLS | < 0.1 | 0.1-0.25 | > 0.25 |
| INP | < 200ms | 200-500ms | > 500ms |

**Mobile-specific checklist:**
- [ ] Viewport meta tag present
- [ ] Touch targets ≥ 48×48px
- [ ] No horizontal scroll
- [ ] Images responsive (srcset + sizes)
- [ ] JS budget < 300KB (compressed) on mobile
- [ ] Critical CSS < 14KB (fits in first TCP round trip)
- [ ] Avoid complex CSS (heavy animations, large box-shadows)

## Phase 7: Performance Budget

### Setting Budgets

```yaml
performance_budget:
  metrics:
    lcp_ms: 2500
    fcp_ms: 1800
    tbt_ms: 200
    cls: 0.1
    inp_ms: 200
    
  resources:
    total_kb: 1500
    js_kb: 350
    css_kb: 80
    images_kb: 800
    fonts_kb: 100
    
  requests:
    total: 60
    third_party: 15
    
  lighthouse:
    performance: 90
    accessibility: 90
    best_practices: 90
    seo: 90
```

**Budget enforcement rules:**
- Any PR that increases JS by >10KB needs justification
- LCP regression > 200ms blocks deploy
- Monthly Lighthouse audit — track trend
- Per-route budgets for SPAs (homepage stricter than admin)

### Budget Monitoring Template

```yaml
# Weekly performance check
date: "YYYY-MM-DD"
url: ""
device: "mobile"

scores:
  lighthouse: null
  lcp: null
  fcp: null
  tbt: null
  cls: null

trend: "improving | stable | degrading"
regressions: []
actions: []
```

## Phase 8: Performance Scoring Rubric

Rate the site 0-100:

| Dimension | Weight | 0-2 | 3-4 | 5 |
|-----------|--------|-----|-----|---|
| Core Web Vitals | 25% | All red | Mixed | All green |
| Page weight | 15% | >5MB | 2-5MB | <2MB |
| Caching strategy | 15% | None | Partial | Full with immutable |
| Render path | 15% | Multiple blockers | Some optimized | Clean critical path |
| Image optimization | 10% | Unoptimized | Partially | WebP/AVIF + responsive |
| JavaScript health | 10% | >1MB, no splitting | Some splitting | <350KB, code-split |
| Third-party control | 5% | Unmanaged | Some deferred | All managed + budgeted |
| Mobile experience | 5% | Desktop-only | Responsive | Mobile-first optimized |

**Score interpretation:**
- 90-100: Elite. Maintain and iterate.
- 70-89: Good. Fix the weakest dimension.
- 50-69: Needs work. Follow Phase 3 playbooks.
- <50: Critical. Start with server + render-blocking fixes.

## Phase 9: Common Architectures — Quick Wins

### Next.js / React
- Use `next/image` (auto WebP, lazy, blur placeholder)
- Enable ISR or SSG for static pages
- Use `dynamic()` for heavy components
- Check bundle with `@next/bundle-analyzer`
- Middleware for edge caching

### WordPress
- Page cache plugin (WP Super Cache, W3 Total Cache)
- Image optimization (ShortPixel, Imagify)
- Disable unused plugins (each adds JS+CSS)
- Use a CDN plugin
- Consider static generation (Simply Static)

### SPA (React/Vue/Svelte)
- Route-based code splitting (mandatory)
- SSR or SSG for SEO pages
- Service worker for repeat visits
- Skeleton screens (not spinners)
- Virtual scrolling for long lists

### Static Sites
- Already fast — focus on image optimization
- Deploy to CDN edge (Cloudflare Pages, Netlify, Vercel)
- Inline all critical CSS
- Minimal JS (< 50KB)

## Phase 10: Advanced Techniques

### Service Worker Caching

```javascript
// Cache-first for static assets
self.addEventListener('fetch', (event) => {
  if (event.request.url.match(/\.(css|js|woff2|webp|avif)$/)) {
    event.respondWith(
      caches.match(event.request).then(cached => cached || fetch(event.request))
    );
  }
});
```

### Resource Hints for Navigation

```javascript
// Predictive prefetch on hover
document.querySelectorAll('a').forEach(link => {
  link.addEventListener('mouseenter', () => {
    const prefetch = document.createElement('link');
    prefetch.rel = 'prefetch';
    prefetch.href = link.href;
    document.head.appendChild(prefetch);
  }, { once: true });
});
```

### Performance Monitoring in Production

```javascript
// Report Core Web Vitals
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    // Send to analytics
    sendToAnalytics({
      metric: entry.name,
      value: entry.value,
      rating: entry.rating, // "good" | "needs-improvement" | "poor"
    });
  }
}).observe({ type: 'largest-contentful-paint', buffered: true });
```

### Edge Cases

**Infinite scroll / pagination:**
- Virtual scrolling for >100 items
- Intersection Observer to load batches
- `content-visibility: auto` for off-screen items
- Memory management: remove far-off-screen DOM nodes

**SPAs with client-side routing:**
- Measure soft navigations (not just initial load)
- Report per-route metrics
- Prefetch likely next routes
- Keep route JS < 100KB each

**E-commerce product pages:**
- Preload first product image
- Lazy load review section, related products
- Defer recommendation engine JS
- Cache product data with stale-while-revalidate

**Media-heavy sites:**
- Lazy load everything below fold
- Use `<video>` not GIF (90% smaller)
- Adaptive quality based on connection (Network Information API)
- Progressive JPEG for large photos

## Natural Language Commands

- "Audit {url}" → Run full Phase 1 audit
- "Fix LCP on {url}" → Phase 3C playbook
- "What's slowing down {url}?" → Phase 2 diagnosis tree
- "Set performance budget for {project}" → Phase 7 template
- "Score {url}" → Phase 8 rubric
- "Optimize images on {url}" → Phase 3C image checklist
- "Reduce JavaScript on {url}" → Phase 3D JS optimization
- "Fix layout shifts on {url}" → Phase 3E CLS playbook
- "Mobile performance audit for {url}" → Phase 6
- "Third-party script audit for {url}" → Phase 5
- "Weekly performance check for {url}" → Phase 7 monitoring template
- "Compare {url1} vs {url2}" → Side-by-side audit
