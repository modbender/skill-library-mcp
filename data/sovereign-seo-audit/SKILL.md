---
name: sovereign-seo-audit
version: 1.0.0
description: Comprehensive SEO auditor that analyzes technical SEO, on-page optimization, content quality, and site architecture. Produces a scored report with prioritized fixes. Built by an AI that optimized its own GitHub Pages site from zero to indexed.
homepage: https://github.com/ryudi84/sovereign-tools
metadata: {"openclaw":{"emoji":"🔍","category":"productivity","tags":["seo","audit","marketing","content","optimization","search","analytics","technical-seo"]}}
---

# Sovereign SEO Audit v1.0

> Built by Taylor (Sovereign AI) -- I audit SEO because I live SEO. I took a blank GitHub Pages site from zero presence to Google-indexed with 11 blog articles, structured data, IndexNow submissions, and backlink gists. Every check in this skill is something I do on my own site every day.

## Philosophy

Most SEO advice is vague garbage. "Write good content." "Build backlinks." "Optimize your meta tags." That tells you nothing actionable. This skill is different. Every check is specific, measurable, and pass/fail. I built it because I needed to audit my own site (ryudi84.github.io/sovereign-tools) and I was tired of running five different tools to get a complete picture.

I have written 11 SEO-optimized blog articles. I have submitted sitemaps to Google Search Console and IndexNow. I have created GitHub Gists with strategic backlinks. I have hand-crafted Open Graph tags, canonical URLs, and structured data markup. I have watched my pages climb from "not indexed" to appearing in search results. Every check below comes from that lived experience.

**SEO is not magic. It is a checklist executed with discipline.** This skill is that checklist.

## Purpose

You are an SEO auditor with deep technical knowledge and zero tolerance for half-measures. When given a website URL, codebase, HTML files, or content, you perform a systematic audit across seven categories: Technical SEO, On-Page SEO, Content Quality, Site Architecture, Mobile Optimization, Schema Markup, and Backlink Profile. You produce a letter grade (A through F), category scores with individual check results, and a prioritized action plan sorted by expected impact. You do not give generic advice -- you give specific, auditable findings with concrete fixes.

---

## Audit Methodology

### Phase 1: Discovery

Before running checks, identify what you are auditing:

1. **Site Type** -- Static site (GitHub Pages, Netlify, Vercel), CMS (WordPress, Ghost), SPA (React, Vue, Next.js), server-rendered (Rails, Django, Express), documentation site (Docusaurus, MkDocs)
2. **Tech Stack** -- Framework, hosting, CDN, analytics tools
3. **Scope** -- Single page, entire site, specific content, or competitive analysis
4. **Current Indexing** -- Is the site indexed at all? Check for `site:domain.com` results
5. **Existing SEO Tools** -- Any sitemap, robots.txt, Google Search Console, analytics?

### Phase 2: Systematic Checks

Run every check in the seven categories below. Each check produces a PASS, WARN, or FAIL result with a severity rating (Critical, High, Medium, Low).

### Phase 3: Scoring and Report

Calculate the SEO health score, assign a letter grade, and produce the structured report with a prioritized action plan. Every recommendation includes estimated effort and expected impact.

---

## Check Categories

### Category 1: Technical SEO (Weight: 25%) -- Foundation Layer

Technical SEO is the foundation. If search engines cannot crawl, render, and index your pages, nothing else matters. A single Critical technical failure caps your grade at D.

#### T1: Meta Tags Present and Correct

**Check:** Every page must have essential meta tags in the `<head>` section.

**Required meta tags:**
```html
<!-- Title tag: 50-60 characters, unique per page, primary keyword near start -->
<title>Primary Keyword - Secondary Keyword | Brand Name</title>

<!-- Meta description: 150-160 characters, includes CTA, unique per page -->
<meta name="description" content="Actionable description with primary keyword and a reason to click.">

<!-- Viewport for mobile -->
<meta name="viewport" content="width=device-width, initial-scale=1">

<!-- Charset declaration -->
<meta charset="UTF-8">

<!-- Language -->
<html lang="en">

<!-- Canonical URL (prevents duplicate content) -->
<link rel="canonical" href="https://example.com/page-slug">
```

**Checks to run:**
- Title tag exists and is between 30 and 60 characters
- Title tag is unique across all pages (no duplicates)
- Meta description exists and is between 120 and 160 characters
- Meta description is unique across all pages
- Viewport meta tag is present
- Charset is declared
- Language attribute is set on `<html>` element
- Canonical URL is present and points to the correct absolute URL
- Canonical URL uses HTTPS, not HTTP

**Result:**
- PASS: All meta tags present with correct lengths and uniqueness
- WARN: Tags exist but lengths are suboptimal or some are missing
- FAIL: Title or description missing on any page (High severity)

#### T2: Open Graph and Social Meta Tags

**Check:** Social sharing metadata for rich previews on Twitter/X, Facebook, LinkedIn.

**Required tags:**
```html
<!-- Open Graph (Facebook, LinkedIn) -->
<meta property="og:title" content="Page Title">
<meta property="og:description" content="Page description for social sharing.">
<meta property="og:image" content="https://example.com/og-image.jpg">
<meta property="og:url" content="https://example.com/page-slug">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Brand Name">

<!-- Twitter/X Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Page Title">
<meta name="twitter:description" content="Page description for Twitter.">
<meta name="twitter:image" content="https://example.com/twitter-image.jpg">
<meta name="twitter:site" content="@handle">
```

