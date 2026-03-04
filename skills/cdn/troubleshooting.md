# CDN Troubleshooting

## "Why Isn't This Cached?"

### Diagnostic Steps
1. Check response headers:
```bash
curl -I https://example.com/asset.js
# Look for:
# - Cache-Control header
# - CF-Cache-Status (Cloudflare)
# - X-Cache (CloudFront)
# - Age header
```

2. Common cache status values:
| Status | Meaning |
|--------|---------|
| HIT | Served from cache |
| MISS | Fetched from origin, now cached |
| EXPIRED | Was cached, TTL expired |
| BYPASS | Cache intentionally skipped |
| DYNAMIC | Not eligible for caching |

3. Check for cache-busting factors:
- `Set-Cookie` in response
- `Cache-Control: no-store` or `private`
- `Vary` header with high-cardinality values
- Query strings (some CDNs ignore by default)

### Common Causes
| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Always MISS | `no-store` header | Fix origin Cache-Control |
| BYPASS | Set-Cookie present | Remove cookie from cacheable responses |
| Low hit ratio | Query string variations | Normalize cache key |
| DYNAMIC | Page rules excluding | Review CDN page rules |

## "Users See Stale Content"

### After Deploy
1. Verify invalidation completed:
```bash
# Cloudflare: check purge status
# CloudFront: check invalidation status
aws cloudfront get-invalidation --distribution-id XXX --id YYY
```

2. Check multiple edge locations:
```bash
# Use VPN or online tools to test from different regions
curl -H "Cache-Control: no-cache" https://example.com/app.js
```

3. Browser cache vs CDN cache:
- CDN purged but browser still has old version
- Solution: versioned filenames or `Clear-Site-Data` header

### Content Not Updating
1. Check `max-age` isn't too long for dynamic content
2. Verify origin is serving new content
3. Check for intermediate caches (browser, proxy)

## Origin Overload

### Symptoms
- High origin CPU/memory
- Slow response times
- 503/504 errors

### Causes
1. **Cache bypass attack** — Requests with unique query params
2. **Low cache hit ratio** — Too many cache misses
3. **Purge storm** — Full cache purge causing thundering herd

### Solutions
```
# Emergency: increase origin capacity or enable rate limiting

# Long-term:
# 1. Improve cache hit ratio
# 2. Use stale-while-revalidate
Cache-Control: max-age=60, stale-while-revalidate=3600, stale-if-error=86400

# 3. Origin shield (single point of origin contact)
# 4. Request coalescing (dedupe simultaneous requests)
```

## SSL/Certificate Issues

### Certificate Expired
```bash
# Check certificate
echo | openssl s_client -connect example.com:443 2>/dev/null | openssl x509 -noout -dates
```

### Mixed Content
- HTTPS page loading HTTP resources
- Fix: Update resource URLs to HTTPS or use protocol-relative URLs

### Certificate Mismatch
- CDN certificate doesn't match domain
- Check CDN certificate configuration and custom domains

## Performance Debugging

### High TTFB
1. Check origin response time
2. Check edge location (are users hitting far edges?)
3. Check SSL handshake time
4. Enable HTTP/2 or HTTP/3

### Slow in Specific Regions
```bash
# Test from multiple locations
# Use synthetic monitoring tools or:
curl -w "@timing.txt" -o /dev/null -s https://example.com

# timing.txt:
# time_namelookup: %{time_namelookup}\n
# time_connect: %{time_connect}\n
# time_appconnect: %{time_appconnect}\n
# time_starttransfer: %{time_starttransfer}\n
# time_total: %{time_total}\n
```

### Cache Miss Spikes
1. Check for cache purge events
2. Check for new content deployments
3. Look for attack patterns (unique query strings)

## Monitoring Checklist

| Metric | Alert Threshold |
|--------|-----------------|
| Cache hit ratio | < 85% |
| Origin 5xx rate | > 1% |
| Edge response time (p95) | > 500ms |
| Origin response time (p95) | > 1s |
| Bandwidth spike | > 2x normal |
| Certificate expiry | < 14 days |
