---
name: website-seo
version: 1.0.0
description: Complete on-page SEO system for any website — page optimization, schema markup, technical SEO checklist, internal linking strategy, Core Web Vitals guidance, and AI-driven content gap analysis. Works for any CMS (WordPress, Webflow, Squarespace, custom).
tags: [seo, on-page-seo, technical-seo, schema-markup, core-web-vitals, wordpress, content-optimization]
author: contentai-suite
license: MIT
---

# Website SEO — Universal On-Page Optimization System

## What This Skill Does

Guides you through a complete website SEO audit and optimization process. Covers on-page elements, technical fundamentals, schema markup, and an ongoing optimization strategy that compounds over time.

## How to Use This Skill

**Input format:**
```
WEBSITE URL: [Your website]
CMS: [WordPress / Webflow / Squarespace / Shopify / Custom]
NICHE: [Your industry]
TARGET LOCATION: [Local / National / Global]
PRIORITY PAGES: [Homepage / Service pages / Blog / Product pages]
CURRENT ISSUES: [Known issues or "unknown — need full audit"]
GOAL: [Rank for specific keywords / Improve existing rankings / Fix technical issues]
```

---

## Phase 1: Page-Level Optimization

### Title Tag Optimization

**Formula:** `Primary Keyword — Secondary Keyword | Brand Name`

```
Rules:
- 50-60 characters maximum
- Primary keyword as close to the beginning as possible
- Each page must have a UNIQUE title
- Make it compelling for humans, not just crawlers

Bad: "Home | Company Name"
Good: "Personal Training Rotterdam — 1-on-1 Coaching | Brand Name"
```

### Meta Description Optimization

**Formula:** `[Benefit] + [Primary keyword] + [CTA]`

```
Rules:
- 150-160 characters
- Include primary keyword naturally
- Include a call-to-action
- Each page must have a UNIQUE meta description
- Think of it as a micro-ad for your page in search results

Prompt to generate:
"Write a meta description for a [PAGE TYPE] page about [TOPIC] for [BRAND NAME].
Primary keyword: [KEYWORD]. Audience: [AUDIENCE].
Max 155 characters. Include a benefit + soft CTA."
```

### Header Structure (H1-H6)

```
Rules:
- ONE H1 per page — contains primary keyword
- H2s: section headers — contain secondary/LSI keywords
- H3s: subsections
- Never skip levels (don't go H1 → H3)
- Headers should describe the content below them accurately

Audit prompt:
"Review the heading structure of this page: [paste page content]
Identify: missing H1, keyword opportunities in headers, hierarchy issues."
```

### Content Optimization

```
On-Page Content Checklist:
- [ ] Primary keyword in first 100 words
- [ ] Primary keyword appears naturally throughout (1-2% density)
- [ ] LSI keywords (related terms) used throughout
- [ ] Minimum 300 words for service pages, 800+ for blog posts
- [ ] Content answers the search intent (informational/commercial/navigational)
- [ ] Internal links to 2-3 relevant pages on your site
- [ ] External link to 1 authoritative source
- [ ] All images have descriptive alt text

Content optimization prompt:
"Optimize this content for the keyword [KEYWORD]:
[Paste your existing content]
Suggest: where to add the keyword naturally, missing LSI terms,
structural improvements, and any thin content sections to expand."
```

---

## Phase 2: Technical SEO Essentials

### Core Technical Checklist

```
INDEXABILITY:
- [ ] robots.txt exists and doesn't block important pages
- [ ] XML sitemap submitted to Google Search Console
- [ ] No important pages with noindex tag
- [ ] Canonical tags set correctly

PERFORMANCE:
- [ ] Page loads under 3 seconds (test: PageSpeed Insights)
- [ ] Images compressed and in WebP format where possible
- [ ] Minified CSS and JavaScript
- [ ] Browser caching enabled

MOBILE:
- [ ] Mobile-responsive design
- [ ] No intrusive interstitials on mobile
- [ ] Tap targets large enough (48×48px minimum)
- [ ] Text readable without zooming

CRAWLABILITY:
- [ ] Clean URL structure (yoursite.com/service-name not yoursite.com/p=123)
- [ ] No broken internal links
- [ ] No redirect chains (A→B→C, should be A→C directly)
- [ ] HTTPS enabled on all pages

CORE WEB VITALS:
- [ ] LCP (Largest Contentful Paint) < 2.5 seconds
- [ ] CLS (Cumulative Layout Shift) < 0.1
- [ ] FID/INP (Interaction to Next Paint) < 200ms
```

