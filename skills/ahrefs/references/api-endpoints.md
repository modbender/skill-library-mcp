# Ahrefs API Endpoints Reference

Comprehensive reference for Ahrefs API v3 endpoints.

## Base URL
```
https://api.ahrefs.com/v3/site-explorer/
```

## Authentication
All requests require Bearer token authentication:
```
Authorization: Bearer {AHREFS_API_TOKEN}
```

**Important:** Do NOT use `AHREFS_MCP_TOKEN` - use `AHREFS_API_TOKEN`.

## Required Parameters
ALL endpoints require:
- `date`: Current date in `YYYY-MM-DD` format
- `target`: Domain (e.g., `example.com`)

---

## Site Explorer API

### Backlinks Stats
**Endpoint**: `GET /site-explorer/backlinks-stats`

Get backlinks and referring domains counts.

**Parameters**:
- `date` (required): Date in `YYYY-MM-DD` format
- `target` (required): Domain (e.g., `example.com`)

**Example**:
```bash
curl "https://api.ahrefs.com/v3/site-explorer/backlinks-stats?date=2026-02-18&target=example.com" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "metrics": {
    "live": 4545,
    "all_time": 25318,
    "live_refdomains": 718,
    "all_time_refdomains": 3272
  }
}
```

---

### Metrics (Organic Keywords & Traffic)
**Endpoint**: `GET /site-explorer/metrics`

Get organic search metrics including keywords and traffic.

**Parameters**:
- `date` (required): Date in `YYYY-MM-DD` format
- `target` (required): Domain (e.g., `example.com`)

**Example**:
```bash
curl "https://api.ahrefs.com/v3/site-explorer/metrics?date=2026-02-18&target=example.com" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "metrics": {
    "org_keywords": 6925,
    "paid_keywords": 907,
    "org_keywords_1_3": 1560,
    "org_traffic": 38702,
    "org_cost": 2372016,
    "paid_traffic": 3392,
    "paid_cost": 178172,
    "paid_pages": 493
  }
}
```

---

### Domain Rating
**Endpoint**: `GET /site-explorer/domain-rating`

Get domain rating and Ahrefs rank.

**Parameters**:
- `date` (required): Date in `YYYY-MM-DD` format
- `target` (required): Domain (e.g., `example.com`)

**Example**:
```bash
curl "https://api.ahrefs.com/v3/site-explorer/domain-rating?date=2026-02-18&target=example.com" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "domain_rating": {
    "domain_rating": 43.0,
    "ahrefs_rank": 1189155
  }
}
```

---

### Top Pages
**Endpoint**: `GET /site-explorer/top-pages`

Get top-performing pages by organic traffic.

**Parameters**:
- `date` (required): Date in `YYYY-MM-DD` format
- `target` (required): Domain (e.g., `example.com`)
- `limit` (optional): Number of results (default: 50)
- `select` (optional): Comma-separated fields to return
- `order_by` (optional): e.g., `sum_traffic:desc`

**Available select fields**:
- `url`: Page URL
- `sum_traffic`: Estimated traffic
- `top_keyword`: Primary ranking keyword
- `top_keyword_volume`: Search volume of primary keyword
- `top_keyword_best_position`: Best ranking position
- `ur`: URL Rating
- `referring_domains`: Number of referring domains
- `keywords`: Total ranking keywords

**Example**:
```bash
curl "https://api.ahrefs.com/v3/site-explorer/top-pages?date=2026-02-18&target=example.com&limit=10&select=url,sum_traffic,top_keyword&order_by=sum_traffic:desc" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "pages": [
    {
      "url": "https://example.com/page",
      "sum_traffic": 7337,
      "top_keyword": "example keyword"
    }
  ]
}
```

---

## Common Query Parameters

