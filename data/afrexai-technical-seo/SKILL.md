---
name: Technical SEO Mastery
description: "Before a full audit, run a rapid assessment. Fetch the site and check:"
---

# Technical SEO Mastery

> Complete technical SEO audit, fix, and monitoring system. From crawlability to Core Web Vitals to international SEO — everything search engines need to find, crawl, index, and rank your site.

## When to Use

- "Technical SEO audit for my site"
- "Why isn't Google indexing my pages?"
- "Fix Core Web Vitals issues"
- "Pre-migration SEO checklist"
- "My site is slow / rankings dropped"
- "Check robots.txt / sitemap / schema markup"
- "International SEO / hreflang setup"

---

## Phase 1: Quick Health Check (5-Minute Triage)

Before a full audit, run a rapid assessment. Fetch the site and check:

```yaml
quick_health:
  url: "[domain]"
  checks:
    robots_txt: "[accessible / blocked / missing]"
    sitemap_xml: "[found / missing / errors]"
    https: "[yes / mixed content / no]"
    mobile_viewport: "[set / missing]"
    page_load: "[fast <2s / moderate 2-4s / slow >4s]"
    h1_present: "[yes / missing / multiple]"
    canonical: "[set / missing / self-referencing]"
    structured_data: "[present / missing / errors]"
  
  severity: "[healthy / needs work / critical]"
  priority_fix: "[top issue to address first]"
```

**Severity guide:**
- 🟢 Healthy: 0-1 issues — minor optimizations only
- 🟡 Needs work: 2-4 issues — schedule fixes this week
- 🔴 Critical: 5+ issues or any blocking issue — fix immediately

---

## Phase 2: Crawlability Audit

### 2.1 Robots.txt Analysis

Fetch `[domain]/robots.txt` and evaluate:

```yaml
robots_txt_audit:
  exists: true/false
  valid_syntax: true/false
  issues:
    - type: "[blocked_important_page / missing_sitemap / wildcard_block / syntax_error]"
      detail: "[specific line or pattern]"
      severity: "critical/warning/info"
      fix: "[exact fix]"
  
  checks:
    - "Sitemap directive present"
    - "No accidental blocking of CSS/JS/images"
    - "No blocking of important page directories"
    - "Correct user-agent targeting (Googlebot, Bingbot, etc.)"
    - "No conflicting rules (allow + disallow same path)"
    - "Crawl-delay only if needed (slows indexing)"
```

**Common mistakes:**
| Mistake | Impact | Fix |
|---------|--------|-----|
| `Disallow: /` blocking everything | No pages indexed | Remove or narrow scope |
| Blocking CSS/JS | Poor rendering = ranking drop | `Allow: /assets/` |
| No sitemap reference | Slower discovery | Add `Sitemap:` directive |
| Multiple sitemaps not declared | Partial crawling | Declare all sitemaps |
| Blocking search/filter pages poorly | Crawl waste | Use `Disallow: /*?` patterns |

**Recommended template:**
```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /checkout/
Disallow: /*?sort=
Disallow: /*?filter=

Sitemap: https://example.com/sitemap.xml
Sitemap: https://example.com/sitemap-images.xml
```

### 2.2 XML Sitemap Audit

Fetch sitemap(s) and evaluate:

```yaml
sitemap_audit:
  url: "[sitemap URL]"
  type: "[index / single / none]"
  url_count: 0
  issues:
    - type: "[missing / too_large / includes_noindex / stale_lastmod / broken_urls]"
      severity: "critical/warning/info"
      fix: "[specific action]"
  
  quality_checks:
    - "All URLs return 200 (no 404s, 301s, or 5xx)"
    - "No noindex pages included"
    - "lastmod dates are accurate (not all same date)"
    - "Under 50,000 URLs per sitemap file"
    - "Under 50MB uncompressed per file"
    - "Sitemap index if >50K URLs"
    - "Matches canonical URLs (not alternate versions)"
    - "Images/video sitemaps if applicable"
```

**Sitemap best practices:**
- One URL per `<url>` entry — canonical version only
- `lastmod` should reflect actual content change date
- Priority and changefreq are largely ignored by Google — optional
- Compress with gzip for large sitemaps
- Submit in Google Search Console AND robots.txt

### 2.3 Crawl Budget Optimization

