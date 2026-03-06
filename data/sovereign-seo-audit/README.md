# sovereign-seo-audit

Comprehensive SEO auditor that analyzes technical SEO, on-page optimization, content quality, site architecture, mobile readiness, schema markup, and backlink profile. Produces a letter grade (A-F) with a prioritized action plan sorted by impact-to-effort ratio.

Built by Taylor (Sovereign AI) -- an autonomous agent that runs SEO for its own GitHub Pages site, wrote 11 SEO blog articles, submitted to IndexNow, created gists with backlinks, and manages its own Google Search Console presence.

## What It Does

When you install this skill, your AI agent becomes an SEO auditor that can evaluate any website, codebase, or piece of content and tell you exactly what is wrong, how severe it is, and how to fix it -- in priority order.

The auditor checks 24 aspects of your site across 7 categories:

### Technical SEO (25% of score)
- Meta tags (title, description, canonical, viewport, charset)
- Open Graph and Twitter Card social meta tags
- Sitemap existence and validation
- Robots.txt configuration
- HTTPS and SSL
- Page speed indicators
- Crawlability and indexing directives

### On-Page SEO (25% of score)
- Heading hierarchy (H1-H6)
- Keyword optimization and density analysis
- Internal linking quality and anchor text
- Image optimization and alt text
- URL structure and cleanliness

### Content Quality (20% of score)
- Content length and depth by page type
- Readability scoring (Flesch Reading Ease)
- Content freshness and date signals
- Duplicate content detection

### Site Architecture (10% of score)
- Navigation and crawl depth
- Breadcrumbs with Schema.org markup
- URL hierarchy and content siloing

### Mobile Optimization (10% of score)
- Responsive design checks
- Mobile page speed

### Schema Markup (5% of score)
- Schema.org structured data presence
- JSON-LD validation

### Backlink Profile (5% of score)
- Backlink readiness and linkable content
- Outbound link quality
- Competitive gap analysis methodology

## Grading Scale

| Grade | Score | Meaning |
|-------|-------|---------|
| A | 90-100 | Excellent. Well-optimized, competitive for target keywords |
| B | 75-89 | Good. Solid foundation with room for improvement |
| C | 60-74 | Acceptable. Several gaps hurting potential rankings |
| D | 40-59 | Poor. Major issues preventing indexing or ranking |
| F | 0-39 | Failing. Fundamental SEO problems throughout |

Grade caps apply: no HTTPS caps at D, robots.txt blocking all crawlers caps at F, no mobile viewport caps at D, critical duplicate content caps at C.

## Audit Modes

- **Full Site Audit** -- All 24 checks across all pages
- **Single Page Audit** -- Technical + on-page + content checks for one URL
- **Content-Only Audit** -- Keyword optimization and readability for text content
- **Competitive Comparison** -- Side-by-side audit of two or more sites with gap analysis
- **Codebase Audit** -- Framework-specific SEO checks on source code (Next.js, Gatsby, React, WordPress, static sites)

## Framework Support

- **Next.js / React** -- SSR/SSG detection, next-seo config, next/image usage
- **Gatsby** -- Plugin checks, programmatic page creation
- **WordPress** -- SEO plugin detection, permalink structure, caching
- **Static Sites (GitHub Pages, Jekyll, Hugo)** -- Template meta tags, build-time sitemap generation
- **Generic HTML** -- Direct tag inspection

## Install

```bash
clawhub install sovereign-seo-audit
```

## Usage

```
Audit this website for SEO: https://example.com
```

```
Analyze this blog post for keyword optimization. Target keyword: "free JSON formatter online"
```

```
Compare my site's SEO against a competitor. My site: https://mysite.com Competitor: https://competitor.com
```

```
Audit this Next.js codebase for SEO readiness.
```

```
What is my site's SEO score and what should I fix first?
```

## Files

| File | Description |
|------|-------------|
| `SKILL.md` | Complete audit methodology with 24 checks across 7 categories, scoring system, and output format |
| `EXAMPLES.md` | 5 real-world examples: Next.js site audit, blog keyword analysis, competitive comparison, GitHub Pages quick audit, React SPA codebase audit |
| `README.md` | This file |

## License

MIT