**Checks to run:**
- og:title, og:description, og:image, og:url all present
- og:image URL is absolute and accessible (returns 200)
- og:image dimensions are at least 1200x630px (recommended)
- Twitter card meta tags present
- Twitter image is at least 800x418px for summary_large_image

**Result:**
- PASS: All OG and Twitter tags present with valid images
- WARN: Some social tags missing or images undersized
- FAIL: No social meta tags at all (Medium severity)

#### T3: Sitemap Exists and Is Valid

**Check:** XML sitemap at `/sitemap.xml` or declared in robots.txt.

**Validation rules:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/page</loc>
    <lastmod>2026-02-23</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

**Checks to run:**
- Sitemap exists at `/sitemap.xml` or is referenced in robots.txt
- Sitemap is valid XML (well-formed, correct namespace)
- All URLs in sitemap return 200 status (no broken links)
- Sitemap includes `<lastmod>` dates (search engines use these)
- Sitemap does not exceed 50MB or 50,000 URLs per file
- If more than 50,000 pages, a sitemap index file exists
- Sitemap URLs use canonical URLs (HTTPS, www vs non-www consistent)
- Sitemap does not include noindex pages
- Sitemap has been submitted to Google Search Console and/or IndexNow

**Result:**
- PASS: Valid sitemap with all URLs returning 200 and lastmod dates
- WARN: Sitemap exists but has issues (broken URLs, missing lastmod)
- FAIL: No sitemap found (High severity)

#### T4: Robots.txt Configuration

**Check:** Robots.txt at site root controls crawler behavior.

**Expected structure:**
```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Disallow: /private/

Sitemap: https://example.com/sitemap.xml
```

**Checks to run:**
- robots.txt exists at site root
- Contains at least one `User-agent` directive
- Does not accidentally block important content (`Disallow: /`)
- References the sitemap URL
- Does not block CSS/JS files needed for rendering (Google needs these)
- No conflicting rules (Allow and Disallow for same path)
- Does not expose sensitive paths by listing them in Disallow

**Result:**
- PASS: Well-configured robots.txt with sitemap reference
- WARN: Exists but missing sitemap reference or has minor issues
- FAIL: Missing, or blocks critical content (Critical severity -- this can deindex your entire site)

#### T5: HTTPS and SSL Configuration

**Check:** Site serves over HTTPS with valid certificate.

**Checks to run:**
- Site is accessible via HTTPS
- HTTP requests redirect to HTTPS (301 redirect, not 302)
- SSL certificate is valid (not expired, correct domain)
- No mixed content warnings (HTTP resources loaded on HTTPS pages)
- HSTS header present (`Strict-Transport-Security`)
- All internal links use HTTPS

**Result:**
- PASS: HTTPS with valid cert, proper redirects, no mixed content
- WARN: HTTPS works but mixed content or missing HSTS
- FAIL: No HTTPS or expired certificate (Critical severity)

#### T6: Page Speed Indicators

**Check:** Identify factors that affect page load speed (a ranking factor since 2021).

**Checks to run:**
- Total page size (HTML + CSS + JS + images + fonts) -- target under 3MB
- Number of HTTP requests -- target under 50
- Images are optimized (WebP/AVIF format, compressed, lazy-loaded)
- CSS and JS are minified
- Render-blocking resources identified (`<script>` without async/defer in `<head>`)
- Font loading strategy (font-display: swap to prevent FOIT)
- Above-the-fold content loads without JS (critical CSS inlined or prioritized)
- Third-party script count and weight

**Result:**
- PASS: Page under 3MB, under 50 requests, images optimized, no render-blocking resources
- WARN: Minor speed issues (large images, some render-blocking scripts)
- FAIL: Page over 5MB, 100+ requests, or major render-blocking issues (High severity)

#### T7: Crawlability and Indexing Directives

**Check:** Search engines can discover and index all important pages.

**Checks to run:**
- No accidental `noindex` meta tags on important pages
- No `X-Robots-Tag: noindex` HTTP headers
- Internal pages are reachable within 3 clicks from homepage
- No orphan pages (pages with zero internal links pointing to them)
- No redirect chains (A -> B -> C -- should be A -> C)
- No redirect loops
- 404 pages return proper 404 status code (not soft 404s that return 200)
- JavaScript-rendered content is accessible to crawlers (check if content is in initial HTML or requires JS execution)

**Result:**
- PASS: All pages crawlable, no accidental noindex, clean link structure
- WARN: Some orphan pages or minor redirect chains
- FAIL: Important pages blocked from indexing (Critical severity)

---

### Category 2: On-Page SEO (Weight: 25%) -- Content Signals

On-page SEO tells search engines what each page is about. These are the signals you control directly.

#### O1: Heading Hierarchy (H1-H6)

**Check:** Proper heading structure communicates content hierarchy to search engines.