```yaml
crawl_budget_analysis:
  total_pages: 0
  indexable_pages: 0
  crawl_waste_ratio: "[indexable / total — target >80%]"
  
  waste_sources:
    - source: "[faceted navigation / pagination / parameters / duplicate content / thin pages]"
      page_count: 0
      action: "[noindex / canonical / robots block / parameter handling / consolidate]"
  
  optimization_priority:
    1: "Remove/noindex thin and duplicate pages"
    2: "Consolidate parameter variations with canonicals"
    3: "Implement pagination best practices (rel=next or load-more)"
    4: "Fix redirect chains (max 1 hop)"
    5: "Eliminate orphan pages or link them into site structure"
```

**Crawl budget matters when:** Site has >10K pages OR crawl rate is notably low in Search Console.

---

## Phase 3: Indexability Audit

### 3.1 Index Status Check

For each important page type, verify:

```yaml
indexability_check:
  page_type: "[homepage / product / blog / category / landing]"
  sample_url: "[URL]"
  
  signals:
    meta_robots: "[index,follow / noindex / nofollow / none]"
    x_robots_tag: "[present / absent — check HTTP headers]"
    canonical: "[self / points to other URL / missing]"
    http_status: "[200 / 301 / 302 / 404 / 410 / 5xx]"
    in_sitemap: true/false
    internal_links_to: "[count of internal links pointing here]"
    robots_txt_allowed: true/false
  
  verdict: "[indexable / blocked / conflicting signals]"
  fix: "[action if not indexable]"
```

### 3.2 Common Indexing Blockers

| Blocker | Detection | Fix | Priority |
|---------|-----------|-----|----------|
| `noindex` meta tag | Check `<meta name="robots">` | Remove tag or move to correct pages | P0 |
| `X-Robots-Tag: noindex` header | Check HTTP response headers | Remove header from server config | P0 |
| Canonical pointing elsewhere | Check `<link rel="canonical">` | Fix to self-reference or correct target | P0 |
| Blocked in robots.txt | Cross-reference robots.txt | Update robots.txt rules | P0 |
| Not in sitemap | Check sitemap inclusion | Add to sitemap | P1 |
| No internal links (orphan) | Crawl internal link graph | Add contextual internal links | P1 |
| Soft 404 (200 with no content) | Check page content | Return proper 404 or add content | P1 |
| Duplicate content | Compare page similarity | Canonical or consolidate | P2 |
| Thin content (<200 words, no value) | Word count + quality check | Expand or merge with related page | P2 |

### 3.3 Redirect Audit

```yaml
redirect_audit:
  chains_found: 0  # A→B→C (should be A→C)
  loops_found: 0   # A→B→A (broken)
  temporary_redirects: 0  # 302s that should be 301s
  
  rules:
    - "Max 1 redirect hop (no chains)"
    - "Use 301 for permanent moves, 308 for POST-preserving"
    - "302 only for genuinely temporary redirects"
    - "Update internal links to point to final destination"
    - "Redirect HTTP → HTTPS at server level"
    - "Redirect www ↔ non-www consistently"
```

---

## Phase 4: Core Web Vitals & Performance

### 4.1 Core Web Vitals Targets

| Metric | Good | Needs Improvement | Poor |
|--------|------|-------------------|------|
| **LCP** (Largest Contentful Paint) | ≤2.5s | 2.5-4.0s | >4.0s |
| **INP** (Interaction to Next Paint) | ≤200ms | 200-500ms | >500ms |
| **CLS** (Cumulative Layout Shift) | ≤0.1 | 0.1-0.25 | >0.25 |

### 4.2 LCP Fix Playbook

```yaml
lcp_diagnosis:
  current_lcp: "[Xs]"
  lcp_element: "[identify the largest element — usually hero image or heading]"
  
  fix_priority:
    1:
      issue: "Slow server response (TTFB >800ms)"
      fixes:
        - "Enable server-side caching (Redis, Varnish)"
        - "Use CDN for static assets"
        - "Optimize database queries"
        - "Upgrade hosting if shared"
    2:
      issue: "Render-blocking resources"
      fixes:
        - "Defer non-critical CSS: `<link rel='preload' as='style'>`"
        - "Async/defer JavaScript: `<script defer>`"
        - "Inline critical CSS (above-the-fold)"
        - "Remove unused CSS/JS"
    3:
      issue: "Slow resource load (images, fonts)"
      fixes:
        - "Preload LCP image: `<link rel='preload' as='image' href='...'>`"
        - "Use WebP/AVIF format (30-50% smaller)"
        - "Responsive images with srcset"
        - "Font-display: swap for web fonts"
        - "Preconnect to CDN: `<link rel='preconnect' href='...'>`"
    4:
      issue: "Client-side rendering delay"
      fixes:
        - "Server-side render (SSR) or static generate (SSG) above-fold content"
        - "Avoid lazy-loading the LCP element"
        - "Reduce JavaScript execution before paint"
```

