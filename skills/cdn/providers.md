# CDN Providers Comparison

## Major Providers

| Provider | Best For | CLI | Free Tier |
|----------|----------|-----|-----------|
| **Cloudflare** | General web, DDoS protection | `wrangler`, API | Generous free tier |
| **AWS CloudFront** | AWS ecosystem, S3 integration | `aws cloudfront` | 1TB/month free (first year) |
| **Bunny CDN** | Cost-effective, simple | API, dashboard | No free tier, but cheap |
| **Fastly** | Real-time purging, edge compute | `fastly` CLI | Limited free tier |
| **Vercel/Netlify** | JAMstack, static sites | Built-in | Generous for static |

## CLI Quick Reference

### Cloudflare
```bash
# Purge cache
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -d '{"purge_everything":true}'

# Purge specific URLs
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -d '{"files":["https://example.com/styles.css"]}'
```

### AWS CloudFront
```bash
# Create invalidation
aws cloudfront create-invalidation \
  --distribution-id EDFDVBD6EXAMPLE \
  --paths "/images/*" "/css/*"

# Check invalidation status
aws cloudfront get-invalidation \
  --distribution-id EDFDVBD6EXAMPLE \
  --id IDFDVBD6EXAMPLE
```

### Bunny CDN
```bash
# Purge URL
curl -X POST "https://api.bunny.net/purge?url=https://example.com/image.jpg" \
  -H "AccessKey: $BUNNY_API_KEY"

# Purge entire pull zone
curl -X POST "https://api.bunny.net/pullzone/{id}/purgeCache" \
  -H "AccessKey: $BUNNY_API_KEY"
```

## Provider Selection Matrix

| Requirement | Recommended |
|-------------|-------------|
| Tight AWS integration | CloudFront |
| Best free tier | Cloudflare |
| Lowest cost at scale | Bunny |
| Edge computing needs | Cloudflare Workers, Fastly Compute |
| Real-time purging (<1s) | Fastly |
| Simple static hosting | Vercel, Netlify, Cloudflare Pages |
| Enterprise with SLA | Akamai, Fastly |

## Cost Estimation

Typical costs per 1TB bandwidth:
- Cloudflare Pro: ~$20/month flat
- CloudFront: ~$85 (varies by region)
- Bunny: ~$10
- Fastly: ~$100+

For accurate estimates, calculate:
1. Monthly bandwidth (GB)
2. Number of requests
3. Geographic distribution (some regions cost more)
4. Features needed (WAF, image optimization, etc.)

## Multi-CDN Strategy

When to use multiple CDNs:
- Traffic exceeds single provider limits
- Need geographic redundancy
- Different CDNs for different content types

Implementation:
1. DNS-based routing (Cloudflare Load Balancing, Route 53)
2. Origin-side logic for content routing
3. Monitoring to detect and failover on degradation
