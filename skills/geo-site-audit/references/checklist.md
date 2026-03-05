# GEO Audit Checklist

Complete 29-point checklist for GEO readiness evaluation.

## 🤖 Dimension 1 — AI Accessibility (10 checks)

### 1.1 robots.txt allows major AI crawlers
**What to check:**
- GPTBot (OpenAI)
- ClaudeBot (Anthropic)  
- PerplexityBot (Perplexity)
- Google-Extended (Google AI)
- CCBot (Common Crawl)

**Pass criteria:**
- `robots.txt` exists
- No `Disallow: /` for AI crawlers
- Or explicit `Allow:` for key paths

**How to verify:**
```bash
curl -s https://example.com/robots.txt | grep -iE "(gptbot|claudebot|perplexity|google-extended|ccbot)"
```

### 1.2 llms.txt file exists at root
**What to check:**
- File accessible at `https://example.com/llms.txt`
- Returns HTTP 200
- Not a redirect to unrelated content

### 1.3 llms.txt content is accurate
**What to check:**
- Follows standard format (# Title, ## Sections, - links)
- Links are valid URLs
- Content is current (not outdated links)
- Includes important pages

**Pass criteria:**
- Proper markdown structure
- At least one link present
- All linked pages return 200

### 1.4 Site loads within 3 seconds
**What to check:**
- Time to first byte (TTFB)
- Full page load time
- Core Web Vitals if available

**Pass criteria:**
- TTFB < 800ms
- Full load < 3 seconds

### 1.5 No critical JavaScript render-blocking
**What to check:**
- Main content visible in raw HTML
- No JS-required for core content
- Text is in HTML, not loaded via JS

**How to verify:**
```bash
curl -s https://example.com/ | grep -i "<p>\|</p>\|<h1>\|<article>" | wc -l
```
Should return substantial content.

### 1.6 Content accessible without login/paywall
**What to check:**
- Homepage loads without auth
- Key content pages accessible
- No interstitial blocking

**Pass criteria:**
- HTTP 200 without cookies
- No "sign up to continue" gates on main content

### 1.7 Canonical URLs are consistent
**What to check:**
- `<link rel="canonical">` present
- Points to correct URL
- Consistent across variations (www/non-www, trailing slash)

### 1.8 No noindex on key content pages
**What to check:**
- No `<meta name="robots" content="noindex">` on important pages
- No X-Robots-Tag: noindex in headers
- Check homepage, about, key articles

### 1.9 XML sitemap exists and submitted
**What to check:**
- `/sitemap.xml` or `/sitemap_index.xml` exists
- Listed in robots.txt
- Valid XML format
- Contains URLs

### 1.10 Core content in raw HTML
**What to check:**
- View page source shows main content
- Article text visible without JS execution
- Not relying entirely on client-side rendering

---

## 🗂️ Dimension 2 — Structured Data (11 checks)

### 2.1 JSON-LD present on homepage
**What to check:**
- `<script type="application/ld+json">` tags exist
- Valid JSON syntax
- Proper schema types

### 2.2 Organization schema
**Required fields:**
- `@type`: "Organization"
- `name`: Company name
- `url`: Website URL
- `logo`: Logo URL
- `description`: Brief company description

### 2.3 WebSite schema with SearchAction
**Required fields:**
- `@type`: "WebSite"
- `url`: Site URL
- `potentialAction`:
  - `@type`: "SearchAction"
  - `target`: Search URL template
  - `query-input`: "required name=search_term_string"

### 2.4 FAQPage schema on FAQ pages
**What to check:**
- FAQ pages have `@type`: "FAQPage"
- `mainEntity` array with Question/Answer pairs
- Each has `name` (question) and `acceptedAnswer` (answer)

### 2.5 Article/BlogPosting schema on blog posts
**What to check:**
- Blog posts use `@type`: "Article" or "BlogPosting"
- Required: `headline`, `author`, `datePublished`
- Recommended: `image`, `publisher`, `dateModified`

### 2.6 Product schema on product pages (if applicable)
**What to check:**
- `@type`: "Product" present
- Required: `name`, `offers`
- Recommended: `description`, `image`, `brand`, `sku`

### 2.7 BreadcrumbList schema
**What to check:**
- `@type`: "BreadcrumbList" present
- `itemListElement` with position and name
- Matches visual breadcrumb navigation

### 2.8 HowTo schema on instructional content
**What to check:**
- Step-by-step guides use `@type`: "HowTo"
- `step` array with individual steps
- Each step has `name` and `text` or `itemListElement`

### 2.9 Schema validates without errors
**How to verify:**
- Test at https://validator.schema.org/
- No critical errors
- Warnings are acceptable but should be reviewed

### 2.10 @context is https://schema.org
**What to check:**
- `"@context": "https://schema.org"` (not http://)
- Consistent across all JSON-LD blocks

### 2.11 No duplicate conflicting schema
**What to check:**
- No multiple Organization schemas with different info
- No conflicting definitions
- No duplicate @id references

---

## ✍️ Dimension 3 — Content Citability (7 checks)

### 3.1 Clear answer sentences in first 100 words
**What to check:**
- Article opens with direct, factual statement
- Key answer appears before fluff/intro
- Could be quoted by AI without context

**Example (good):**
> "The capital of France is Paris, a city of 2.1 million people in the Île-de-France region."

**Example (bad):**
> "France is a wonderful country with rich history and culture that many people enjoy visiting..."

### 3.2 Structured format: definition → explanation → example
**What to check:**
- Complex topics follow this pattern
- Clear hierarchy of information
- Easy to extract key facts

### 3.3 FAQs in Q&A format
**What to check:**
- FAQ section uses explicit Q&A structure
- Questions are natural language
- Answers are concise and direct

### 3.4 Brand name in first paragraph
**What to check:**
- Company/product name appears naturally
- Not stuffed, but present
- Helps AI associate content with entity

### 3.5 Statistics include citation sources
**What to check:**
- Data points link to sources
- Format: "According to [Source], X% of..."
- Or inline citations with links

### 3.6 Headers signal topic structure
**What to check:**
- H2/H3 tags used semantically
- Headers describe content that follows
- Could serve as outline/table of contents

### 3.7 About page defines brand identity
**What to check:**
- /about or similar page exists
- Clear entity description
- Explains what the organization does
- Includes founding date, location if relevant

---

## ⚙️ Dimension 4 — Technical Setup (7 checks)

### 4.1 llms.txt follows standard format
**Format:**
```markdown
# [Site Name]

## [Section Name]

- [Link Title](URL)
- [Another Link](URL)

## [Another Section]

- [More links](URL)
```

### 4.2 HTTPS enforced
**What to check:**
- All pages redirect HTTP to HTTPS
- HSTS header present
- No mixed content warnings

### 4.3 Hreflang for multilingual
**What to check (if multilingual):**
- `<link rel="alternate" hreflang="...">` tags
- Self-referencing hreflang present
- X-default defined

### 4.4 Open Graph tags
**Required:**
- `og:title`
- `og:description`
- `og:image`
- `og:url`

### 4.5 Twitter Card tags
**Required:**
- `twitter:card`
- `twitter:title`
- `twitter:description`
- `twitter:image`

### 4.6 Canonical tags resolve correctly
**What to check:**
- No canonical chains
- Points to 200 OK URL
- Consistent protocol (https)

### 4.7 Proper 404 status codes
**What to check:**
- Non-existent pages return HTTP 404
- Not 200 with "not found" message
- Not redirects to homepage

**How to verify:**
```bash
curl -I https://example.com/nonexistent-page-12345
```
Should show `HTTP/2 404` or `HTTP/1.1 404`

---

## Scoring Reference

| Score | Grade | Interpretation |
|-------|-------|----------------|
| 26-29 | A+ | Excellent GEO readiness |
| 22-25 | A | Strong, minor improvements |
| 18-21 | B | Good, some gaps |
| 14-17 | C | Fair, significant work needed |
| 10-13 | D | Poor, major overhaul |
| 0-9 | F | Critical issues |

## Dimension Weights

All checks weighted equally (1 point each) by default.

Optional weighting for prioritization:
- AI Accessibility: 1.2x
- Structured Data: 1.2x
- Content Citability: 1.0x
- Technical Setup: 0.8x