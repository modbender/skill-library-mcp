---
name: rss-reader
description: Monitor RSS and Atom feeds for content research. Track blogs, news sites, newsletters, and any feed source. Use when monitoring competitors, tracking industry news, finding content ideas, or building a personal news aggregator. Supports multiple feeds with categories, filters, and summaries.
---

# RSS Reader

Monitor any RSS/Atom feed for content ideas, competitor tracking, and industry news.

## Quick Start

```bash
# Add a feed
node scripts/rss.js add "https://example.com/feed.xml" --category tech

# Check all feeds
node scripts/rss.js check

# Check specific category
node scripts/rss.js check --category tech

# List feeds
node scripts/rss.js list

# Remove a feed
node scripts/rss.js remove "https://example.com/feed.xml"
```

## Configuration

Feeds stored in `rss-reader/feeds.json`:

```json
{
  "feeds": [
    {
      "url": "https://example.com/feed.xml",
      "name": "Example Blog",
      "category": "tech",
      "enabled": true,
      "lastChecked": "2026-02-22T00:00:00Z",
      "lastItemDate": "2026-02-21T12:00:00Z"
    }
  ],
  "settings": {
    "maxItemsPerFeed": 10,
    "maxAgeDays": 7,
    "summaryEnabled": true
  }
}
```

## Use Cases

### Content Research
Monitor competitor blogs, industry publications, and thought leaders:
```bash
# Add multiple feeds
node scripts/rss.js add "https://competitor.com/blog/feed" --category competitors
node scripts/rss.js add "https://techcrunch.com/feed" --category news
node scripts/rss.js add "https://news.ycombinator.com/rss" --category tech

# Get recent items as content ideas
node scripts/rss.js check --since 24h --format ideas
```

### Newsletter Aggregation
Track newsletters and digests:
```bash
node scripts/rss.js add "https://newsletter.com/feed" --category newsletters
```

### Keyword Monitoring
Filter items by keywords:
```bash
node scripts/rss.js check --keywords "AI,agents,automation"
```

## Output Formats

### Default (list)
```
[tech] Example Blog - "New Post Title" (2h ago)
  https://example.com/post-1
[news] TechCrunch - "Breaking News" (4h ago)
  https://techcrunch.com/article-1
```

### Ideas (content research mode)
```
## Content Ideas from RSS (Last 24h)

### Tech
- **"New Post Title"** - [Example Blog]
  Key points: Point 1, Point 2, Point 3
  Angle: How this relates to your niche

### News  
- **"Breaking News"** - [TechCrunch]
  Key points: Summary of the article
  Angle: Your take or response
```

### JSON (for automation)
```bash
node scripts/rss.js check --format json
```

## Popular Feeds by Category

### Tech/AI
- `https://news.ycombinator.com/rss` - Hacker News
- `https://www.reddit.com/r/artificial/.rss` - r/artificial
- `https://www.reddit.com/r/LocalLLaMA/.rss` - r/LocalLLaMA
- `https://openai.com/blog/rss.xml` - OpenAI Blog

### Marketing
- `https://www.reddit.com/r/Entrepreneur/.rss` - r/Entrepreneur
- `https://www.reddit.com/r/SaaS/.rss` - r/SaaS

### News
- `https://techcrunch.com/feed/` - TechCrunch
- `https://www.theverge.com/rss/index.xml` - The Verge

## Cron Integration

Set up daily feed checking via heartbeat or cron:

```
// In HEARTBEAT.md
- Check RSS feeds once daily, summarize new items worth reading
```

Or via cron job:
```bash
clawdbot cron add --schedule "0 8 * * *" --task "Check RSS feeds and summarize: node /root/clawd/skills/rss-reader/scripts/rss.js check --since 24h --format ideas"
```

## Scripts

- `scripts/rss.js` - Main CLI for feed management
- `scripts/parse-feed.js` - Feed parser module (uses xml2js)

## Dependencies

```bash
npm install xml2js node-fetch
```

The script will prompt for installation if dependencies are missing.
