# Google Rich Results Guidelines

## Eligible Schema Types

Google supports Rich Results for these schema types:

### Currently Supported
- Article
- Book
- Breadcrumb
- Carousel
- Course
- Dataset
- Employer Aggregate Rating
- Estimated Salary
- Event
- Fact Check
- FAQ
- Guidance (HowTo)
- Image License
- Job Posting
- Learning Video
- Local Business
- Logo
- Math Solvers
- Movie
- Education Q&A
- Practice Problems
- Product
- Q&A Page
- Recipe
- Review Snippet
- Sitelinks Searchbox
- Software App
- Speakable
- Subscription and Paywalled Content
- Video

## Guidelines by Type

### Article

**Requirements**:
- Headline (max 110 characters)
- Image (min 1200px width)
- Date published
- Author name

**Recommended**:
- Date modified
- Author URL
- Description

**Common Errors**:
- ❌ Image smaller than 1200px
- ❌ Missing author
- ❌ Date in wrong format

### Product

**Requirements**:
- Name
- Offers (price + currency) OR Review

**Recommended**:
- Brand
- SKU/MPN/GTIN
- Rating
- Availability
- Price valid until

**Common Errors**:
- ❌ Price includes currency symbol
- ❌ Multiple products without ItemList
- ❌ No offer or review

### FAQ

**Requirements**:
- Question text
- Answer text

**Guidelines**:
- ✅ Questions must be visible on page
- ✅ Answers must be complete
- ✅ No promotional content in answers
- ❌ No duplicate questions
- ❌ All questions must be answered

**Limitations**:
- Max 2 FAQs per page in search results
- Must be authoritative, factual content

### HowTo

**Requirements**:
- Total time OR estimated cost
- Step list with instructions

**Recommended**:
- Images for each step
- Tools and supplies
- Video

**Guidelines**:
- Steps must be visible on page
- Each step needs name and text
- Don't use for recipes (use Recipe schema)

## Technical Requirements

### JSON-LD Format

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  ...
}
</script>
```

Requirements:
- Must be in `<head>` or `<body>`
- Must be valid JSON
- Must use https://schema.org (not http)
- Each schema type on its own (no mixing Article and Product in one object)

### Testing Your Markup

1. **Rich Results Test**: https://search.google.com/test/rich-results
   - Shows if eligible for rich results
   - Identifies errors and warnings

2. **Schema Markup Validator**: https://validator.schema.org
   - Validates Schema.org syntax
   - Checks all fields

3. **URL Inspection Tool** (Google Search Console)
   - See live structured data
   - Check for indexing issues

### Common Validation Errors

| Error | Cause | Fix |
|-------|-------|-----|
| "Missing field" | Required field not present | Add the field |
| "Invalid value" | Wrong data type | Check format requirements |
| "Date format" | Date not ISO 8601 | Use YYYY-MM-DD format |
| "URL not accessible" | Schema URL returns error | Fix the URL |
| "Multiple items" | Multiple same-type schemas | Use @graph or separate pages |

## Content Guidelines

### Factual Accuracy
- Schema must match visible page content
- Don't markup content users can't see
- Don't use misleading titles/descriptions

### Prohibited Content
Google will not show rich results for:
- Adult content
- Violent content
- Dangerous/illegal products
- Misleading or deceptive practices
- Copyrighted material without rights

### Quality Standards
- Content must be original
- Must provide substantial value
- Not primarily promotional
- Not automatically generated (spam)

## Monitoring

### Google Search Console

Check **Enhancements** section for:
- Valid items count
- Errors and warnings
- Performance data

### Common Issues

**Issue**: "Crawled - currently not indexed"
- **Cause**: Page quality issues
- **Fix**: Improve content, wait for re-crawl

**Issue**: Valid items but no rich results
- **Cause**: Not eligible or not selected by algorithm
- **Fix**: No guaranteed fix; ensure compliance

**Issue**: Structured data errors spike
- **Cause**: Template change broke markup
- **Fix**: Validate templates, fix errors

## Best Practices

1. **Start with one type**: Don't try to implement everything at once
2. **Validate before deploying**: Use Google's test tools
3. **Monitor GSC**: Check for errors regularly
4. **Keep it current**: Update for schema changes
5. **Don't over-markup**: Only mark what's important
6. **Match visible content**: Schema = what's on the page

## Updates and Changes

Google frequently updates rich result requirements:
- Subscribe to Google Search Central blog
- Follow @googlesearchc on Twitter
- Check GSC for notifications

Recent notable changes:
- 2023: HowTo rich results limited on desktop
- 2023: Product rich results expanded
- 2024: Article guidelines updated