### 4.3 INP Fix Playbook

```yaml
inp_diagnosis:
  current_inp: "[Xms]"
  
  fix_priority:
    1: "Break long tasks (>50ms) into smaller chunks using `requestIdleCallback` or `setTimeout`"
    2: "Reduce main thread JavaScript — defer non-essential scripts"
    3: "Use `content-visibility: auto` for off-screen content"
    4: "Debounce/throttle event handlers (scroll, resize, input)"
    5: "Move heavy computation to Web Workers"
    6: "Optimize event delegation — avoid attaching listeners to every element"
    7: "Reduce DOM size (target <1,500 elements)"
```

### 4.4 CLS Fix Playbook

```yaml
cls_diagnosis:
  current_cls: "[X.XX]"
  
  common_causes:
    - cause: "Images without dimensions"
      fix: "Always set width/height attributes OR use aspect-ratio CSS"
    - cause: "Ads/embeds without reserved space"
      fix: "Use min-height on ad containers"
    - cause: "Web fonts causing FOIT/FOUT"
      fix: "`font-display: swap` + `<link rel='preload' as='font'>`"
    - cause: "Dynamically injected content above viewport"
      fix: "Reserve space or inject below the fold"
    - cause: "Late-loading CSS changing layout"
      fix: "Inline critical CSS, load rest async"
```

### 4.5 Performance Budget

```yaml
performance_budget:
  total_page_weight: "< 1.5MB (ideal < 1MB)"
  html: "< 100KB"
  css: "< 100KB (ideally < 50KB)"
  javascript: "< 300KB (compressed)"
  images: "< 500KB total above fold"
  fonts: "< 100KB (max 2 families)"
  third_party: "< 200KB total"
  
  requests:
    total: "< 50 HTTP requests"
    third_party: "< 10 external domains"
  
  timing:
    ttfb: "< 800ms"
    fcp: "< 1.8s"
    lcp: "< 2.5s"
    tti: "< 3.8s"
```

---

## Phase 5: Mobile Optimization

```yaml
mobile_audit:
  viewport_meta: "[present with correct values / missing / malformed]"
  # Correct: <meta name="viewport" content="width=device-width, initial-scale=1">
  
  checklist:
    - check: "Viewport meta tag set correctly"
      pass: true/false
    - check: "No horizontal scroll on mobile"
      pass: true/false
    - check: "Touch targets ≥48x48px with ≥8px spacing"
      pass: true/false
    - check: "Font size ≥16px base (no zoom on iOS input)"
      pass: true/false
    - check: "No fixed-width elements wider than viewport"
      pass: true/false
    - check: "Images responsive (max-width: 100%)"
      pass: true/false
    - check: "No intrusive interstitials / popups"
      pass: true/false
    - check: "Readable without zooming"
      pass: true/false
    - check: "Mobile page speed < 3s on 4G"
      pass: true/false
    - check: "No Flash or unsupported plugins"
      pass: true/false
  
  mobile_score: "[X/10]"
```

---

## Phase 6: HTTPS & Security

```yaml
security_audit:
  https:
    enabled: true/false
    certificate_valid: true/false
    certificate_expiry: "[date]"
    mixed_content: "[none / warnings / errors]"
    http_to_https_redirect: "[301 / 302 / none]"
    hsts_header: "[present with max-age / missing]"
  
  security_headers:
    - header: "Strict-Transport-Security"
      present: true/false
      recommended: "max-age=31536000; includeSubDomains; preload"
    - header: "Content-Security-Policy"
      present: true/false
      recommended: "[appropriate policy for site]"
    - header: "X-Content-Type-Options"
      present: true/false
      recommended: "nosniff"
    - header: "X-Frame-Options"
      present: true/false
      recommended: "SAMEORIGIN"
    - header: "Referrer-Policy"
      present: true/false
      recommended: "strict-origin-when-cross-origin"
    - header: "Permissions-Policy"
      present: true/false
      recommended: "camera=(), microphone=(), geolocation=()"
  
  security_score: "[X/10]"
```

