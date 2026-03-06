# Brand Radar API Reference

Monitor brand mentions and track brand performance across the web.

**Note**: Brand Radar availability depends on your Ahrefs plan tier. Check your plan at https://ahrefs.com/pricing

## Base URL
```
https://api.ahrefs.com/v3/brand-radar/
```

## What is Brand Radar?

Brand Radar helps you:
- Track brand mentions across the web
- Monitor brand sentiment
- Identify link-building opportunities
- Track competitor brand mentions
- Measure share of voice
- Find unlinked brand mentions

---

## Get Brand Mentions

**Endpoint**: `GET /brand-radar/mentions`

Get all mentions of your brand.

**Parameters**:
- `brand` (required): Brand name or domain
- `date_from` (optional): Start date (YYYY-MM-DD)
- `date_to` (optional): End date (YYYY-MM-DD)
- `limit` (optional): Max results (default: 100)
- `has_link` (optional): Filter by linked mentions (`true`/`false`)

**Example**:
```bash
curl "https://api.ahrefs.com/v3/brand-radar/mentions?brand=example&date_from=2026-01-01&date_to=2026-02-18&limit=50" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "mentions": [
    {
      "url": "https://somesite.com/article",
      "domain": "somesite.com",
      "domain_rating": 65,
      "anchor_text": "Example Company",
      "has_link": true,
      "link_url": "https://example.com",
      "context": "...using Example Company for their SEO needs...",
      "first_seen": "2026-02-15",
      "traffic": 2500
    }
  ],
  "total_mentions": 342,
  "linked_mentions": 156,
  "unlinked_mentions": 186
}
```

---

## Get Unlinked Mentions

**Endpoint**: `GET /brand-radar/unlinked-mentions`

Find brand mentions that don't link to your website (link-building opportunities).

**Parameters**:
- `brand` (required): Brand name
- `date_from` (optional): Start date
- `date_to` (optional): End date
- `min_domain_rating` (optional): Minimum DR filter
- `limit` (optional): Max results

**Example**:
```bash
curl "https://api.ahrefs.com/v3/brand-radar/unlinked-mentions?brand=example&min_domain_rating=40&limit=50" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "unlinked_mentions": [
    {
      "url": "https://blog.com/article",
      "domain": "blog.com",
      "domain_rating": 58,
      "anchor_text": "Example",
      "context": "...Example is a great tool for...",
      "traffic": 1200,
      "link_opportunity_score": 85
    }
  ]
}
```

---

## Get Brand Stats

**Endpoint**: `GET /brand-radar/stats`

Get overall brand mention statistics.

**Parameters**:
- `brand` (required): Brand name or domain
- `date_from` (optional): Start date
- `date_to` (optional): End date

**Example**:
```bash
curl "https://api.ahrefs.com/v3/brand-radar/stats?brand=example&date_from=2026-01-01" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "brand": "example",
  "total_mentions": 1245,
  "new_mentions": 87,
  "lost_mentions": 12,
  "linked_mentions": 645,
  "unlinked_mentions": 600,
  "avg_domain_rating": 52.3,
  "total_traffic_to_mentions": 125000,
  "share_of_voice": 18.5
}
```

---

## Compare Brands

**Endpoint**: `GET /brand-radar/compare`

Compare your brand mentions against competitors.

**Parameters**:
- `brands` (required): Comma-separated list of brands
- `date_from` (optional): Start date
- `date_to` (optional): End date

**Example**:
```bash
curl "https://api.ahrefs.com/v3/brand-radar/compare?brands=example,competitor1,competitor2&date_from=2026-01-01" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "comparison": [
    {
      "brand": "example",
      "mentions": 1245,
      "share_of_voice": 32.5,
      "linked_mentions": 645,
      "avg_domain_rating": 52.3
    },
    {
      "brand": "competitor1",
      "mentions": 1890,
      "share_of_voice": 49.3,
      "linked_mentions": 980,
      "avg_domain_rating": 61.2
    }
  ]
}
```

---

## Get Brand Sentiment

**Endpoint**: `GET /brand-radar/sentiment`

Analyze sentiment of brand mentions (when available).

**Parameters**:
- `brand` (required): Brand name
- `date_from` (optional): Start date
- `date_to` (optional): End date