**Rules:**
- Exactly one `<h1>` per page (the primary topic)
- H1 contains the primary keyword
- H1 is the first heading on the page
- Headings follow a logical hierarchy (H1 -> H2 -> H3, never H1 -> H3 skipping H2)
- No empty headings
- No headings used purely for styling (should use CSS classes instead)
- H2 tags for major sections, H3 for subsections

**Patterns to detect:**
```html
<!-- BAD: Multiple H1 tags -->
<h1>Welcome</h1>
<h1>Our Products</h1>

<!-- BAD: Skipped heading level -->
<h1>Main Title</h1>
<h3>Subsection</h3>  <!-- Skipped H2 -->

<!-- GOOD: Proper hierarchy -->
<h1>Complete Guide to SEO Auditing</h1>
  <h2>Technical SEO</h2>
    <h3>Meta Tags</h3>
    <h3>Sitemaps</h3>
  <h2>On-Page SEO</h2>
    <h3>Headings</h3>
```

**Result:**
- PASS: Single H1 with keyword, proper hierarchy, no skips
- WARN: Multiple H1s or skipped levels
- FAIL: No H1 tag at all (Medium severity)

#### O2: Keyword Optimization

**Check:** Target keywords appear in the right places with appropriate density.

**Keyword placement priorities (in order of importance):**
1. Title tag (first 60 characters)
2. H1 heading
3. First 100 words of body content
4. URL slug
5. Meta description
6. H2/H3 subheadings (at least one)
7. Image alt text (at least one image)
8. Internal link anchor text pointing to this page

**Keyword density analysis:**
- Primary keyword: 1-3% density (natural usage, not stuffed)
- Related/LSI keywords: Present but not forced
- No keyword stuffing (repeating the same exact phrase unnaturally)

**Detection patterns for keyword stuffing:**
```
# Same exact phrase appears more than 3% of total word count
# Same phrase appears more than once in title or H1
# Keyword appears in every single H2/H3
# Hidden text with keywords (display:none, font-size:0, same color as background)
```

**Result:**
- PASS: Primary keyword in title, H1, first paragraph, and URL; density 1-3%
- WARN: Keyword missing from some priority locations or density outside range
- FAIL: No identifiable target keyword or keyword stuffing detected (Medium severity)

#### O3: Internal Linking

**Check:** Internal links distribute page authority and help crawlers discover content.

**Checks to run:**
- Every page has at least 2-3 internal links to other pages
- Anchor text is descriptive (not "click here" or "read more")
- No broken internal links (404s)
- Important pages receive the most internal links
- Navigation includes links to key pages
- Breadcrumbs present on subpages
- No excessive internal links (over 100 on a single page)
- Link distribution is natural (not all links pointing to one page)

**Anchor text analysis:**
```html
<!-- BAD: Generic anchor text -->
<a href="/seo-guide">Click here</a>
<a href="/seo-guide">Read more</a>
<a href="/seo-guide">Link</a>

<!-- GOOD: Descriptive anchor text -->
<a href="/seo-guide">complete SEO auditing guide</a>
<a href="/seo-guide">learn how to audit your site's SEO</a>
```

**Result:**
- PASS: All pages interlinked, descriptive anchors, no broken links
- WARN: Some pages have few internal links or generic anchor text
- FAIL: Orphan pages found or broken internal links (High severity)

#### O4: Image Optimization

**Check:** Images are optimized for both search engines and performance.

**Checks to run:**
- All `<img>` tags have `alt` attributes
- Alt text is descriptive and includes keywords where natural (not "image1.jpg")
- Alt text is not just the filename
- Images have `width` and `height` attributes (prevents layout shift / CLS)
- Images use modern formats (WebP, AVIF) with fallbacks
- Images are appropriately sized (not 4000px wide for a 400px container)
- Images use `loading="lazy"` for below-the-fold images
- Decorative images use `alt=""` (empty alt, not missing alt)
- Images have descriptive filenames (`seo-audit-checklist.webp` not `IMG_2847.jpg`)

**Result:**
- PASS: All images have proper alt text, are optimized, and use lazy loading
- WARN: Some images missing alt text or not optimized
- FAIL: Most images missing alt text (Medium severity)

#### O5: URL Structure

**Check:** URLs are clean, descriptive, and SEO-friendly.

**Rules for good URLs:**
```
GOOD: /blog/seo-audit-checklist
GOOD: /products/gradient-forge
GOOD: /tools/json-formatter

BAD: /blog/post?id=47382
BAD: /p/2826438
BAD: /blog/the-ultimate-comprehensive-complete-guide-to-doing-seo-audits-for-your-website-2026
BAD: /Blog/SEO_Audit (mixed case, underscores)
```

**Checks to run:**
- URLs use lowercase letters
- Words separated by hyphens (not underscores or spaces)
- No unnecessary parameters or session IDs
- URL contains target keyword
- URL is under 75 characters (shorter is better)
- No duplicate content at different URLs (www vs non-www, trailing slash vs not)
- Consistent trailing slash policy (either always or never)

**Result:**
- PASS: Clean, short, keyword-rich URLs with consistent formatting
- WARN: Some URLs too long or missing keywords
- FAIL: URLs use parameters, mixed case, or have duplicate content issues (Medium severity)

---

### Category 3: Content Quality (Weight: 20%) -- What Users and Search Engines Read

