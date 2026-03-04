# Google Rich Results Guidelines

Eligibility requirements for Google's enhanced search results.

## General Principles

- **No spam**: Structured data must accurately reflect page content
- **Original content**: Must be visible to users (not hidden or cloaked)
- **Not promotional**: Can't use structured data solely for marketing/ads
- **Accessible**: Content must be accessible to users (not behind login/paywall unless site-wide)

## Eligibility by Type

### ✅ Eligible (Common)

- Article (NewsArticle, BlogPosting) – must have substantive text content
- Book (with reviews, offers)
- Course (with courseDescription, provider, etc.)
- Dataset – with proper licensing and description
- Event – with clear dates, location, and tickets if sold
- FAQPage – only for pages with primarily FAQ content
- HowTo – clear steps, supplies, tools
- JobPosting – must comply with job posting policies
- LocalBusiness – with address, phone, opening hours
- Organization – with logo, social links
- Person – for public figures
- Product – with name, description, offers
- Recipe – with ingredients and instructions
- VideoObject – with video embedded on page
- Review – with author, date, rating

### ⚠️ Not Eligible for Rich Results

- Generic `WebPage` only – must add specific subtype
- Many `Thing` subclasses unless explicitly listed above
- Schema used for decoration only (no visible content correlation)

## Content Requirements

### Article / BlogPosting

- Must have substantial text content (not a list of links)
- Author must be a Person or Organization object (not string)
- datePublished and dateModified should be accurate
- `headline` should match page `<title>` or `<h1>`
- Images must be visible on page

### Product

- Must represent a specific product (not category pages)
- `offers` must include `price`, `priceCurrency`, `availability`
- `aggregateRating` only if at least 1 review exists and visible
- `brand` recommended but not strictly required

### Event

- Must have `name`, `startDate`, and either `location` or `onlineEvent` flag
- For in-person events, provide full address
- `eventStatus` recommended (EventScheduled, EventCancelled, etc.)
- Past events should be marked with `eventStatus: https://schema.org/EventEnded`

### Recipe

- Must have `recipeIngredient` and `recipeInstructions`
- `nutrition` optional but recommended
- `prepTime`, `cookTime` help qualify for rich results
- Videos/images should be on-page

### FAQPage

- Page content should be primarily FAQ; don't add to unrelated pages
- Each question must have a full answer (not one-word)
- Don't use for marketing/CTAs; purely informational
- Duplicate FAQs across site will be devalued

### HowTo

- Must have at least 2-3 `step` entries with `text` or `itemListElement`
- `totalTime` recommended
- Each step should be actionable and visible on page

## Testing & Validation

1. **Rich Results Test**: https://search.google.com/test/rich-results
   - Enter URL or paste JSON-LD
   - Fix any errors or warnings (some warnings are okay)

2. **Schema.org Validator**: https://validator.schema.org/
   - Checks syntax and required fields
   - Use for debugging

3. **Manual inspection**: In Google Search Console → Enhancements → see if eligible pages are detected

## Common Pitfalls

- Missing required fields → won't qualify
- Wrong `@type` → may not be eligible (e.g., use `VideoObject`, not generic `MediaObject`)
- Hidden content → script must match visible page content
- Multiple conflicting schemas on same page → Google picks one; ensure consistency
- Using `sameAs` for non-official profiles → only official brand/person profiles
- Price not visible on page → must match what user sees

## Updating Schema

- When content changes (price, dates, availability), update JSON-LD immediately
- Use server-side rendering for dynamic values; avoid client-side only if possible
- For SPA frameworks (React/Next.js), ensure JSON-LD is in initial HTML (not loaded after)

## Monitoring

- Search Console → Enhancements → check for errors/improvements
- Rich results can take days-weeks to appear after fixing issues
- Use `site:` search operator to see if rich snippets appear in SERP

---

For complete guidelines, see Google's official documentation:
- [Overview](https://developers.google.com/search/docs/appearance/structured-data/intro-structured-data)
- [General guidelines](https://developers.google.com/search/docs/appearance/structured-data/guidelines)