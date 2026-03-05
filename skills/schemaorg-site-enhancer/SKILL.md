---
name: schemaorg-site-enhancer
description: Enhances agent-built websites with proper schema.org structured data for SEO, rich snippets, and search engine visibility. Use when creating or improving websites to add JSON-LD markup for organizations, products, articles, events, and more. Provides templates, generators, and validation guidance.
---

# Schema.org Site Enhancer

## Overview

This skill helps agents integrate schema.org structured data into websites, enabling rich search results, better SEO, and improved communication with search engines. It provides ready-to-use JSON-LD templates, generation scripts, and implementation patterns for common schema types.

## When to Use This Skill

Use this skill when:
- Building new websites that need SEO-optimized structured data
- Enhancing existing sites with schema.org markup
- Generating JSON-LD for organizations, products, articles, blog posts, events, FAQs, or local business info
- Validating schema markup against schema.org standards
- Creating reusable templates for recurring site types

**Triggers:**
- "Add schema.org markup to this site"
- "Generate JSON-LD for [product/article/event]"
- "Improve SEO with structured data"
- "Create schema template for [type]"
- "Validate my schema.org implementation"

## Core Capabilities

1. **JSON-LD Template Generation** – Produce ready-to-insert JSON-LD scripts for 15+ common schema types
2. **Custom Schema Construction** – Build tailored structured data from user-provided details
3. **Validation Guidance** – Check markup against schema.org specs and Google's rich result guidelines
4. **Template Reuse** – Maintain consistent structured data across multiple pages/sites
5. **Auto-Integration Patterns** – Guidance for injecting schema into HTML frameworks (React, Next.js, plain HTML)

## Quick Start

### Basic Usage

When a user asks for schema.org markup:

1. Identify the schema type needed (Organization, Product, Article, etc.)
2. Gather required properties from the user or existing site content
3. Generate JSON-LD using the appropriate template
4. Provide instructions for adding `<script type="application/ld+json">` to HTML
5. Optionally validate with Google's Rich Results Test

### Example Requests

- "Add schema.org markup for my freelance portfolio" → Organization + Person
- "I'm selling handmade jewelry, add product schema" → Product with price, availability, brand
- "My blog needs article schema for better SEO" → BlogPosting with author, date, image
- "We host tech meetups, add Event schema" → Event with location, dates, organizer
- "Create FAQ schema for this page" → FAQPage with questions and answers

## Schema Types Supported

### Essential (Always Available)
- **Organization** – Company, agency, institution
- **Person** – Individual profiles
- **WebSite** – Site-wide metadata, search action
- **WebPage** – Generic page markup
- **Article** / **BlogPosting** – News and blog content

### Commerce
- **Product** – Items for sale (price, availability, SKU)
- **Offer** – Pricing and availability details
- **AggregateRating** – Review summaries
- **Brand** – Manufacturer or brand info

### Local & Events
- **LocalBusiness** –Physical business locations
- **Place** – Generic location data
- **Event** – Meetups, conferences, webinars
- **Venue** – Event locations

### Content & Media
- **VideoObject** – Embedded videos
- **ImageObject** – Photos and graphics
- **AudioObject** – Podcasts, sound clips

### Interactive
- **FAQPage** – Frequently asked questions
- **HowTo** – Step-by-step instructions
- **Recipe** – Cooking instructions (ingredients, steps, nutrition)
- **Review** – Individual reviews

## Implementation Patterns

### Pattern 1: Static HTML Injection

For plain HTML or static sites, add JSON-LD directly in `<head>`:

```html
<head>
  <!-- other head content -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "Your Company",
    "url": "https://example.com",
    "logo": "https://example.com/logo.png"
  }
  </script>
</head>
```

### Pattern 2: React / Next.js Component

Create a reusable component:

```jsx
// components/JsonLd.js
export function JsonLd({ data }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}

// Usage in page:
<JsonLd data={{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Your Post Title",
  "author": { "@type": "Person", "name": "Author Name" },
  "datePublished": "2025-02-20T10:00:00Z"
}} />
```

### Pattern 3: Template Variables

