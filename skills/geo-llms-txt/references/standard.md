# The llms.txt Standard

## Purpose

llms.txt is a proposed standard that helps AI systems (LLMs) understand website structure and find important content. It serves a similar purpose for AI crawlers as robots.txt does for search engines.

## Why It Matters

AI platforms like ChatGPT, Perplexity, Claude, and Gemini need to:
1. Quickly understand what a site/company does
2. Find authoritative, up-to-date information
3. Distinguish high-value content from low-value pages
4. Cite sources accurately

Without guidance, AI crawlers may:
- Miss important pages entirely
- Cite outdated or less relevant content
- Misunderstand brand positioning
- Waste crawl budget on low-priority URLs

## File Location

Place at the root of your domain:
```
https://example.com/llms.txt
```

Requirements:
- Must return HTTP 200
- No authentication required
- Plain text or markdown format

## Standard Structure

### Header Block

```markdown
# Brand Name

> One-sentence description of what the company/product does.
> Keep it factual and specific. Avoid superlatives.

Paragraph 1: What the product/service does, who it's for,
and the core problem it solves.

Paragraph 2: Key differentiators, notable features,
or unique approach. Include specific capabilities.

Paragraph 3 (optional): Target audience, use cases,
or industry context.
```

### Content Sections

Organize links into logical sections. Common patterns:

#### For SaaS/Products
- Key Pages (homepage, about, pricing)
- Products / Features
- Documentation / API Reference
- Blog / Resources
- Company (about, careers, contact)

#### For Publishers
- Key Pages
- Top Articles (by traffic/importance)
- Categories / Topics
- Author Pages
- About / Contact

#### For E-commerce
- Key Pages
- Product Categories
- Top Products
- Buying Guides
- Support / FAQ

### Link Format

```markdown
## Section Name

- [Page Title](https://example.com/page): Description of what this page covers
```

Rules:
- Use bullet points with `-`
- Link text = page title (not URL)
- One-line description after colon
- Full URLs (including https://)

### Description Guidelines

**Good descriptions:**
- Explain what the user will learn/find
- Include key entities and facts
- Stay under 15 words
- Match the actual page content

**Bad descriptions:**
- "Our amazing product page" (vague)
- "Click here to learn more" (no information)
- "The best solution on the market" (promotional)
- "Various features and benefits" (too general)

## Link Curation

### How Many Links?

**Recommended: 15-40 links**

- Too few (<10): AI may miss important context
- Sweet spot (15-40): Curated, high-value pages
- Too many (>50): Noise, diluted signal

### What to Include

**Must have:**
- Homepage
- About page (establishes entity)
- Key product/feature pages
- Most important documentation
- 3-5 top articles/resources

**Should have:**
- Pricing (if SaaS)
- API docs (if developer tool)
- Case studies / testimonials
- FAQ / support hub

**Avoid:**
- Login pages
- User-specific content
- Duplicate/similar pages
- Outdated content
- Auto-generated pages

## Comparison with Similar Files

| File | Purpose | Audience |
|------|---------|----------|
| robots.txt | Tell crawlers what NOT to index | Search engines |
| sitemap.xml | List all indexable URLs | Search engines |
| llms.txt | Guide AI to most valuable content | AI platforms |

**Key difference:** llms.txt is *curated* and *semantic*, not comprehensive.

## Platform Support

As of 2024, llms.txt is:
- ✅ Supported by Anthropic (Claude)
- ✅ Supported by Perplexity
- 🟡 Partially supported by OpenAI
- 🟡 Community standard (not official)

Even without universal adoption, it helps organize thinking about AI-ready content.

## History

The llms.txt standard was proposed by Anthropic in 2024 as a way for websites to provide structured information to AI systems. It draws inspiration from:
- robots.txt (1994)
- humans.txt (2011)
- security.txt (2017)

## Related Standards

- **robots.txt**: Crawl control for search engines
- **sitemap.xml**: URL discovery for search engines  
- **security.txt**: Security contact information
- **humans.txt**: Team credits and site information