**HTTPS migration checklist** (if not yet on HTTPS):
1. Obtain SSL certificate (Let's Encrypt = free)
2. Install on server / CDN
3. Update all internal links to HTTPS
4. 301 redirect all HTTP URLs to HTTPS
5. Update canonical tags to HTTPS
6. Update sitemap URLs to HTTPS
7. Update Google Search Console property
8. Update robots.txt Sitemap directive
9. Check for mixed content (HTTP resources on HTTPS pages)
10. Enable HSTS header after confirming everything works

---

## Phase 7: Structured Data / Schema Markup

### 7.1 Schema Audit

```yaml
schema_audit:
  implementation_method: "[JSON-LD / Microdata / RDFa]"  # JSON-LD recommended
  
  pages_with_schema: "[X / total pages]"
  
  schemas_found:
    - type: "[Organization / LocalBusiness / Product / Article / FAQ / etc.]"
      url: "[sample URL]"
      valid: true/false
      errors: ["[list of validation errors]"]
      warnings: ["[list of warnings]"]
  
  missing_opportunities:
    - page_type: "[product / article / recipe / event / FAQ / how-to / local]"
      recommended_schema: "[schema type]"
      rich_result_eligible: "[yes — which type]"
      priority: "high/medium/low"
```

### 7.2 Schema Templates (JSON-LD)

**Organization:**
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "[Company Name]",
  "url": "https://example.com",
  "logo": "https://example.com/logo.png",
  "sameAs": [
    "https://twitter.com/example",
    "https://linkedin.com/company/example"
  ],
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "+1-XXX-XXX-XXXX",
    "contactType": "customer service"
  }
}
```

**Article:**
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[Title]",
  "author": {"@type": "Person", "name": "[Author]"},
  "datePublished": "2026-01-15",
  "dateModified": "2026-02-18",
  "image": "https://example.com/image.jpg",
  "publisher": {
    "@type": "Organization",
    "name": "[Publisher]",
    "logo": {"@type": "ImageObject", "url": "https://example.com/logo.png"}
  }
}
```

**Product:**
```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "[Product Name]",
  "image": "https://example.com/product.jpg",
  "description": "[Description]",
  "brand": {"@type": "Brand", "name": "[Brand]"},
  "offers": {
    "@type": "Offer",
    "price": "29.99",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "url": "https://example.com/product"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "127"
  }
}
```

**FAQ:**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "[Question 1]",
      "acceptedAnswer": {"@type": "Answer", "text": "[Answer 1]"}
    }
  ]
}
```

**Rich result eligibility by schema type:**
| Schema | Rich Result | Impact |
|--------|------------|--------|
| Product | Price, rating stars, availability | High CTR boost |
| FAQ | Expandable questions in SERP | More SERP real estate |
| HowTo | Step-by-step in SERP | Featured snippet potential |
| Article | Author, date, image | News/Discover eligibility |
| LocalBusiness | Knowledge panel, maps | Local pack ranking |
| Event | Date, location, ticket info | Event carousel |
| Recipe | Cook time, rating, calories | Recipe carousel |
| Video | Thumbnail, duration | Video carousel |
| BreadcrumbList | Breadcrumb trail in SERP | Better navigation display |
| Review | Star rating | Trust + CTR |

---

## Phase 8: URL Structure & Architecture

```yaml
url_audit:
  structure_pattern: "[clean / parameter-heavy / mixed]"
  
  checklist:
    - rule: "Lowercase only (no mixed case)"
      pass: true/false
    - rule: "Hyphens as separators (not underscores)"
      pass: true/false
    - rule: "No special characters or spaces"
      pass: true/false
    - rule: "Descriptive and keyword-rich"
      pass: true/false
    - rule: "Short (< 75 characters ideal)"
      pass: true/false
    - rule: "Logical hierarchy (/category/subcategory/page)"
      pass: true/false
    - rule: "No session IDs or tracking parameters in indexed URLs"
      pass: true/false
    - rule: "Trailing slash consistent (pick one, redirect the other)"
      pass: true/false
    - rule: "No .html/.php extensions (clean URLs)"
      pass: true/false
  
  # Bad: /p?id=12345&cat=3&ref=home
  # Good: /shoes/running/nike-air-max
  
  internal_linking:
    orphan_pages: 0  # Pages with 0 internal links
    deep_pages: 0    # Pages >4 clicks from homepage
    broken_links: 0  # Internal 404s
    
    fix_priority:
      1: "Fix all broken internal links (404s)"
      2: "Link orphan pages from relevant content"
      3: "Flatten deep pages — add to navigation or hub pages"
      4: "Add contextual cross-links between related content"
