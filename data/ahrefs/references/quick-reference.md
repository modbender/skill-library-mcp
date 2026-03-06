# Ahrefs API Quick Reference

## Authentication
```bash
export AHREFS_API_TOKEN="your-token-here"
```

⚠️ **Important:** Use `AHREFS_API_TOKEN`, NOT `AHREFS_MCP_TOKEN`

## Base URL
```
https://api.ahrefs.com/v3/site-explorer/
```

## Required Parameters (ALL Endpoints)
- `date`: Current date in `YYYY-MM-DD` format
- `target`: Domain (e.g., `example.com`)

---

## Working Endpoints

### 1. Backlinks Stats
**Get:** Total backlinks and referring domains

```bash
curl "https://api.ahrefs.com/v3/site-explorer/backlinks-stats?date=2026-02-18&target=example.com" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Returns:**
- `live`: Current live backlinks
- `all_time`: Historical backlinks
- `live_refdomains`: Current referring domains
- `all_time_refdomains`: Historical referring domains

---

### 2. Metrics
**Get:** Organic keywords, traffic, and cost estimates

```bash
curl "https://api.ahrefs.com/v3/site-explorer/metrics?date=2026-02-18&target=example.com" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Returns:**
- `org_keywords`: Total organic keywords
- `org_traffic`: Estimated monthly organic traffic
- `org_cost`: Estimated traffic value
- `paid_keywords`, `paid_traffic`, `paid_cost`: Paid search metrics

---

### 3. Domain Rating
**Get:** Domain authority score and Ahrefs rank

```bash
curl "https://api.ahrefs.com/v3/site-explorer/domain-rating?date=2026-02-18&target=example.com" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Returns:**
- `domain_rating`: Score 0-100
- `ahrefs_rank`: Global rank position

---

### 4. Top Pages
**Get:** Best-performing pages by traffic

```bash
curl "https://api.ahrefs.com/v3/site-explorer/top-pages?date=2026-02-18&target=example.com&limit=10&select=url,sum_traffic,keywords&order_by=sum_traffic:desc" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Common select fields:**
- `url`: Page URL
- `sum_traffic`: Estimated traffic
- `top_keyword`: Primary keyword
- `keywords`: Total ranking keywords
- `referring_domains`: Backlink sources
- `ur`: URL Rating

---

## PowerShell Example

```powershell
$today = (Get-Date -Format "yyyy-MM-dd")
$token = $env:AHREFS_API_TOKEN
$headers = @{ "Authorization" = "Bearer $token" }
$domain = "example.com"

# Get all key metrics
$backlinks = Invoke-RestMethod -Uri "https://api.ahrefs.com/v3/site-explorer/backlinks-stats?date=$today&target=$domain" -Headers $headers
$metrics = Invoke-RestMethod -Uri "https://api.ahrefs.com/v3/site-explorer/metrics?date=$today&target=$domain" -Headers $headers
$rating = Invoke-RestMethod -Uri "https://api.ahrefs.com/v3/site-explorer/domain-rating?date=$today&target=$domain" -Headers $headers

Write-Output "Backlinks: $($backlinks.metrics.live)"
Write-Output "Referring Domains: $($backlinks.metrics.live_refdomains)"
Write-Output "Domain Rating: $($rating.domain_rating.domain_rating)"
Write-Output "Organic Keywords: $($metrics.metrics.org_keywords)"
Write-Output "Organic Traffic: $($metrics.metrics.org_traffic)"
```

---

## Common Issues

### 404 Errors
- Endpoint path is wrong (missing `date` parameter?)
- Domain format incorrect (use `example.com` not `https://example.com`)

### 400 Bad Request
- Missing required `date` parameter
- Invalid `target` format
- Invalid `select` field names

### 401 Unauthorized
- Wrong API token
- Using `AHREFS_MCP_TOKEN` instead of `AHREFS_API_TOKEN`

### 429 Rate Limited
- Too many requests
- Implement exponential backoff
- Cache responses where appropriate

---

## Testing Script

Save as `test-ahrefs.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y-%m-%d)
TOKEN="$AHREFS_API_TOKEN"
DOMAIN="$1"

if [ -z "$DOMAIN" ]; then
  echo "Usage: $0 example.com"
  exit 1
fi

echo "Testing Ahrefs API for $DOMAIN..."

echo -e "\n1. Backlinks Stats:"
curl -s "https://api.ahrefs.com/v3/site-explorer/backlinks-stats?date=$DATE&target=$DOMAIN" \
  -H "Authorization: Bearer $TOKEN" | jq '.metrics'

echo -e "\n2. Domain Rating:"
curl -s "https://api.ahrefs.com/v3/site-explorer/domain-rating?date=$DATE&target=$DOMAIN" \
  -H "Authorization: Bearer $TOKEN" | jq '.domain_rating'

echo -e "\n3. Organic Metrics:"
curl -s "https://api.ahrefs.com/v3/site-explorer/metrics?date=$DATE&target=$DOMAIN" \
  -H "Authorization: Bearer $TOKEN" | jq '.metrics | {org_keywords, org_traffic}'
```

Make executable: `chmod +x test-ahrefs.sh`
Run: `./test-ahrefs.sh example.com`