Use placeholders for dynamic values:

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{{product_name}}",
  "description": "{{product_description}}",
  "offers": {
    "@type": "Offer",
    "price": "{{price}}",
    "priceCurrency": "USD"
  }
}
```

Replace `{{variables}}` with actual data.

## Best Practices

- **Use JSON-LD** – Preferred format; easier to maintain than Microdata or RDFa
- **Keep it current** – Schema.org evolves; use stable versions (@context: "https://schema.org")
- **Only include relevant properties** – Quality over quantity; avoid empty fields
- **Validate** – Google Rich Results Test, Schema.org validator
- **Test rich results** – Not all schema triggers rich snippets; follow Google's guidelines
- **Avoid duplication** – Each page should have unique structured data; don't copy-paste identical JSON-LD across pages
- **Performance** – JSON-LD is lightweight; keep it under few KB per page

## Resources

### scripts/
Python utilities for generating and validating schema.org markup.

- `generate_jsonld.py` – Main generator function for all supported types
- `validate_schema.py` – Local validation against schema.org definitions
- `templates/` – JSON-LD templates with placeholders

### references/
Detailed documentation:

- `schema_types.md` – Quick reference for all supported schema types and required/optional properties
- `google_guidelines.md` – Google's rich result requirements and eligibility
- `examples.md` – Complete examples for each schema type in realistic scenarios

### assets/
Boilerplate templates:

- `html-head-injection.html` – Snippet showing where to place JSON-LD in HTML
- `react-component-template.jsx` – Next.js/React component starter
- `vue-component-template.vue` – Vue 3 component for Nuxt/Vite projects

## Advanced: Custom Schema Construction

When a standard type doesn't fit, combine multiple types or use `Thing` subclasses. For example, a software product may combine `Product` + `SoftwareApplication`.

See `references/schema_extensions.md` for composition patterns.

## Troubleshooting

**Q: Rich snippets not appearing in search**
- Validate with Google's tool
- Check eligibility (some types require manual review)
- Ensure page is indexed and not blocked by robots.txt
- Be patient – rich results can take weeks to appear

**Q: Schema validation errors**
- Use correct @context: "https://schema.org"
- Required properties missing? Add mandatory fields for that type
- Property names are case-sensitive; use camelCase (e.g., `datePublished`, not `date_published`)

**Q: Multiple schemas on one page**
- Use an array: `[ { "@type": "Article" }, { "@type": "Organization" } ]`
- Or separate `<script>` tags (both fine)

## Next Steps

After adding schema.org markup:
1. Test with [Google Rich Results Test](https://search.google.com/test/rich-results)
2. Monitor Search Console for rich result appearance
3. Update structured data when content changes (price, dates, availability)

---

## Resources

This skill bundles generators, validators, and templates to streamline schema.org implementation.

### scripts/

**`generate_jsonld.py`** — Python library for generating JSON-LD for 15+ schema types.  
**`generate_jsonld_cli.py`** — Command-line interface for the generator (optional, for local use).  
**`validate_schema.py`** — Validates JSON-LD structure, required fields, and date formats.

**Usage from Python:**

```python
from generate_jsonld import generate_schema, format_jsonld

data = generate_schema("Organization", name="Acme", url="https://acme.com")
print(format_jsonld(data))
```

**Usage from CLI:**

```bash
python generate_jsonld_cli.py Product --name "Widget" --brand "Acme" --price 29.99 --url "https://shop.example.com/widget" --output schema.json
python validate_schema.py schema.json
```

### references/

- **`schema_types.md`** — Quick reference of all supported types and their required/optional parameters.
- **`google_guidelines.md`** — Google's rich result eligibility rules and best practices.
- **`examples.md`** — Complete real-world examples: portfolio, blog article, product, event, local business, FAQ, recipe, how-to, etc.

Read these when you need to:
- Check which properties are required for a given type
- Validate against Google's policies
- Copy/paste a realistic example and adapt

### assets/

- **`html-head-injection.html`** — Plain HTML template showing exactly where to place JSON-LD in `<head>`.
- **`react-component-template.jsx`** — Reusable React components (`<JsonLd>`, `<OrganizationJsonLd>`, `<ProductJsonLd>`, etc.) for Next.js and other React apps.

Use these as starting points for projects; copy into your codebase and customize.
