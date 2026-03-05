# Structured Data (Schema Markup)

## Basics
- JSON-LD format preferred — script tag in head, cleanest implementation
- Test with Rich Results Test — not all schema triggers rich results
- Test with Schema Validator (schema.org) — catches syntax errors
- Required vs recommended properties — missing required = invalid
- One schema type per thing — don't mark same content as Article AND BlogPosting

## Common Schema Types

### Article / BlogPosting
```json
{
  "@type": "Article",
  "headline": "...",
  "author": {"@type": "Person", "name": "..."},
  "datePublished": "2025-01-15",
  "dateModified": "2025-01-20",
  "image": "..."
}
```
- `datePublished` required — omitting it loses rich result eligibility
- `dateModified` shows in search when different from published
- `image` recommended for better visual in search results

### LocalBusiness
```json
{
  "@type": "LocalBusiness",
  "name": "...",
  "address": {"@type": "PostalAddress", ...},
  "telephone": "...",
  "openingHoursSpecification": [...]
}
```
- Use specific subtype: `Restaurant`, `Dentist`, `LegalService`
- `geo` coordinates help Google verify location
- `priceRange` shows in Knowledge Panel

### FAQ
```json
{
  "@type": "FAQPage",
  "mainEntity": [
    {"@type": "Question", "name": "...", "acceptedAnswer": {...}}
  ]
}
```
- FAQ schema shows expandable Q&A in search results — HUGE CTR boost
- Content must be visible on page — hidden FAQ = spam
- Max ~10 questions typically shown

### Product
```json
{
  "@type": "Product",
  "name": "...",
  "offers": {"@type": "Offer", "price": "...", "priceCurrency": "USD"},
  "aggregateRating": {...}
}
```
- `offers` required for price in search results
- `aggregateRating` shows stars — needs actual review data
- `availability` (InStock, OutOfStock) shows availability badge

### HowTo
- Step-by-step instructions with images
- Can show as rich result with step previews
- Each step needs `text`, optionally `image`

### Review
- Individual review with `reviewRating`
- Self-serving reviews (reviewing own business) = spam

## Traps
- Marking invisible content — schema must match visible page content
- Fake reviews/ratings — Google detects and penalizes
- Schema for content that doesn't exist — "Product" on info page
- Mixing incompatible types — Article + Product on same page
- Not updating `dateModified` when content changes