### URL Structure Best Practices

```
Good URL structure:
yoursite.com/service/keyword-based-page-name
yoursite.com/blog/topic-keyword-post-title

Bad URL structure:
yoursite.com/page?id=123
yoursite.com/2024/01/01/blog/post
yoursite.com/my-awesome-service-page-click-here

Rules:
- Use hyphens (-) not underscores (_)
- Lowercase only
- Include primary keyword
- Remove stop words (the, a, and, or) where possible
- Keep it short — under 60 characters ideal
```

---

## Phase 3: Schema Markup

Schema markup tells search engines exactly what your content means, enabling rich snippets.

### Most Valuable Schema Types

**Local Business (for location-based businesses):**
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "[Business Name]",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[Street]",
    "addressLocality": "[City]",
    "postalCode": "[Code]",
    "addressCountry": "[Country Code]"
  },
  "telephone": "[Phone]",
  "url": "[Website URL]",
  "openingHours": ["Mo-Fr 09:00-17:00"],
  "priceRange": "$$"
}
```

**Article/Blog Post:**
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[Post Title]",
  "author": {"@type": "Person", "name": "[Author Name]"},
  "datePublished": "[ISO Date]",
  "description": "[Meta Description]"
}
```

**FAQ (for Q&A sections):**
```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [{
    "@type": "Question",
    "name": "[Question text]",
    "acceptedAnswer": {
      "@type": "Answer",
      "text": "[Answer text]"
    }
  }]
}
```

**Schema generation prompt:**
```
Generate [SCHEMA TYPE] schema markup for [BUSINESS NAME].
Details: [provide business details, page content, or FAQ content]
Output: valid JSON-LD format ready to add to the page <head>
```

---

## Phase 4: Internal Linking Strategy

Internal links distribute page authority and help users navigate your site.

**Hub and Spoke Model:**
```
PILLAR PAGE (broad topic) → linked to by all related pages
CLUSTER PAGES (specific subtopics) → each links back to pillar page

Example:
Pillar: "Ultimate Guide to [Your Service]"
Clusters:
- "[Specific aspect 1] Explained"
- "How to [specific task] — Step by Step"
- "[Topic] for Beginners"
- "[Advanced topic] Guide"
```

**Internal linking rules:**
- Link from high-traffic pages to pages you want to rank
- Use descriptive anchor text (not "click here" or "read more")
- Add 2-3 internal links per new page or post
- Audit broken internal links quarterly

---

## Phase 5: Ongoing SEO Monitoring

### Monthly SEO Audit Checklist

```
RANKING:
- [ ] Check Google Search Console for position changes
- [ ] Identify keywords dropped — investigate why
- [ ] Find new keyword opportunities from "Queries" report

TECHNICAL:
- [ ] Check for new crawl errors in GSC
- [ ] Review Core Web Vitals report
- [ ] Check any new 404 errors

CONTENT:
- [ ] Update any outdated statistics or information
- [ ] Add internal links from new content to older pages
- [ ] Identify thin pages (under 300 words) for expansion
```

### SEO Audit Prompt
```
I'm auditing [WEBSITE URL] for [NICHE] targeting [KEYWORDS].
Based on SEO best practices, identify the top 10 issues to fix.
Priority order: technical issues → on-page → content gaps → link opportunities.
Format: Issue | Impact (High/Medium/Low) | Recommended fix
```

---

## Use with ContentAI Suite

This skill works seamlessly with **[ContentAI Suite](https://contentai-suite.vercel.app)** — a free multi-agent marketing platform that generates professional content for any business in minutes.

→ **Try it free:** https://contentai-suite.vercel.app
