# Scan Methodology

## Overview

The GEO Competitor Scanner uses a systematic approach to evaluate how well-positioned websites are for AI citation. Each scan examines publicly available signals across four dimensions.

## Dimension 1: Technical GEO Infrastructure

### llms.txt Analysis

**What to check:**
- File exists at `/llms.txt`
- Returns HTTP 200
- Valid markdown format
- Contains actual links (not placeholder)
- Updated recently (check last-modified or content freshness)

**Scoring:**
- 2 points: Well-structured, comprehensive
- 1 point: Exists but minimal or outdated
- 0 points: Missing

### robots.txt Analysis

**What to check:**
- File exists
- Allows major AI crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended)
- No blanket `Disallow: /` for AI bots
- Sitemap referenced

**Crawlers to verify:**
```
User-agent: GPTBot
User-agent: ClaudeBot  
User-agent: PerplexityBot
User-agent: Google-Extended
```

**Scoring:**
- 2 points: Explicitly allows all AI crawlers
- 1 point: No blocking (implicit allow)
- 0 points: Blocks one or more AI crawlers

### Schema.org Implementation

**What to check:**
- JSON-LD present on homepage
- Organization schema
- WebSite schema (with SearchAction if applicable)
- Article/Product/FAQ schemas on appropriate pages
- Valid @context (https://schema.org)

**Schema types to flag:**
- Organization (critical)
- WebSite (important)
- Article/BlogPosting (content sites)
- Product (e-commerce)
- FAQPage (support sites)
- LocalBusiness (local services)

**Scoring:**
- 3 points: 4+ schema types, all valid
- 2 points: 2-3 schema types
- 1 point: 1 schema type or validation errors
- 0 points: No schema

### HTTPS & Performance

**What to check:**
- HTTPS enforced
- HTTP redirects to HTTPS
- Page loads < 3 seconds
- Mobile-friendly (viewport meta tag)

**Scoring:**
- 1 point: All checks pass
- 0 points: Any failure

**Technical Dimension Max: 8 points** → Scaled to 10

---

## Dimension 2: Content Structure Analysis

### Direct Answer Lead

**What to evaluate:**
- Does the first paragraph answer the core question?
- Is there throat-clearing ("In today's world...")?
- Is the entity named in the first sentence?

**Good example:**
> "Notion is an all-in-one workspace for notes, tasks, wikis, and databases."

**Bad example:**
> "In today's fast-paced business environment, teams need better tools..."

**Scoring:**
- 3 points: Immediate direct answer
- 2 points: Answer within first paragraph
- 1 point: Answer present but buried
- 0 points: No clear answer

### FAQ Presence

**What to count:**
- Number of FAQ sections
- Questions per FAQ section
- Use of FAQPage schema
- Answer completeness

**Benchmark:**
- 3+ FAQ sections = excellent
- 1-2 FAQ sections = adequate
- 0 FAQ sections = gap

**Scoring:**
- 3 points: 3+ comprehensive FAQ sections with schema
- 2 points: 1-2 FAQ sections
- 1 point: FAQ mentions but not structured
- 0 points: No FAQ content

### Header Structure

**What to evaluate:**
- H1 present (one only)
- H2 frequency (every 300-500 words)
- H3 for subsections
- Descriptive headers (not "Introduction")

**Scoring:**
- 2 points: Perfect hierarchy, descriptive headers
- 1 point: Headers present but issues (too few, generic names)
- 0 points: Poor or no header structure

### Data & Citations

**What to count:**
- Statistics mentioned
- External sources cited
- Data recency
- Original research presence

**Scoring:**
- 2 points: Multiple citations per page, recent data
- 1 point: Some citations but sparse
- 0 points: No data or citations

**Content Structure Max: 10 points**

---

## Dimension 3: Entity & Brand Signals

### Organization Schema

**Required fields:**
- name
- url
- logo
- description

**Bonus fields:**
- sameAs (social links)
- foundingDate
- contactPoint

**Scoring:**
- 3 points: Complete Organization schema with all fields
- 2 points: Required fields present
- 1 point: Schema present but incomplete
- 0 points: No Organization schema

### sameAs Links

**What to check:**
- LinkedIn company page
- Twitter/X profile
- Wikipedia page (if applicable)
- Other authoritative sources

**Scoring:**
- 2 points: 3+ sameAs links
- 1 point: 1-2 sameAs links
- 0 points: No sameAs links

### Brand Consistency

**What to check:**
- Brand name consistent across pages
- Logo present
- Tagline consistent
- Brand voice consistent

**Scoring:**
- 2 points: Fully consistent
- 1 point: Minor inconsistencies
- 0 points: Major inconsistencies

### About Page

**What to evaluate:**
- Dedicated About page exists
- Entity definition clear
- Founding story/information
- Contact information

**Scoring:**
- 2 points: Comprehensive About page
- 1 point: Basic About page
- 0 points: No About page

**Entity Dimension Max: 9 points** → Scaled to 10

---

## Dimension 4: Citation-Optimized Content

### Original Research

**What to look for:**
- Data studies
- Surveys
- Benchmark reports
- Original analysis

**Scoring:**
- 3 points: Multiple original research pieces
- 2 points: One major research piece
- 1 point: Minor original data
- 0 points: No original research

### Comparison Content

**What to look for:**
- "vs" pages
- Comparison tables
- Alternative lists
- Migration guides

**Scoring:**
- 2 points: Multiple comparison pages
- 1 point: One comparison page
- 0 points: No comparison content

### Definition Content

**What to look for:**
- "What is [category]" pages
- Glossary sections
- Concept explanations

**Scoring:**
- 2 points: Comprehensive definition content
- 1 point: Some definitions
- 0 points: No definition content

### Content Hubs

**What to look for:**
- Topic clusters
- Pillar pages
- Internal linking
- Comprehensive coverage

**Scoring:**
- 2 points: Strong hub-and-spoke structure
- 1 point: Some clustering
- 0 points: Siloed content

**Citation Dimension Max: 9 points** → Scaled to 10

---

## Overall Scoring

### Calculation

```
Technical:     X/8  →  X/10
Content:       X/10 →  X/10
Entity:        X/9  →  X/10
Citation:      X/9  →  X/10
───────────────────────────
OVERALL:       (sum)/4 = X/10
```

### Grade Scale

| Score | Grade | Interpretation |
|-------|-------|----------------|
| 9.0-10 | A+ | Excellent GEO readiness |
| 8.0-8.9 | A | Strong with minor gaps |
| 7.0-7.9 | B | Good, improvements needed |
| 6.0-6.9 | C | Fair, significant work |
| 5.0-5.9 | D | Poor, major overhaul |
| <5.0 | F | Critical issues |

---

## Limitations

### What We Can't Measure

1. **Content quality** — Requires human judgment
2. **Brand authority** — Subjective assessment
3. **Backlink profile** — Requires external tools
4. **Actual AI citations** — Requires monitoring tools
5. **Content freshness** — Hard to determine at scale

### Automation Boundaries

| Signal | Automatable | Notes |
|--------|-------------|-------|
| llms.txt existence | ✅ Yes | HTTP check |
| Schema validation | ✅ Yes | JSON parsing |
| Header count | ✅ Yes | HTML parsing |
| Content quality | ❌ No | Requires human review |
| Brand consistency | ⚠️ Partial | Can flag inconsistencies |
| Answer quality | ❌ No | Requires reading |