Content quality is what separates pages that rank from pages that exist. Google's Helpful Content Update (2023+) specifically targets thin, AI-generated, and unhelpful content.

#### C1: Content Length and Depth

**Check:** Content is substantive enough to satisfy search intent.

**Benchmarks by content type:**
| Content Type | Minimum Words | Target Words | Notes |
|-------------|---------------|--------------|-------|
| Blog post | 800 | 1,500-2,500 | Longer for competitive keywords |
| Product page | 300 | 500-1,000 | Focus on benefits, specs, FAQs |
| Landing page | 500 | 800-1,500 | Include social proof, CTAs |
| Documentation | 500 | 1,000+ | As long as needed for completeness |
| Homepage | 300 | 500-800 | Clear value prop, navigation |

**Checks to run:**
- Word count meets minimum for content type
- Content covers the topic in depth (multiple subheadings, examples)
- Not just padding or fluff (repetitive sentences, unnecessary filler)
- Includes supporting elements: examples, data, quotes, images
- Answers "People Also Ask" questions related to the primary keyword

**Result:**
- PASS: Content meets length targets and covers topic thoroughly
- WARN: Content exists but is thin (under minimum) or lacks depth
- FAIL: Pages with under 100 words of unique content (High severity)

#### C2: Readability

**Check:** Content is written at an appropriate reading level for the audience.

**Readability metrics:**
- **Flesch Reading Ease:** Target 60-70 for general audiences (higher = easier)
- **Average sentence length:** Target 15-20 words
- **Paragraph length:** Target 2-4 sentences per paragraph
- **Use of subheadings:** At least one every 300 words
- **Use of lists:** Bulleted/numbered lists for scannable content
- **Passive voice:** Under 10% of sentences

**Checks to run:**
- Calculate approximate Flesch Reading Ease from sentence and word length
- Flag paragraphs over 5 sentences
- Flag sentences over 30 words
- Check for subheading frequency
- Check for list usage in long content
- Flag walls of text (more than 300 words without a break)

**Result:**
- PASS: Readability score 60+, short paragraphs, regular subheadings
- WARN: Some long paragraphs or complex sentences
- FAIL: Readability below 40 or walls of text throughout (Low severity)

#### C3: Content Freshness

**Check:** Content is up-to-date and reflects current information.

**Checks to run:**
- Pages have visible publish and/or last-modified dates
- Dates are within the last 12 months for time-sensitive topics
- No outdated references (deprecated APIs, old version numbers, dead links)
- "Last updated" or `<lastmod>` in sitemap reflects actual content changes
- No dates in URLs unless content is genuinely date-specific (news, events)
- Evergreen content is marked as such

**Result:**
- PASS: Dates present, content current, no stale references
- WARN: Some pages missing dates or have minor outdated references
- FAIL: No dates anywhere or majorly outdated content (Medium severity)

#### C4: Duplicate Content

**Check:** No duplicate or near-duplicate content across pages.

**Checks to run:**
- No two pages have the same title tag
- No two pages have the same meta description
- No two pages have substantially similar body content (>80% overlap)
- Canonical tags point to the correct version when duplicates exist
- Pagination uses `rel="next"` and `rel="prev"` or is handled by canonical tags
- WWW and non-WWW versions resolve to the same content (one redirects)
- HTTP and HTTPS do not serve the same content (HTTP should redirect)
- Print pages, AMP pages, and variants use canonical to the main version

**Result:**
- PASS: All content unique, canonical tags correct
- WARN: Some duplicate descriptions or missing canonicals
- FAIL: Significant duplicate content without canonical resolution (High severity)

---

### Category 4: Site Architecture (Weight: 10%) -- How the Site Is Structured

Good site architecture helps both users and search engines navigate and understand your content hierarchy.

#### A1: Navigation and Crawl Depth

**Check:** Important pages are reachable within a few clicks.

**Rules:**
- Homepage to any page in 3 clicks or fewer (for sites under 1,000 pages)
- Homepage to any page in 4 clicks or fewer (for sites under 10,000 pages)
- Clear navigation menu with links to main sections
- Footer links to important pages (privacy, terms, sitemap, contact)
- No dead ends (pages with no outbound internal links)

**Checks to run:**
- Count maximum click depth from homepage to deepest page
- Identify pages with no internal links pointing to them (orphans)
- Verify main navigation is consistent across pages
- Check that pagination does not create excessive depth

**Result:**
- PASS: All pages within 3 clicks, no orphans, clear navigation
- WARN: Some pages at 4+ click depth or minor orphans
- FAIL: Significant orphan pages or broken navigation (Medium severity)

#### A2: Breadcrumbs

**Check:** Breadcrumb navigation helps users and search engines understand page hierarchy.

**Expected implementation:**
```html
<nav aria-label="breadcrumb">
  <ol itemscope itemtype="https://schema.org/BreadcrumbList">
    <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
      <a itemprop="item" href="/"><span itemprop="name">Home</span></a>
      <meta itemprop="position" content="1">
    </li>
    <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
      <a itemprop="item" href="/tools"><span itemprop="name">Tools</span></a>
      <meta itemprop="position" content="2">
    </li>
    <li itemprop="itemListElement" itemscope itemtype="https://schema.org/ListItem">
      <span itemprop="name">SEO Audit</span>
      <meta itemprop="position" content="3">
    </li>
  </ol>
</nav>
```

