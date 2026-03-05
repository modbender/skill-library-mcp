---
name: ahrefs-mcp
description: >
  Access Ahrefs SEO data via the Ahrefs API for comprehensive SEO analysis, keyword research, backlink analysis, site audits, and competitive intelligence. Use when users mention: (1) SEO-related queries about websites, domains, or URLs, (2) Keyword research, rankings, or search volume data, (3) Backlink analysis or link profiles, (4) Domain metrics (DR, UR, traffic), (5) Competitor analysis or site comparison, (6) Rank tracking or SERP analysis, (7) Content gap analysis, (8) Site Explorer data requests. When uncertain if a query is SEO-related, ask if Ahrefs should be used.
---

# Ahrefs API

Access real-time Ahrefs SEO data directly through the Ahrefs API to analyze websites, research keywords, track rankings, and make data-driven SEO decisions.

## First-Time Setup

If this is your first time using the Ahrefs API, read [references/setup.md](references/setup.md) for complete setup instructions. You'll need:
- An Ahrefs account (Enterprise plan for full API access, or Lite+ for limited free test queries)
- An API key from your Ahrefs workspace

After setup, return here for usage guidance.

## Core Capabilities

Ahrefs API provides access to:

1. **Site Explorer** - Domain metrics, backlinks, organic traffic, referring domains
2. **Keywords Explorer** - Search volume, keyword difficulty, SERP analysis, related keywords
3. **Rank Tracker** - Position tracking, visibility metrics, competitor rankings (requires pre-configured projects)
4. **Site Audit** - Technical SEO issues, crawl data, site health (requires pre-configured projects)
5. **SERP Overview** - Top 100 SERP results for any keyword
6. **Batch Analysis** - Process up to 100 targets per request
7. **Brand Radar** - Brand performance stats

For detailed capability reference, see [references/capabilities.md](references/capabilities.md).

## Authentication

All API requests require an API key passed via the `Authorization` header:
```bash
Authorization: Bearer YOUR_API_KEY
```

Store your API key securely. Consider using environment variables:
```bash
export AHREFS_API_KEY="your-api-key-here"
```

## Usage Workflow

### 1. Understand the Request

Identify what SEO data is needed:
- **Domain/URL analysis** → Site Explorer endpoints
- **Keyword data** → Keywords Explorer endpoints
- **Position tracking** → Rank Tracker endpoints (requires project)
- **Technical SEO** → Site Audit endpoints (requires project)
- **SERP data** → SERP Overview endpoints

### 2. Make API Requests

Use `curl` or similar tools to call the Ahrefs API. Base URL: `https://api.ahrefs.com/v3`

**Example - Get domain overview:**
```bash
curl -X GET "https://api.ahrefs.com/v3/site-explorer/domain-overview?target=example.com" \
  -H "Authorization: Bearer $AHREFS_API_KEY"
```

**Example - Keyword metrics:**
```bash
curl -X GET "https://api.ahrefs.com/v3/keywords-explorer/overview?keyword=seo+tools&country=us" \
  -H "Authorization: Bearer $AHREFS_API_KEY"
```

### 3. Process and Present Results

- Parse JSON responses
- Extract relevant metrics
- Present data in clear, actionable formats
- Highlight key insights and opportunities
- Suggest next steps based on findings

## Common Workflows

### Keyword Research + Cross-Reference

1. User provides keyword list
2. Make batch API calls to Keywords Explorer
3. Parse and consolidate metrics (volume, difficulty, CPC)
4. Present analysis with prioritization recommendations

See [references/workflows.md](references/workflows.md) for detailed workflow patterns with example API calls.

### Competitive Analysis

1. Identify target domain and competitors
2. Call Site Explorer for each domain
3. Compare metrics (DR, organic traffic, referring domains)
4. Analyze top organic keywords
5. Identify content gaps
6. Provide actionable recommendations

### Site Audit Review

**Note:** Requires pre-configured Site Audit project in Ahrefs web interface.

1. Call Site Audit API for project data
2. Identify critical issues by severity
3. Prioritize fixes by impact
4. Provide technical recommendations

## API Limits & Best Practices

### Rate Limiting
- **60 requests per minute** by default
- API returns HTTP 429 if limit exceeded
- Implement exponential backoff for retries

### API Unit Consumption
- Each request consumes API units from your monthly allowance
- Cost depends on the number of rows returned (minimum 50 units per request)
- Track usage in **Account settings → Limits and usage**
- Enterprise plans include units; additional units can be purchased

### Optimization Tips
- **Batch requests** when possible (up to 100 targets)
- **Limit result rows** using `limit` parameter
- **Select specific columns** with `select` parameter to reduce costs
- **Cache results** when appropriate
- **Use date ranges** to limit historical data

### Plan-Specific Access
- **Enterprise**: Full API access
- **Lite/Standard/Advanced**: Limited free test queries (check your plan for specifics)

## Error Handling

Common HTTP status codes:
- `200 OK` - Success
- `400 Bad Request` - Invalid parameters
- `401 Unauthorized` - Invalid or missing API key
- `403 Forbidden` - Insufficient permissions or plan limits
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Ahrefs server issue

Always check response status and handle errors gracefully.

## When API Key is Missing

If the API key is not configured:
1. Provide setup instructions from [references/setup.md](references/setup.md)
2. Guide through API key generation in Ahrefs Account settings
3. Explain how to securely store the key (environment variables recommended)
4. Test the connection with a simple API call

## Resources

- **API Documentation**: https://docs.ahrefs.com/docs/api/reference/introduction
- **API Key Management**: https://app.ahrefs.com/account/api-keys
- **Pricing & Limits**: https://ahrefs.com/pricing
- **Limits & Usage Tracking**: https://app.ahrefs.com/account/limits-and-usage/web