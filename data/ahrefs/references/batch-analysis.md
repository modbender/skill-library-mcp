# Batch Analysis API Reference

Process multiple domains, URLs, or keywords in a single API request for efficient bulk analysis.

## Base URL
```
https://api.ahrefs.com/v3/
```

## Benefits of Batch Processing

1. **Cost Efficient**: Process up to 100 targets for the cost of one request
2. **Time Saving**: Get all results in one call instead of 100 separate calls
3. **Rate Limit Friendly**: One request counts as one toward rate limits
4. **Simplified Logic**: Less code complexity for bulk operations

---

## Batch Domain Metrics

**Endpoint**: `POST /site-explorer/batch/metrics`

Get metrics for multiple domains at once.

**Parameters** (JSON body):
- `targets` (required): Array of domains (max 100)
- `date` (required): Date in YYYY-MM-DD format
- `select` (optional): Comma-separated fields to return

**Example**:
```bash
curl -X POST "https://api.ahrefs.com/v3/site-explorer/batch/metrics" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "targets": ["example.com", "competitor1.com", "competitor2.com"],
    "date": "2026-02-18",
    "select": "org_keywords,org_traffic,domain_rating"
  }'
```

**Response**:
```json
{
  "results": [
    {
      "target": "example.com",
      "metrics": {
        "org_keywords": 6926,
        "org_traffic": 38707,
        "domain_rating": 65
      }
    },
    {
      "target": "competitor1.com",
      "metrics": {
        "org_keywords": 14573,
        "org_traffic": 67088,
        "domain_rating": 72
      }
    }
  ]
}
```

---

## Batch Backlinks Stats

**Endpoint**: `POST /site-explorer/batch/backlinks-stats`

Get backlink statistics for multiple domains.

**Parameters** (JSON body):
- `targets` (required): Array of domains (max 100)
- `date` (required): Date in YYYY-MM-DD format

**Example**:
```bash
curl -X POST "https://api.ahrefs.com/v3/site-explorer/batch/backlinks-stats" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "targets": ["example.com", "competitor1.com", "competitor2.com"],
    "date": "2026-02-18"
  }'
```

**Response**:
```json
{
  "results": [
    {
      "target": "example.com",
      "backlinks_stats": {
        "live": 4545,
        "live_refdomains": 718
      }
    }
  ]
}
```

---

## Batch Domain Rating

**Endpoint**: `POST /site-explorer/batch/domain-rating`

Get Domain Rating for multiple domains.

**Parameters** (JSON body):
- `targets` (required): Array of domains (max 100)
- `date` (required): Date in YYYY-MM-DD format

**Example**:
```bash
curl -X POST "https://api.ahrefs.com/v3/site-explorer/batch/domain-rating" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "targets": ["example.com", "competitor1.com", "competitor2.com"],
    "date": "2026-02-18"
  }'
```

---

## Batch Keyword Metrics

**Endpoint**: `POST /keywords-explorer/batch/overview`

Get keyword metrics for multiple keywords.

**Parameters** (JSON body):
- `keywords` (required): Array of keywords (max 100)
- `country` (required): 2-letter country code

**Example**:
```bash
curl -X POST "https://api.ahrefs.com/v3/keywords-explorer/batch/overview" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["seo tools", "keyword research", "backlink analysis", "competitor analysis"],
    "country": "us"
  }'
```

**Response**:
```json
{
  "results": [
    {
      "keyword": "seo tools",
      "volume": 14000,
      "keyword_difficulty": 75,
      "cpc": 25.50,
      "traffic_potential": 18500
    },
    {
      "keyword": "keyword research",
      "volume": 8100,
      "keyword_difficulty": 68,
      "cpc": 18.20,
      "traffic_potential": 11200
    }
  ]
}
```

---

## Batch URL Metrics

**Endpoint**: `POST /site-explorer/batch/url-metrics`

Get metrics for specific URLs (not just domains).

**Parameters** (JSON body):
- `urls` (required): Array of full URLs (max 100)
- `date` (required): Date in YYYY-MM-DD format

**Example**:
```bash
curl -X POST "https://api.ahrefs.com/v3/site-explorer/batch/url-metrics" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "urls": [
      "https://example.com/page1",
      "https://example.com/page2",
      "https://competitor.com/article"
    ],
    "date": "2026-02-18"
  }'
```

**Response**:
```json
{
  "results": [
    {
      "url": "https://example.com/page1",
      "url_rating": 42,
      "backlinks": 125,
      "referring_domains": 45,
      "keywords": 87,
      "traffic": 1250
    }
  ]
}
```

---

## Best Practices

### Optimize Batch Requests

1. **Group by Type**: Process domains separately from URLs
2. **Consistent Dates**: Use same date for comparable results
3. **Limit Fields**: Use `select` to return only needed data
4. **Handle Errors**: Check individual results for errors
5. **Batch Size**: Use full 100-target limit when possible

### Error Handling

Individual targets can fail without failing the entire batch:

```json
{
  "results": [
    {
      "target": "example.com",
      "metrics": {...}
    },
    {
      "target": "invalid-domain",
      "error": "Domain not found in index"
    }
  ]
}
```

Always check for `error` field in each result.

---

## Cost Analysis

**Single Requests vs Batch**:
- 100 individual requests = 5000 API units (50 each)
- 1 batch request = 50-500 API units (depends on targets)

**Typical Savings**: 90-95% cost reduction

---

## Common Use Cases

### Competitor Analysis Dashboard
```javascript
// Analyze 50 competitors at once
const competitors = [
  'competitor1.com',
  'competitor2.com',
  // ... up to 100
];

fetch('/site-explorer/batch/metrics', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    targets: competitors,
    date: '2026-02-18',
    select: 'org_keywords,org_traffic,domain_rating'
  })
});
```

### Keyword Portfolio Analysis
```javascript
// Analyze all target keywords
const keywords = readKeywordsFromFile(); // Up to 100

fetch('/keywords-explorer/batch/overview', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    keywords: keywords,
    country: 'us'
  })
});
```

### Content Audit
```javascript
// Analyze all important pages
const urls = [
  'https://example.com/page1',
  'https://example.com/page2',
  // ... all key pages
];

fetch('/site-explorer/batch/url-metrics', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    urls: urls,
    date: '2026-02-18'
  })
});
```

---

## PowerShell Example

```powershell
$token = $env:AHREFS_API_TOKEN
$date = Get-Date -Format "yyyy-MM-dd"

$body = @{
    targets = @('example.com', 'competitor1.com', 'competitor2.com')
    date = $date
    select = 'org_keywords,org_traffic,domain_rating'
} | ConvertTo-Json

$headers = @{
    'Authorization' = "Bearer $token"
    'Content-Type' = 'application/json'
}

$response = Invoke-RestMethod -Uri "https://api.ahrefs.com/v3/site-explorer/batch/metrics" `
    -Method Post `
    -Headers $headers `
    -Body $body

# Process results
$response.results | ForEach-Object {
    Write-Host "$($_.target): DR $($_.metrics.domain_rating), Keywords $($_.metrics.org_keywords)"
}
```

---

## Limitations

- Maximum 100 targets per batch request
- All targets in a batch must be same type (domains OR URLs OR keywords)
- Batch requests count as one toward rate limits
- Individual target failures don't fail entire batch
- Response time increases with batch size (typically 2-10 seconds for 100 targets)
