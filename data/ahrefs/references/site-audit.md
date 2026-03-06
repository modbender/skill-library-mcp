# Site Audit API Reference

Identify and monitor technical SEO issues on your website.

**⚠️ Important**: Site Audit requires pre-configured projects in the Ahrefs web interface. You must set up audit projects before using these API endpoints.

## Base URL
```
https://api.ahrefs.com/v3/site-audit/
```

## Setup Requirements

1. Log in to https://app.ahrefs.com
2. Navigate to Site Audit
3. Create a project and configure crawl settings
4. Run initial audit crawl
5. Note your `project_id`

---

## Get Project Overview

**Endpoint**: `GET /site-audit/project`

Get overall site health metrics.

**Parameters**:
- `project_id` (required): Your Site Audit project ID

**Example**:
```bash
curl "https://api.ahrefs.com/v3/site-audit/project?project_id=12345" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response Fields**:
- `project_id`: Project identifier
- `domain`: Audited domain
- `health_score`: Overall health (0-100)
- `total_pages`: Pages crawled
- `total_issues`: Total issues found
- `errors`: Critical issues count
- `warnings`: Warning issues count
- `notices`: Notice-level issues count
- `last_crawl`: Last crawl timestamp
- `crawl_duration`: Time taken for last crawl

---

## Get All Issues

**Endpoint**: `GET /site-audit/issues`

List all detected issues grouped by type.

**Parameters**:
- `project_id` (required): Project ID
- `severity` (optional): Filter by severity (`error`, `warning`, `notice`)
- `category` (optional): Filter by category (see categories below)
- `limit` (optional): Max results

**Example**:
```bash
curl "https://api.ahrefs.com/v3/site-audit/issues?project_id=12345&severity=error&limit=50" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "issues": [
    {
      "issue_type": "broken_links",
      "severity": "error",
      "affected_pages": 15,
      "description": "Pages with broken internal links",
      "how_to_fix": "Update or remove broken links",
      "pages": [
        {
          "url": "https://example.com/page1",
          "status_code": 404
        }
      ]
    }
  ]
}
```

---

## Issue Categories

- **Content**: Duplicate content, thin content, missing meta tags
- **Links**: Broken links, redirect chains, orphaned pages
- **Performance**: Slow pages, large images, render-blocking resources
- **Mobile**: Mobile usability, viewport issues
- **Indexability**: Robots.txt issues, noindex pages, canonicalization
- **Security**: Mixed content, HTTPS issues
- **Structured Data**: Schema markup errors

---

## Get Internal Links

**Endpoint**: `GET /site-audit/internal-links`

Analyze internal link structure.

**Parameters**:
- `project_id` (required): Project ID
- `url` (optional): Specific page URL to analyze
- `limit` (optional): Max results

**Example**:
```bash
curl "https://api.ahrefs.com/v3/site-audit/internal-links?project_id=12345&url=https://example.com/page1" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "url": "https://example.com/page1",
  "internal_links_in": 25,
  "internal_links_out": 42,
  "link_equity": 8.5,
  "links_from": [
    {
      "from_url": "https://example.com/homepage",
      "anchor_text": "Important Page",
      "link_type": "dofollow"
    }
  ]
}
```

---

## Get Page Performance

**Endpoint**: `GET /site-audit/page-performance`

Get page speed and performance metrics.

**Parameters**:
- `project_id` (required): Project ID
- `limit` (optional): Max results
- `order_by` (optional): Sort by field (e.g., `load_time:desc`)

**Example**:
```bash
curl "https://api.ahrefs.com/v3/site-audit/page-performance?project_id=12345&limit=20&order_by=load_time:desc" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "pages": [
    {
      "url": "https://example.com/slow-page",
      "load_time": 4.5,
      "page_size": 2.8,
      "requests": 87,
      "performance_score": 45,
      "largest_contentful_paint": 3.2,
      "first_input_delay": 0.3
    }
  ]
}
```

---

## Get Crawl Statistics

**Endpoint**: `GET /site-audit/crawl-stats`

Get detailed crawl statistics.

**Parameters**:
- `project_id` (required): Project ID

**Example**:
```bash
curl "https://api.ahrefs.com/v3/site-audit/crawl-stats?project_id=12345" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "crawl_stats": {
    "pages_crawled": 1250,
    "pages_with_issues": 342,
    "avg_response_time": 0.8,
    "status_codes": {
      "200": 1150,
      "301": 45,
      "302": 12,
      "404": 25,
      "500": 18
    },
    "content_types": {
      "text/html": 1200,
      "application/pdf": 30,
      "image/jpeg": 20
    }
  }
}
```

---

## Get Duplicate Content

**Endpoint**: `GET /site-audit/duplicate-content`

Find pages with duplicate or similar content.

**Parameters**:
- `project_id` (required): Project ID
- `similarity_threshold` (optional): Minimum similarity percentage (default: 85)

**Example**:
```bash
curl "https://api.ahrefs.com/v3/site-audit/duplicate-content?project_id=12345" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "duplicate_groups": [
    {
      "similarity": 95,
      "pages": [
        "https://example.com/page1",
        "https://example.com/page2-copy"
      ]
    }
  ]
}
```

---

## Get Orphaned Pages

**Endpoint**: `GET /site-audit/orphaned-pages`

Find pages with no internal links pointing to them.

**Parameters**:
- `project_id` (required): Project ID

**Example**:
```bash
curl "https://api.ahrefs.com/v3/site-audit/orphaned-pages?project_id=12345" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

---

## Best Practices

1. **Regular Audits**: Run monthly audits to catch new issues
2. **Prioritize Errors**: Fix critical errors before warnings
3. **Track Progress**: Monitor health score improvements over time
4. **Internal Links**: Ensure important pages have adequate internal links
5. **Performance**: Address slow pages affecting user experience
6. **Mobile**: Test and fix mobile-specific issues
7. **Content Quality**: Address thin and duplicate content issues

---

## Cost Optimization

- Site Audit API requests consume API units
- Limit results with `limit` parameter
- Cache audit data between crawls
- Focus queries on specific issue types
- Use severity filters to reduce data returned

---

## Common Issue Types

**Critical (Errors)**:
- Broken internal links (404s)
- Server errors (500s)
- Missing title tags
- Duplicate title tags
- Redirect chains
- Orphaned pages

**Warnings**:
- Slow page load times
- Large page sizes
- Missing meta descriptions
- Multiple h1 tags
- Shallow content

**Notices**:
- Missing alt text
- Underscores in URLs
- Long URLs
- HTTPS mixed content warnings

---

## Limitations

- Projects must be pre-configured in Ahrefs web interface
- Crawl frequency affects data freshness
- Maximum pages crawled varies by plan
- Some issues require manual verification