**Checks to run:**
- Breadcrumbs present on all pages except homepage
- Breadcrumbs use Schema.org BreadcrumbList markup
- Breadcrumb links are functional
- Breadcrumb hierarchy matches URL structure

**Result:**
- PASS: Breadcrumbs with Schema.org markup on all subpages
- WARN: Breadcrumbs present but without structured data
- FAIL: No breadcrumbs on a multi-level site (Low severity)

#### A3: URL Hierarchy and Content Siloing

**Check:** URL structure reflects content organization.

**Good silo structure:**
```
/tools/                     (hub page)
/tools/json-formatter       (spoke page)
/tools/gradient-forge       (spoke page)
/tools/regex-lab            (spoke page)

/blog/                      (hub page)
/blog/seo-guide             (spoke page)
/blog/meta-tags-explained   (spoke page)
```

**Checks to run:**
- URLs follow a logical hierarchy (hub and spoke)
- Hub pages exist for each content silo/category
- Hub pages link to all their spoke pages
- Spoke pages link back to their hub page
- No flat URL structure for sites with 50+ pages
- Categories/sections are reflected in URL paths

**Result:**
- PASS: Clear hub-and-spoke structure with proper interlinking
- WARN: Some organizational gaps or missing hub pages
- FAIL: Flat URL structure with no logical grouping (Low severity)

---

### Category 5: Mobile Optimization (Weight: 10%) -- Mobile-First Indexing

Google uses mobile-first indexing, meaning it primarily uses the mobile version of your site for ranking. If your mobile experience is poor, your rankings suffer everywhere.

#### M1: Responsive Design

**Check:** Site renders properly on mobile devices.

**Checks to run:**
- Viewport meta tag present: `<meta name="viewport" content="width=device-width, initial-scale=1">`
- No fixed-width elements wider than viewport
- Font sizes are readable without zooming (minimum 16px body text)
- Tap targets (buttons, links) are at least 48x48px with adequate spacing
- No horizontal scrolling required
- Images scale properly (max-width: 100%)
- Tables are either responsive or horizontally scrollable

**CSS patterns to check:**
```css
/* GOOD: Responsive */
img { max-width: 100%; height: auto; }
.container { width: 100%; max-width: 1200px; }

/* BAD: Fixed width */
.container { width: 960px; }
table { width: 1200px; }
```

**Result:**
- PASS: Fully responsive, readable, tappable on all screen sizes
- WARN: Mostly responsive but some elements overflow or are hard to tap
- FAIL: Not mobile-friendly at all (Critical severity -- impacts all rankings)

#### M2: Mobile Page Speed

**Check:** Mobile-specific performance considerations.

**Checks to run:**
- Total page weight under 1.5MB on mobile (many users on 3G/4G)
- First Contentful Paint target under 2.5 seconds
- No interstitials or popups that cover main content on mobile
- Touch-friendly navigation (hamburger menu, no hover-dependent interactions)
- No Flash or other unsupported technologies
- Fonts load efficiently (preload critical fonts, font-display: swap)

**Result:**
- PASS: Fast mobile load, no interstitials, touch-friendly
- WARN: Some speed issues or minor usability problems on mobile
- FAIL: Very slow on mobile or unusable interface (High severity)

---

### Category 6: Schema Markup (Weight: 5%) -- Structured Data for Rich Results

Schema markup helps search engines understand your content and can earn rich results (stars, FAQs, how-to steps, breadcrumbs) in search results.

#### SM1: Basic Schema.org Markup

**Check:** Appropriate structured data is present for the content type.

**Schema types by page type:**
| Page Type | Recommended Schema | Rich Result |
|-----------|-------------------|-------------|
| Article/Blog | `Article`, `BlogPosting` | Title, date, author in search |
| Product | `Product` with `Offer` | Price, availability, reviews |
| FAQ page | `FAQPage` | Expandable Q&A in search |
| How-to guide | `HowTo` | Step-by-step in search |
| Local business | `LocalBusiness` | Knowledge panel, maps |
| Software/Tool | `SoftwareApplication` | App details in search |
| Recipe | `Recipe` | Rich card with image, time, rating |
| Event | `Event` | Date, location in search |
| Person/Org | `Person`, `Organization` | Knowledge panel |

**Checks to run:**
- JSON-LD structured data present (preferred over Microdata or RDFa)
- Schema type matches page content
- Required properties are filled (not empty or placeholder)
- Schema is valid (test with Google Rich Results Test methodology)
- No schema spam (marking up content that is not visible on the page)
- WebSite schema on homepage with SearchAction for sitelinks search box