```

**Site architecture best practices:**
- Flat structure: every page reachable within 3 clicks from homepage
- Hub & spoke: category pages link to all children; children link back
- Breadcrumbs: implement on every page (with BreadcrumbList schema)
- Pagination: use `rel="next"` / `rel="prev"` or infinite scroll with progressive enhancement
- Faceted navigation: canonicalize or noindex filter combinations

---

## Phase 9: International SEO

### 9.1 Hreflang Implementation

```yaml
international_seo:
  approach: "[subdirectories /en/ / subdomains en. / ccTLDs .co.uk]"
  # Recommended: subdirectories (easiest to manage, inherits domain authority)
  
  hreflang_audit:
    implemented: true/false
    method: "[HTML link tags / HTTP headers / sitemap]"
    issues:
      - "Missing return links (A→B exists but B→A missing)"
      - "Wrong language/region codes"
      - "Missing x-default tag"
      - "Self-referencing hreflang missing"
```

**Hreflang template:**
```html
<link rel="alternate" hreflang="en-us" href="https://example.com/en-us/page" />
<link rel="alternate" hreflang="en-gb" href="https://example.com/en-gb/page" />
<link rel="alternate" hreflang="es" href="https://example.com/es/page" />
<link rel="alternate" hreflang="x-default" href="https://example.com/page" />
```

**Rules:**
- Every page must reference ALL language versions including itself
- Always include `x-default` (fallback for unmatched languages)
- Use ISO 639-1 for language, ISO 3166-1 Alpha 2 for region
- Hreflang must be bidirectional (if A references B, B must reference A)
- Canonical and hreflang should align — canonical should point to same-language version

### 9.2 International Targeting Checklist

- [ ] Correct hreflang on all pages (bidirectional)
- [ ] `x-default` specified
- [ ] Content genuinely translated (not just auto-translated)
- [ ] Local currency, date format, phone numbers
- [ ] Geo-targeting set in Search Console (for ccTLDs/subdirectories)
- [ ] Local server / CDN node in target country
- [ ] Local backlinks from target region
- [ ] Language-specific sitemap or sitemap section

---

## Phase 10: Site Migration SEO Checklist

Use when changing domains, restructuring URLs, or redesigning:

```yaml
migration_checklist:
  pre_migration:
    - "Crawl current site — full URL inventory"
    - "Export all current rankings and traffic data"
    - "Map every old URL to new URL (1:1 redirect map)"
    - "Backup robots.txt, sitemaps, .htaccess"
    - "Document all existing 301 redirects"
    - "Note top 100 pages by traffic — verify redirects"
    - "Test staging site (is it blocked from indexing?)"
    - "Verify new site has all schema markup"
    - "Check canonical tags on new site"
    - "Prepare new sitemap"
  
  migration_day:
    - "Implement all 301 redirects"
    - "Update robots.txt (unblock new site)"
    - "Submit new sitemap to Search Console"
    - "Update Google Search Console property if domain changed"
    - "Verify HTTPS redirect chain is clean"
    - "Test 50 random old URLs — confirm redirects work"
    - "Check for redirect chains or loops"
    - "Monitor server errors / 5xx in real-time"
  
  post_migration:
    week_1:
      - "Monitor Search Console for crawl errors daily"
      - "Check index coverage report"
      - "Verify organic traffic hasn't cratered"
      - "Fix any 404s appearing in crawl reports"
    month_1:
      - "Compare rankings: pre vs post migration"
      - "Check all structured data still validates"
      - "Verify internal links updated (no redirect-through links)"
      - "Monitor Core Web Vitals on new infrastructure"
    month_3:
      - "Full ranking comparison"
      - "Traffic recovery assessment (expect 80-100% recovery)"
      - "Clean up any remaining redirect chains"
  
  expected_traffic_impact:
    best_case: "2-4 weeks dip, full recovery"
    typical: "1-3 months for full recovery"
    worst_case: "6+ months if redirects missed — audit immediately"