**Example**:
```bash
curl "https://api.ahrefs.com/v3/brand-radar/sentiment?brand=example" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "sentiment_breakdown": {
    "positive": 750,
    "neutral": 420,
    "negative": 75
  },
  "sentiment_score": 0.78,
  "trending": "up"
}
```

---

## Get Top Mentioning Domains

**Endpoint**: `GET /brand-radar/top-domains`

Find domains that mention your brand most frequently.

**Parameters**:
- `brand` (required): Brand name
- `limit` (optional): Max results

**Example**:
```bash
curl "https://api.ahrefs.com/v3/brand-radar/top-domains?brand=example&limit=20" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "top_domains": [
    {
      "domain": "techblog.com",
      "domain_rating": 72,
      "mentions": 45,
      "linked_mentions": 38,
      "traffic": 125000
    }
  ]
}
```

---

## Get Mention Timeline

**Endpoint**: `GET /brand-radar/timeline`

Get brand mention trends over time.

**Parameters**:
- `brand` (required): Brand name
- `date_from` (required): Start date
- `date_to` (required): End date
- `interval` (optional): `daily`, `weekly`, `monthly` (default: `weekly`)

**Example**:
```bash
curl "https://api.ahrefs.com/v3/brand-radar/timeline?brand=example&date_from=2026-01-01&date_to=2026-02-18&interval=weekly" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"
```

**Response**:
```json
{
  "timeline": [
    {
      "date": "2026-01-01",
      "mentions": 87,
      "new_mentions": 12,
      "lost_mentions": 3
    },
    {
      "date": "2026-01-08",
      "mentions": 95,
      "new_mentions": 18,
      "lost_mentions": 5
    }
  ]
}
```

---

## Best Practices

### Link Building Opportunities

1. **Filter by DR**: Focus on high-DR unlinked mentions
2. **Check Context**: Ensure mention is relevant and positive
3. **Prioritize Traffic**: Target high-traffic pages
4. **Track Success**: Monitor conversion of unlinked to linked
5. **Build Relationships**: Reach out to site owners for link placement

### Brand Monitoring

1. **Set Alerts**: Use webhooks for new mention notifications
2. **Track Competitors**: Compare your share of voice
3. **Monitor Sentiment**: Address negative mentions quickly
4. **Weekly Reviews**: Check new mentions regularly
5. **Export Reports**: Generate monthly brand health reports

### Share of Voice Strategy

1. **Benchmark**: Establish baseline SOV vs competitors
2. **Set Goals**: Target percentage increase over time
3. **Content Strategy**: Create linkable content to earn more mentions
4. **PR Campaigns**: Boost SOV with strategic announcements
5. **Track Progress**: Monitor SOV trends monthly

---

## Cost Optimization

- Set `min_domain_rating` to filter low-quality mentions
- Use date ranges to limit historical data
- Cache mention data and check for new mentions only
- Use `limit` parameter for large brands
- Focus on unlinked mentions for actionable opportunities

---

## Common Use Cases

### Link Building Pipeline
```bash
# Get high-value unlinked mentions
curl "https://api.ahrefs.com/v3/brand-radar/unlinked-mentions?brand=example&min_domain_rating=50&limit=100" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"

# Export to CSV for outreach team
# Contact site owners to request link addition
```

### Competitor Brand Analysis
```bash
# Compare multiple brands
curl "https://api.ahrefs.com/v3/brand-radar/compare?brands=example,competitor1,competitor2" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"

# Analyze where competitors are mentioned
# Identify opportunities to get mentioned on same sites
```

### Monthly Brand Report
```bash
# Get stats for last 30 days
date_from=$(date -d "30 days ago" +%Y-%m-%d)
date_to=$(date +%Y-%m-%d)

curl "https://api.ahrefs.com/v3/brand-radar/stats?brand=example&date_from=$date_from&date_to=$date_to" \
  -H "Authorization: Bearer $AHREFS_API_TOKEN"

# Generate report with mention growth, SOV, and sentiment
```

---

## Limitations

- Brand Radar availability varies by plan
- Some sentiment analysis may require manual review
- Historical data availability depends on when tracking started
- New mentions appear with crawl frequency (typically within 24-48 hours)
- Unlinked mention detection has ~95% accuracy