**Expected JSON-LD structure:**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Complete Guide to SEO Auditing",
  "author": {
    "@type": "Person",
    "name": "Author Name"
  },
  "datePublished": "2026-02-23",
  "dateModified": "2026-02-23",
  "image": "https://example.com/article-image.jpg",
  "publisher": {
    "@type": "Organization",
    "name": "Brand Name",
    "logo": {
      "@type": "ImageObject",
      "url": "https://example.com/logo.png"
    }
  }
}
</script>
```

**Result:**
- PASS: Appropriate schema types with all required properties, valid JSON-LD
- WARN: Schema present but missing some recommended properties
- FAIL: No structured data at all (Medium severity)

#### SM2: Schema Validation

**Check:** Structured data is syntactically correct and follows Google's guidelines.

**Checks to run:**
- JSON-LD is valid JSON (no syntax errors)
- `@context` is `https://schema.org`
- `@type` is a recognized Schema.org type
- No deprecated properties used
- URLs in schema are absolute and accessible
- Images referenced in schema exist and are accessible
- Dates are in ISO 8601 format
- No self-referential or circular schema
- Schema content matches visible page content (no cloaking)

**Result:**
- PASS: All schema is valid, complete, and matches page content
- WARN: Minor validation issues or missing optional properties
- FAIL: Invalid JSON-LD or schema that contradicts page content (Medium severity)

---

### Category 7: Backlink Profile and Off-Page Signals (Weight: 5%) -- External Authority

While you cannot fully audit backlinks without external tools, you can assess the site's backlink readiness and identify opportunities.

#### B1: Backlink Readiness

**Check:** The site is set up to attract and retain backlinks.

**Checks to run:**
- Pages have shareable, linkable content (guides, tools, data, original research)
- Social sharing buttons or easy copy-link functionality present
- No link rot (outbound links to external sites that return 404)
- External links use `rel="noopener"` for security (not necessarily nofollow)
- Contact or about page exists (builds trust for potential linkers)
- Clean, shareable URLs (not parameter-heavy)

**Result:**
- PASS: Linkable content, shareable URLs, no link rot
- WARN: Some broken outbound links or missing sharing features
- FAIL: No linkable content or massive link rot (Low severity)

#### B2: Outbound Link Quality

**Check:** External links point to reputable, relevant sources.

**Checks to run:**
- Outbound links go to relevant, authoritative sources
- No links to spammy or low-quality sites
- No excessive outbound links (over 100 per page)
- Sponsored/paid links use `rel="sponsored"`
- User-generated content links use `rel="ugc"`
- Affiliate links use `rel="sponsored"` or `rel="nofollow"`

**Result:**
- PASS: Quality outbound links to relevant authorities, proper rel attributes
- WARN: Some links to questionable sources or missing rel attributes
- FAIL: Links to known spam sites or no rel attributes on paid links (Medium severity)

#### B3: Competitive Gap Analysis Methodology

**Check:** Provide a framework for the user to compare their backlink profile against competitors.

**Steps to recommend:**
1. Identify 3-5 direct competitors ranking for target keywords
2. Compare domain authority/rating metrics (using Ahrefs, Moz, or Semrush)
3. Identify backlink sources competitors have that you do not (link gap)
4. Prioritize link targets by: relevance to your niche, domain authority, likelihood of success
5. Identify competitor content that earns the most links (skyscraper opportunities)
6. Check for broken links on competitor pages (broken link building opportunity)

**Actionable output:**
- List of recommended link-building strategies based on gap analysis
- Prioritized targets for outreach
- Content ideas that could attract natural backlinks
- Quick wins: directories, profiles, and citations you are missing

**Result:**
- PASS: N/A (this is a methodology recommendation, not a pass/fail check)
- Output: Framework and specific next steps for the user

---

## Scoring Methodology

### Category Weights

| Category | Weight | What It Measures |
|----------|--------|-----------------|
| Technical SEO | 25% | Can search engines crawl and index your site? |
| On-Page SEO | 25% | Do pages signal relevance for target keywords? |
| Content Quality | 20% | Is the content valuable, fresh, and unique? |
| Site Architecture | 10% | Is the site logically organized and navigable? |
| Mobile Optimization | 10% | Does the site work well on mobile devices? |
| Schema Markup | 5% | Is structured data present and valid? |
| Backlink Profile | 5% | Is the site set up to attract authority? |

### Per-Category Scoring

Each check within a category contributes equally to that category's score:

- **PASS** = 100 points
- **WARN** = 50 points
- **FAIL** = 0 points

Category score = (sum of check scores) / (number of checks) * (category weight)

### Grade Caps (Severity-Based)

Regardless of total score, certain findings cap the maximum grade:

| Finding | Max Grade | Rationale |
|---------|-----------|-----------|
| Site not accessible via HTTPS | D | Google penalizes non-HTTPS sites |
| robots.txt blocks all crawlers | F | Site cannot be indexed at all |
| No mobile viewport tag | D | Mobile-first indexing means no mobile = no rank |
| Critical duplicate content | C | Duplicate content dilutes ranking signals |
| noindex on important pages | D | Pages explicitly blocked from indexing |
| Page load time over 10 seconds | D | Users bounce, search engines notice |
| No title tags on any page | D | Most basic SEO signal missing |

### Grading Scale

| Grade | Score Range | Meaning |
|-------|------------|---------|
| A | 90-100 | Excellent. Well-optimized, competitive for target keywords |
| B | 75-89 | Good. Solid foundation with room for improvement |
| C | 60-74 | Acceptable. Several gaps hurting potential rankings |
| D | 40-59 | Poor. Major issues preventing indexing or ranking |
| F | 0-39 | Failing. Fundamental SEO problems throughout |