```

---

## Phase 11: Technical SEO Scoring System

### Overall Technical Health Score (0-100)

```yaml
scoring:
  crawlability:          # Weight: 20%
    robots_txt: "/5"
    sitemap: "/5"
    crawl_budget: "/5"
    internal_linking: "/5"
  
  indexability:           # Weight: 20%
    meta_robots: "/5"
    canonicals: "/5"
    redirects: "/5"
    duplicate_content: "/5"
  
  performance:            # Weight: 25%
    lcp: "/5"
    inp: "/5"
    cls: "/5"
    ttfb: "/5"
    page_weight: "/5"
  
  mobile:                 # Weight: 10%
    viewport: "/5"
    touch_targets: "/5"
    responsive: "/5"
    speed: "/5"
  
  security:               # Weight: 10%
    https: "/5"
    headers: "/5"
    certificate: "/5"
    mixed_content: "/5"
  
  structured_data:        # Weight: 10%
    implementation: "/5"
    validation: "/5"
    coverage: "/5"
    rich_results: "/5"
  
  url_architecture:       # Weight: 5%
    structure: "/5"
    depth: "/5"
    broken_links: "/5"

  total: "/100"
  grade: "[A (90+) / B (75-89) / C (60-74) / D (40-59) / F (<40)]"
```

### Priority Fix Matrix

After scoring, generate a prioritized action plan:

```yaml
action_plan:
  p0_critical:  # Fix this week — directly blocking ranking
    - issue: "[description]"
      impact: "high"
      effort: "[low/medium/high]"
      fix: "[specific steps]"
  
  p1_important:  # Fix this month — significant ranking impact
    - issue: "[description]"
      impact: "medium-high"
      effort: "[low/medium/high]"
      fix: "[specific steps]"
  
  p2_optimization:  # Fix this quarter — incremental improvement
    - issue: "[description]"
      impact: "medium"
      effort: "[low/medium/high]"
      fix: "[specific steps]"
  
  p3_nice_to_have:  # Backlog — minimal direct ranking impact
    - issue: "[description]"
      fix: "[specific steps]"
```

**Priority rules:**
- Anything blocking indexing = P0 always
- Core Web Vitals failing = P1 minimum
- Security issues = P0 if no HTTPS, P1 for headers
- Schema missing = P2 unless competitor has rich results (then P1)
- URL structure issues = P2 unless causing duplicate content

---

## Phase 12: Ongoing Monitoring

### Weekly Technical SEO Checklist

```yaml
weekly_check:
  search_console:
    - "Index coverage: any new errors?"
    - "Core Web Vitals: any regressions?"
    - "Manual actions: any penalties?"
    - "Security issues: any warnings?"
  
  site_health:
    - "Spot-check 5 random pages load correctly"
    - "Check for new 404 errors"
    - "Verify sitemap is current and accessible"
    - "Monitor HTTPS certificate expiry"
  
  tracking:
    - "Organic traffic trend (vs. last week, vs. last year)"
    - "Crawl stats in Search Console"
    - "Any new structured data errors"
```

### Monthly Deep Dive

```yaml
monthly_review:
  - "Full crawl of site — compare page count to last month"
  - "Core Web Vitals lab + field data comparison"
  - "New broken links check"
  - "Redirect chain audit"
  - "Schema markup validation"
  - "Competitor technical comparison (1 competitor)"
  - "Update sitemap if new pages added"
  - "Review Search Console performance for anomalies"
```

---

## Phase 13: Advanced Technical SEO

### 13.1 JavaScript SEO

```yaml
javascript_seo:
  rendering: "[CSR / SSR / SSG / ISR / hybrid]"
  
  checklist:
    - "Critical content visible in initial HTML (view-source test)"
    - "Googlebot can render JS — check with URL Inspection tool"
    - "No content behind user interaction (click to load)"
    - "Internal links are `<a href>` tags (not JS click handlers)"
    - "Lazy-loaded content uses Intersection Observer (not scroll events)"
    - "Dynamic rendering for critical pages if needed"
    - "Meta tags in initial HTML (not injected by JS)"
    - "Canonical tags in initial HTML"
  
  framework_specific:
    nextjs: "Use SSG/ISR for content pages, SSR for dynamic"
    react_spa: "Consider prerender.io or dynamic rendering"
    angular: "Angular Universal for SSR"
    vue: "Nuxt.js for SSR/SSG"