### Date (REQUIRED)
ALL endpoints require the `date` parameter in `YYYY-MM-DD` format.
```bash
DATE=$(date +%Y-%m-%d)  # Unix/Linux/Mac
$DATE = (Get-Date -Format "yyyy-MM-dd")  # PowerShell
```

### Target (REQUIRED)
The domain or URL to analyze. Format: `example.com` (without protocol)

### Select (Optional)
Comma-separated list of fields to return. Available fields vary by endpoint.

### Limit (Optional)
Number of results to return (varies by endpoint, typically 1-1000).

### Order By (Optional)
Sort results. Format: `field:asc` or `field:desc`

---

## Rate Limits

- API requests are rate-limited per subscription tier
- Check response headers:
  - `X-RateLimit-Limit`: Max requests per period
  - `X-RateLimit-Remaining`: Remaining requests
  - `X-RateLimit-Reset`: Reset timestamp

### Handling Rate Limits
```bash
# Check rate limit headers
curl -I https://api.ahrefs.com/v3/site-explorer/domain-overview?target=example.com \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

When rate limited (HTTP 429), implement exponential backoff.

---

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Invalid token |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Domain not in index |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error |
| 503 | Service Unavailable |

---

## Best Practices

1. **Batch Requests**: Group related queries when possible
2. **Cache Aggressively**: SEO data doesn't change minute-to-minute
3. **Use Appropriate Mode**: Choose between `exact`, `domain`, `subdomains` wisely
4. **Pagination**: Always use `limit` and `offset` for large datasets
5. **Error Recovery**: Implement retry logic with exponential backoff

---

## Example Workflows

### Complete Domain Audit
```bash
DATE=$(date +%Y-%m-%d)
TOKEN="your-api-token"
DOMAIN="example.com"

# 1. Backlinks & Referring Domains
curl "https://api.ahrefs.com/v3/site-explorer/backlinks-stats?date=$DATE&target=$DOMAIN" \
  -H "Authorization: Bearer $TOKEN"

# 2. Domain Rating
curl "https://api.ahrefs.com/v3/site-explorer/domain-rating?date=$DATE&target=$DOMAIN" \
  -H "Authorization: Bearer $TOKEN"

# 3. Organic Keywords & Traffic
curl "https://api.ahrefs.com/v3/site-explorer/metrics?date=$DATE&target=$DOMAIN" \
  -H "Authorization: Bearer $TOKEN"

# 4. Top Pages by Traffic
curl "https://api.ahrefs.com/v3/site-explorer/top-pages?date=$DATE&target=$DOMAIN&limit=50&select=url,sum_traffic,keywords&order_by=sum_traffic:desc" \
  -H "Authorization: Bearer $TOKEN"
```

### PowerShell Domain Comparison
```powershell
$today = (Get-Date -Format "yyyy-MM-dd")
$token = $env:AHREFS_API_TOKEN
$headers = @{ "Authorization" = "Bearer $token" }

$domains = @("site1.com", "site2.com")

foreach ($domain in $domains) {
    Write-Output "`n=== $domain ==="
    
    # Get all metrics
    $backlinks = Invoke-RestMethod -Uri "https://api.ahrefs.com/v3/site-explorer/backlinks-stats?date=$today&target=$domain" -Headers $headers
    $metrics = Invoke-RestMethod -Uri "https://api.ahrefs.com/v3/site-explorer/metrics?date=$today&target=$domain" -Headers $headers
    $rating = Invoke-RestMethod -Uri "https://api.ahrefs.com/v3/site-explorer/domain-rating?date=$today&target=$domain" -Headers $headers
    
    Write-Output "Backlinks: $($backlinks.metrics.live)"
    Write-Output "Referring Domains: $($backlinks.metrics.live_refdomains)"
    Write-Output "Domain Rating: $($rating.domain_rating.domain_rating)"
    Write-Output "Organic Keywords: $($metrics.metrics.org_keywords)"
    Write-Output "Organic Traffic: $($metrics.metrics.org_traffic)"
}
```
