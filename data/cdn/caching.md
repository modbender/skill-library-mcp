# CDN Caching Strategies

## Cache-Control Header Reference

| Directive | Meaning |
|-----------|---------|
| `public` | Any cache can store |
| `private` | Only browser can cache (not CDN) |
| `no-cache` | Must revalidate before using cached copy |
| `no-store` | Never cache at all |
| `max-age=N` | Cache for N seconds |
| `s-maxage=N` | CDN cache time (overrides max-age for CDN) |
| `immutable` | Content will never change (skip revalidation) |
| `stale-while-revalidate=N` | Serve stale while fetching fresh |
| `stale-if-error=N` | Serve stale if origin fails |

## Recommended Headers by Content Type

### Static Assets (JS, CSS with hash in filename)
```
Cache-Control: public, max-age=31536000, immutable
```
- 1 year cache (365 days)
- `immutable` prevents revalidation requests

### Images (with content-based URLs)
```
Cache-Control: public, max-age=31536000, immutable
```

### HTML Pages
```
Cache-Control: no-cache
# or
Cache-Control: public, max-age=0, must-revalidate
```
- Always revalidate to get fresh content
- Use ETags for efficient revalidation

### API Responses (cacheable)
```
Cache-Control: public, s-maxage=60, stale-while-revalidate=300
```
- CDN caches for 60s
- Serves stale for 5min while revalidating

### User-Specific Content
```
Cache-Control: private, no-store
```
- Never cache at CDN edge

## Cache Key Design

Default cache key: `scheme + host + path + query`

### Optimize Cache Keys
```
# Strip tracking parameters
?utm_source=x&utm_campaign=y → ignore these in cache key

# Normalize query parameter order
?b=2&a=1 → ?a=1&b=2

# Include relevant headers in key (carefully)
Vary: Accept-Encoding, Accept-Language
```

### Cache Key Pitfalls
- Including cookies in cache key → cache fragmentation
- Ignoring important query params → serving wrong content
- Not normalizing → duplicate cache entries

## Invalidation Strategies

### Versioned URLs (Best)
```
/assets/app.a1b2c3d4.js  # Hash in filename
/images/logo.v2.png       # Version in filename
```
- No invalidation needed
- New version = new URL = new cache entry

### Surrogate Keys / Tags
```
# Tag content at origin
Surrogate-Key: product-123 category-shoes homepage

# Purge by tag
curl -X POST "cdn.api/purge" -d '{"tags":["product-123"]}'
```
- Purge all content with specific tag
- More precise than path-based purging

### Path-Based Purging
```
# Purge specific paths
/images/*
/products/shoe-123.html
```
- Use when versioning not possible
- More expensive at scale

### Full Purge (Last Resort)
- Clears entire cache
- Causes origin traffic spike
- Only use for emergencies

## Performance Optimization

### Pre-warming Cache
After deploy, request critical assets from multiple edge locations:
```bash
# Hit from different regions
curl -H "X-Edge-Location: US-East" https://cdn.example.com/app.js
curl -H "X-Edge-Location: EU-West" https://cdn.example.com/app.js
```

### Stale-While-Revalidate
Serve cached content immediately while fetching fresh:
```
Cache-Control: max-age=60, stale-while-revalidate=3600
```
- Users always get fast response
- Fresh content fetched in background

### Connection Coalescing
- Keep-alive connections to origin
- HTTP/2 multiplexing
- Reduces origin latency
