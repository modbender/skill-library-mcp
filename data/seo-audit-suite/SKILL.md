---
name: seo-audit-suite
description: "Comprehensive SEO and GEO audit toolkit for OpenClaw agents. Run on-page audits, technical SEO checks, competitor analysis, keyword tracking, and GEO (Generative Engine Optimization) scoring. Generates PDF reports. Use when: (1) auditing a website for SEO issues, (2) analyzing competitors, (3) tracking keyword rankings, (4) checking technical SEO health, (5) evaluating GEO readiness for AI search engines, (6) generating SEO reports for clients, or (7) monitoring site performance over time."
---

# SEO Audit Suite

Production-grade SEO and GEO auditing from your OpenClaw agent. Crawl pages, score them, find issues, track progress, and generate client-ready reports.

## Setup

### Dependencies

```bash
pip3 install requests beautifulsoup4 lxml
```

Optional for advanced features:
- `GOOGLE_SEARCH_CONSOLE_KEY` — JSON key file for Search Console API
- `BRAVE_API_KEY` — Already configured if web_search works
- `PAGESPEED_API_KEY` — Google PageSpeed Insights (free, 25k queries/day)

### Workspace

All data lives in `~/.openclaw/workspace/seo-audit/`:

```
seo-audit/
├── config.json          # API keys, default settings
├── sites/               # Per-site audit data
│   └── example.com/
│       ├── audits/      # Timestamped audit results
│       ├── keywords/    # Keyword tracking data
│       └── competitors/ # Competitor analysis
├── reports/             # Generated PDF/MD reports
└── templates/           # Report templates
```

Run `scripts/init-workspace.sh` to create this structure.

## Core Workflows

### 1. On-Page SEO Audit

Crawl a URL and audit all on-page SEO factors:

```bash
scripts/audit-page.sh "https://example.com" [--depth 1]
```

**Checks performed:**
- **Title tag** — exists, length (50-60 chars), keyword presence
- **Meta description** — exists, length (150-160 chars), compelling
- **H1 tag** — exactly one, contains primary keyword
- **Header hierarchy** — proper H1→H2→H3 nesting
- **Image alt text** — all images have descriptive alt attributes
- **Internal links** — count, anchor text quality, orphan pages
- **External links** — count, nofollow usage, broken links
- **Word count** — minimum 300 for ranking, ideal 1500+ for competitive terms
- **Keyword density** — primary keyword appears naturally (1-3%)
- **Schema markup** — JSON-LD structured data present and valid
- **Open Graph / Twitter cards** — social sharing metadata
- **Canonical tag** — exists, self-referencing or correct
- **URL structure** — clean, keyword-rich, no parameters

Output: JSON audit result + human-readable summary.

### 2. Technical SEO Audit

Check the technical foundation:

```bash
scripts/audit-technical.sh "https://example.com"
```

**Checks performed:**
- **Page speed** — Core Web Vitals via PageSpeed API (LCP, FID, CLS)
- **Mobile friendliness** — viewport meta, responsive design signals
- **HTTPS** — SSL certificate valid, no mixed content
- **Robots.txt** — exists, not blocking important pages
- **XML sitemap** — exists, valid, submitted
- **Crawlability** — no noindex on important pages, proper canonicals
- **404 errors** — broken internal links
- **Redirect chains** — no chains longer than 2 hops
- **Duplicate content** — similar title/meta across pages
- **hreflang** — international targeting (if applicable)
- **Structured data** — valid JSON-LD, no errors

### 3. GEO (Generative Engine Optimization) Audit

Score a page's readiness for AI search engines (ChatGPT, Perplexity, Google AI Overviews):

```bash
scripts/audit-geo.sh "https://example.com"
```

**GEO-specific checks:**
- **Content structure** — clear Q&A format, definition patterns
- **Entity clarity** — unambiguous mentions of people, places, brands
- **Citation-worthiness** — stats, data points, unique insights present
- **Concise answers** — key info in first 2-3 sentences of sections
- **Topical authority signals** — depth of content, internal linking to related topics
- **Schema richness** — FAQ, HowTo, Article schema
- **Brand mentions** — consistent NAP (Name, Address, Phone), entity associations
- **Source credibility signals** — author bios, about pages, E-E-A-T indicators

Output: GEO readiness score (0-100) with specific improvement recommendations.

### 4. Competitor Analysis

Analyze competitors for a target keyword or domain:

```bash
scripts/analyze-competitor.sh --keyword "ai seo tools" [--competitors "site1.com,site2.com"]
```

If no competitors specified, auto-discovers top 10 ranking pages via Brave Search.

**Analysis includes:**
- Content length comparison
- Keyword usage patterns
- Header structure
- Schema markup comparison
- Backlink profile (if Ahrefs/Moz API available)
- Content gaps — topics competitors cover that you don't
- GEO readiness comparison

### 5. Keyword Tracking

Track keyword rankings over time:

```bash
scripts/track-keywords.sh --site "example.com" --keywords "keyword1,keyword2,keyword3"
scripts/track-keywords.sh --site "example.com" --report  # Show ranking changes
```

- Checks current position via Brave Search
- Stores history in `sites/<domain>/keywords/`
- Alerts on significant ranking changes (±5 positions)
- Weekly trend reports

### 6. Report Generation

Generate client-ready reports:

```bash
scripts/generate-report.sh --site "example.com" --type full    # Complete audit
scripts/generate-report.sh --site "example.com" --type summary  # Executive summary
scripts/generate-report.sh --site "example.com" --type geo      # GEO-focused
scripts/generate-report.sh --site "example.com" --type monthly  # Monthly progress
```

Reports include:
- Overall score (0-100) with letter grade
- Priority issues ranked by impact
- Specific fix recommendations with examples
- Competitor benchmarking
- Progress tracking (if previous audits exist)
- GEO readiness section

Output formats: Markdown (default), HTML (for email/web).

## Scoring System

Each audit produces scores across categories:

| Category | Weight | What It Measures |
|----------|--------|-----------------|
| On-Page | 25% | Content, tags, structure |
| Technical | 25% | Speed, mobile, crawlability |
| GEO | 20% | AI search readiness |
| Content Quality | 15% | Depth, uniqueness, authority |
| User Experience | 15% | Core Web Vitals, navigation |

**Overall grade:** A (90-100), B (80-89), C (70-79), D (60-69), F (<60)

## Cron Integration

- **Weekly audit:** Re-run full audit every Monday, compare to previous
- **Daily keyword check:** Track rankings daily, alert on big moves
- **Monthly report:** Auto-generate and deliver to configured email/channel

## References

- `references/scoring-rubric.md` — Detailed scoring criteria for each check
- `references/geo-optimization.md` — Deep dive on GEO strategies and AI search ranking factors
- `references/search-console-setup.md` — Google Search Console API integration guide