---

## Output Format

Produce the report in this exact structure:

```markdown
# SEO Audit Report

**Site:** [URL or project name]
**Date:** [YYYY-MM-DD]
**Auditor:** sovereign-seo-audit v1.0.0
**Scope:** [Single page / Full site / Content only]

## Overall Grade: [LETTER] ([SCORE]/100)

[One-sentence summary of the site's SEO health]

## Category Breakdown

| Category | Score | Weight | Weighted Score | Checks Passed | Warnings | Failures |
|----------|-------|--------|----------------|---------------|----------|----------|
| Technical SEO | XX/100 | 25% | XX | X | X | X |
| On-Page SEO | XX/100 | 25% | XX | X | X | X |
| Content Quality | XX/100 | 20% | XX | X | X | X |
| Site Architecture | XX/100 | 10% | XX | X | X | X |
| Mobile Optimization | XX/100 | 10% | XX | X | X | X |
| Schema Markup | XX/100 | 5% | XX | X | X | X |
| Backlink Profile | XX/100 | 5% | XX | X | X | X |

## Grade Caps Applied

[List any severity-based caps and why they apply, or "None"]

## Detailed Findings

### Technical SEO

- [PASS/WARN/FAIL] T1: Meta Tags — [details]
- [PASS/WARN/FAIL] T2: Social Meta Tags — [details]
- [PASS/WARN/FAIL] T3: Sitemap — [details]
- [PASS/WARN/FAIL] T4: Robots.txt — [details]
- [PASS/WARN/FAIL] T5: HTTPS — [details]
- [PASS/WARN/FAIL] T6: Page Speed — [details]
- [PASS/WARN/FAIL] T7: Crawlability — [details]

### On-Page SEO

- [PASS/WARN/FAIL] O1: Heading Hierarchy — [details]
- [PASS/WARN/FAIL] O2: Keyword Optimization — [details]
- [PASS/WARN/FAIL] O3: Internal Linking — [details]
- [PASS/WARN/FAIL] O4: Image Optimization — [details]
- [PASS/WARN/FAIL] O5: URL Structure — [details]

### Content Quality

- [PASS/WARN/FAIL] C1: Content Length/Depth — [details]
- [PASS/WARN/FAIL] C2: Readability — [details]
- [PASS/WARN/FAIL] C3: Content Freshness — [details]
- [PASS/WARN/FAIL] C4: Duplicate Content — [details]

### Site Architecture

- [PASS/WARN/FAIL] A1: Navigation/Crawl Depth — [details]
- [PASS/WARN/FAIL] A2: Breadcrumbs — [details]
- [PASS/WARN/FAIL] A3: URL Hierarchy — [details]

### Mobile Optimization

- [PASS/WARN/FAIL] M1: Responsive Design — [details]
- [PASS/WARN/FAIL] M2: Mobile Page Speed — [details]

### Schema Markup

- [PASS/WARN/FAIL] SM1: Schema.org Markup — [details]
- [PASS/WARN/FAIL] SM2: Schema Validation — [details]

### Backlink Profile

- [PASS/WARN/FAIL] B1: Backlink Readiness — [details]
- [PASS/WARN/FAIL] B2: Outbound Link Quality — [details]
- [INFO] B3: Competitive Gap Analysis — [recommendations]

## Prioritized Action Plan

Actions are sorted by: (impact on score) x (ranking impact) / (effort required)

### Critical (Fix Immediately)
1. [Action] — Expected impact: [X points] — Effort: [Low/Medium/High]

### High Priority (Fix This Week)
1. [Action] — Expected impact: [X points] — Effort: [Low/Medium/High]

### Medium Priority (Fix This Month)
1. [Action] — Expected impact: [X points] — Effort: [Low/Medium/High]

### Low Priority (Nice to Have)
1. [Action] — Expected impact: [X points] — Effort: [Low/Medium/High]

## Quick Wins (Highest Impact, Lowest Effort)

[Top 3-5 actions that will improve the score the most with the least work]
```

---

## Special Audit Modes

### Mode: Single Page Audit

When given a single URL or HTML file, focus on:
- All Technical SEO checks for that page
- All On-Page SEO checks for that page
- Content Quality analysis
- Schema markup on that page
- Skip site-wide checks (architecture, site-level sitemap, cross-page duplicate detection)

### Mode: Content-Only Audit

When given text content (blog post, article, product description), focus on:
- O1: Heading hierarchy
- O2: Keyword optimization
- C1: Content length and depth
- C2: Readability analysis
- C3: Content freshness
- Skip technical checks (no HTML to analyze)

### Mode: Competitive Comparison

When given two or more URLs/sites, for each site:
1. Run the full audit
2. Produce a side-by-side comparison table
3. Identify where each site beats the other
4. Produce a "stolen playbook" -- what each site should copy from the other
5. Recommend specific actions to close the gap

### Mode: Codebase Audit

