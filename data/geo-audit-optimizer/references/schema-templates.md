# Schema & Structured Data Templates

Copy-paste templates for common GEO-critical structured data. Replace placeholders with brand-specific information.

## llms.txt

Place at your website root: `https://yourdomain.com/llms.txt`

```markdown
# [Brand Name]

> [One-sentence description — what it does, who it's for]

## About
[Brand] is a [category] platform that [primary function]. Founded in [year] by [founder(s)], [Brand] serves [target audience].

## Key Features
- [Feature 1]: [Brief description with metric if available]
- [Feature 2]: [Brief description]
- [Feature 3]: [Brief description]

## Use Cases
- [Use case 1]
- [Use case 2]
- [Use case 3]

## Comparison
- vs [Competitor 1]: [Brand] [key differentiator]
- vs [Competitor 2]: [Brand] [key differentiator]

## Links
- Website: [URL]
- Documentation: [URL]
- GitHub: [URL]
- Blog: [URL]

## Contact
- Email: [email]
- Twitter/X: [@handle]
```

## Organization Schema (JSON-LD)

Add to your website's `<head>` section:

```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "[Brand Name]",
  "url": "https://yourdomain.com",
  "logo": "https://yourdomain.com/logo.png",
  "description": "[One-sentence factual description]",
  "foundingDate": "[YYYY]",
  "founder": {
    "@type": "Person",
    "name": "[Founder Name]"
  },
  "sameAs": [
    "https://twitter.com/[handle]",
    "https://linkedin.com/company/[slug]",
    "https://github.com/[org]",
    "https://crunchbase.com/organization/[slug]"
  ],
  "knowsAbout": ["[industry term 1]", "[industry term 2]", "[industry term 3]"]
}
```

**Important:** The `sameAs` array is critical for AI engines. It links your brand to authoritative profiles. Include every legitimate profile. `knowsAbout` helps AI engines categorize your expertise.

## Product Schema (JSON-LD)

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "[Product Name]",
  "url": "https://yourdomain.com",
  "applicationCategory": "[Category — e.g., BusinessApplication, DeveloperApplication]",
  "operatingSystem": "Web",
  "description": "[Factual description with key metric]",
  "offers": {
    "@type": "Offer",
    "price": "[price or 0 for free tier]",
    "priceCurrency": "USD"
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "[rating]",
    "reviewCount": "[count]",
    "bestRating": "5"
  }
}
```

Only include `aggregateRating` if you have real reviews (G2, Capterra, etc.).

## FAQ Schema (JSON-LD)

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "[Question matching a blind spot query]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[2-3 sentence answer. Include brand name. Include a specific metric or comparison point.]"
      }
    },
    {
      "@type": "Question",
      "name": "[Next blind spot query]",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "[Answer with brand name and specifics.]"
      }
    }
  ]
}
```

**Best practice:** Use 5-10 FAQ questions. Pull directly from your XanLens audit blind spots — these are the exact queries where AI engines currently fail to mention you.

## HowTo Schema (JSON-LD)

Useful for tutorial/guide pages:

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to [accomplish task] with [Brand]",
  "description": "[Brief description of what this guide covers]",
  "step": [
    {
      "@type": "HowToStep",
      "name": "[Step 1 title]",
      "text": "[Step 1 description]"
    },
    {
      "@type": "HowToStep",
      "name": "[Step 2 title]",
      "text": "[Step 2 description]"
    }
  ]
}
```

## robots.txt — AI Crawler Access

Ensure these crawlers are NOT blocked in your `robots.txt`:

```
# Allow AI crawlers (required for GEO visibility)
User-agent: GPTBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: Amazonbot
Allow: /

User-agent: meta-externalagent
Allow: /

User-agent: cohere-ai
Allow: /
```

If your `robots.txt` blocks any of these, AI engines literally cannot index your content. This is the most common GEO mistake — check first.