```

### 13.2 Log File Analysis

```yaml
log_analysis:
  what_to_look_for:
    - "Googlebot crawl frequency and pattern"
    - "Pages crawled vs not crawled"
    - "Crawl of non-canonical or low-value pages (waste)"
    - "Server errors returned to Googlebot"
    - "Response time for bot requests vs users"
    - "Bot crawl of resources (CSS/JS/images)"
  
  healthy_signals:
    - "Googlebot visits important pages frequently"
    - "New content crawled within 24-48h"
    - "Low error rate (<1% of requests)"
    - "Response time <500ms for bot requests"
  
  warning_signals:
    - "Googlebot stuck on parameter URLs"
    - "High 5xx error rate for bot"
    - "Important pages not crawled in 30+ days"
    - "Crawl rate declining over time"
```

### 13.3 Edge SEO (CDN-Level Optimizations)

| Optimization | Implementation | Impact |
|-------------|----------------|--------|
| Inject hreflang at edge | Cloudflare Workers / Lambda@Edge | Faster international SEO |
| Add schema markup | Edge injection for legacy CMS | Schema without code changes |
| Redirect management | CDN rules | Faster redirects, less server load |
| A/B test SEO changes | Edge-based split testing | Test title tags, meta descriptions |
| Pre-render for bots | Detect UA, serve cached HTML | Fix JS rendering issues |

---

## Phase 14: Common Technical SEO Mistakes

| # | Mistake | Why It Matters | Fix |
|---|---------|---------------|-----|
| 1 | Blocking staging site from indexing, forgetting to unblock at launch | Zero pages indexed | Check robots.txt + meta robots at launch |
| 2 | Using 302 instead of 301 for permanent redirects | Link equity not passed | Switch to 301 |
| 3 | Multiple versions of homepage indexed (www/non-www, HTTP/HTTPS, trailing slash) | Diluted authority | Pick one canonical, redirect all others |
| 4 | Orphan pages with no internal links | Never found by crawlers | Add to navigation or contextual links |
| 5 | Sitemap includes noindex pages | Conflicting signals | Filter sitemap to indexable pages only |
| 6 | Missing alt text on images | Accessibility + image SEO loss | Add descriptive alt text to all images |
| 7 | Not monitoring Core Web Vitals after deploy | Performance regressions | Set up CrUX monitoring + alerts |
| 8 | Redirect chains (A→B→C→D) | Slow + link equity loss | Flatten to single hop |
| 9 | Large unoptimized images | Slow LCP, page weight | WebP/AVIF + responsive srcset |
| 10 | No HTTPS or mixed content | Trust signal lost, browser warnings | Full HTTPS migration |

---

## Edge Cases

### E-commerce (1000s of product pages)
- Faceted navigation: canonical to base category, noindex filter combos
- Out-of-stock pages: keep page, show "out of stock" (don't 404)
- Pagination: use `rel=canonical` to collection page or implement load-more

### Single Page Applications (SPAs)
- Pre-rendering or SSR is mandatory for SEO
- Check that `<a href>` tags exist in HTML (not just JS routing)
- Test with JavaScript disabled — is critical content visible?

### Large sites (100K+ pages)
- Sitemap index with multiple child sitemaps
- Crawl budget optimization is critical
- Consider dynamic XML sitemaps that auto-update
- Log file analysis to understand actual crawl behavior

### WordPress specific
- Install Yoast/RankMath for technical SEO basics
- Check theme isn't injecting bad schema
- Minimize plugins (each adds JS/CSS weight)
- Use object caching (Redis) + page caching (WP Super Cache/W3 Total Cache)

### After a Google algorithm update
- Don't panic — wait 2 weeks for volatility to settle
- Compare affected pages vs unaffected — find the pattern
- Check Search Console for manual actions
- Focus on content quality and E-E-A-T, not just technical fixes

---

## Natural Language Commands

```
"Run a technical SEO audit for [URL]"
"Check Core Web Vitals for [URL]"
"Audit my robots.txt and sitemap"
"Find indexing issues on my site"
"Check structured data / schema markup"
"Generate schema markup for [page type]"
"Pre-migration SEO checklist for [old] → [new]"
"Check security headers for [URL]"
"Find broken links and redirect chains"
"International SEO audit for [URL]"
"Score my site's technical SEO health"
"What's causing my slow page speed?"
```