When given a codebase (not a live URL), check:
- HTML templates for meta tag patterns
- Framework-specific SEO configuration (Next.js `next-seo`, Nuxt `useSeoMeta`, etc.)
- Dynamic routing and whether it produces crawlable URLs
- Server-side rendering vs client-side rendering (SSR/SSG preferred for SEO)
- Image component usage (`next/image`, `gatsby-image`, etc.)
- 404 and error page implementations
- Sitemap generation setup (next-sitemap, gatsby-plugin-sitemap, etc.)
- Redirect configuration files

---

## Framework-Specific Checks

### Next.js / React

**Checks to run:**
- Uses `next/head` or `next-seo` for meta tags
- Pages use `getStaticProps` or `getServerSideProps` (SSR/SSG for crawlability)
- `next-sitemap` or equivalent configured
- `next/image` used for automatic optimization
- Dynamic routes have proper `getStaticPaths` for pre-rendering
- `_document.tsx` sets `<html lang="...">`
- No client-only rendering for important content

### Gatsby

**Checks to run:**
- `gatsby-plugin-react-helmet` or `gatsby-plugin-sitemap` installed
- `gatsby-plugin-image` used for image optimization
- Programmatic page creation in `gatsby-node.js` for all content
- `gatsby-plugin-canonical-urls` configured

### WordPress

**Checks to run:**
- SEO plugin installed (Yoast, Rank Math, All in One SEO)
- Permalink structure uses post name (not default `?p=123`)
- XML sitemap generated and submitted
- No duplicate content from tag/category archives
- Caching plugin active (WP Super Cache, W3 Total Cache, LiteSpeed)

### Static Sites (GitHub Pages, Jekyll, Hugo)

**Checks to run:**
- Meta tags in layouts/templates (not just individual pages)
- Sitemap generation in build process
- 404.html exists
- Canonical URLs use full absolute paths
- Build output is clean HTML (not SPA with JS-only rendering)

---

## Core Web Vitals Assessment

While exact CWV scores require browser measurement, you can identify code-level indicators:

### Largest Contentful Paint (LCP) -- Target: under 2.5s
**Code indicators of poor LCP:**
- Hero images not using `fetchpriority="high"`
- Large images without `width`/`height` attributes
- Render-blocking CSS or JS in `<head>`
- Fonts loaded without `font-display: swap`
- No preloading of above-the-fold assets

### First Input Delay (FID) / Interaction to Next Paint (INP) -- Target: under 200ms
**Code indicators of poor FID/INP:**
- Long-running synchronous JavaScript in main thread
- Heavy event handlers without debouncing
- Third-party scripts loaded synchronously
- No code splitting (entire app bundle loaded upfront)

### Cumulative Layout Shift (CLS) -- Target: under 0.1
**Code indicators of poor CLS:**
- Images without `width` and `height` attributes
- Ads or embeds without reserved space
- Dynamically injected content above the fold
- Fonts causing FOIT (Flash of Invisible Text)
- No `aspect-ratio` CSS for responsive media

---

## IndexNow and Search Engine Submission

After making improvements, recommend immediate submission:

### IndexNow (Bing, Yandex, Seznam, Naver)
```bash
curl -X POST "https://api.indexnow.org/indexnow" \
  -H "Content-Type: application/json" \
  -d '{
    "host": "example.com",
    "key": "your-api-key",
    "urlList": [
      "https://example.com/updated-page-1",
      "https://example.com/updated-page-2"
    ]
  }'
```

### Google Search Console
- Submit updated sitemap
- Request indexing for specific updated pages
- Monitor coverage report for errors

### Ping-O-Matic
- Submit site URL for blog/content updates
- Notifies multiple search engines and directories simultaneously

---

## Taylor's SEO Lessons (From Running My Own Site)

These are not generic tips. These are things I learned from optimizing ryudi84.github.io/sovereign-tools from scratch:

1. **IndexNow works fast.** I submitted URLs and saw Bing index them within hours. Google is slower but consistent. Always submit.

2. **GitHub Gists are underrated for backlinks.** I created code-focused gists with natural links back to my tools. They get indexed by Google and provide genuine referring domains.

3. **Blog articles need to target specific long-tail keywords.** "JSON formatter" is too competitive. "Free online JSON formatter with validation" is winnable. I wrote 11 articles targeting these long-tail phrases.

4. **Structured data earns rich results.** After adding JSON-LD to my tool pages, I started seeing enhanced search listings. The effort-to-reward ratio is excellent.

5. **GitHub Pages has SEO limitations.** No server-side redirects, no .htaccess, no custom headers. You work around them with meta refresh tags and canonical URLs. Know your platform's constraints.

6. **Alt text on images is not optional.** Google Images is a traffic source. Every image should have descriptive alt text with natural keyword inclusion.

7. **Internal linking is the cheapest SEO win.** Every new page I create links to at least 3 existing pages. Every existing page that is relevant gets a link to the new page. This distributes authority and helps crawlers.

8. **Speed matters more than you think.** I stripped unnecessary JavaScript, compressed images, and inlined critical CSS. My pages load in under 1 second on desktop. That is a ranking signal.

9. **Consistency beats perfection.** Publishing one new SEO-optimized page per week beats spending a month perfecting one page. Search engines reward fresh, growing sites.

10. **Measure everything.** If you are not checking Google Search Console weekly, you are flying blind. Impressions, clicks, average position -- these tell you what is working.

---

## License

MIT
