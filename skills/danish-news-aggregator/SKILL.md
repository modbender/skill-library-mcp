---
name: danish-news-aggregator
description: |
  Comprehensive Danish News RSS Aggregator - combines 100+ Danish RSS feeds into category-based unified feeds.
  
  Produces 6 curated RSS feeds:
  - danish-all.xml (top 30 sources)
  - danish-national.xml (newspapers)
  - danish-regional.xml (local news)
  - danish-sports.xml (sports)
  - danish-business.xml (finance)
  - danish-tech.xml (technology)
  - danish-english.xml (English-language Denmark)

  Auto-refreshes every 15 minutes, deduplicates, ranks by source authority.
---

# Danish News Aggregator Skill

Aggregates 100+ Danish RSS feeds into category-based unified RSS feeds.

## Quick Start

```bash
# Install dependencies
pip install feedparser python-dateutil

# Run aggregator
python3 aggregator.py

# Output feeds in output/ directory
ls output/
```

## Configuration

Edit `feeds.json` to customize which feeds to include:

```json
{
  "refresh_interval": 900,  // seconds (15 min)
  "max_items_per_feed": 50,
  "deduplicate": true,
  "feeds": {
    "national": ["https://..."],
    "sports": ["https://..."]
  }
}
```

## Output Feeds

| Feed | Description | Sources |
|------|-------------|---------|
| `danish-all.xml` | All news combined | Top 30 |
| `danish-national.xml` | DR, Berlingske, Politiken | 8 |
| `danish-regional.xml` | Nordjyske, Fyens, etc | 5 |
| `danish-sports.xml` | Bold, Tipsbladet, TV2 Sport | 8 |
| `danish-business.xml` | Finans, Nationalbanken | 6 |
| `danish-tech.xml` | Version2, Ingeniøren | 10 |
| `danish-english.xml` | The Local, CPH Post | 5 |

## Features

- ✅ Category-based feeds
- ✅ Deduplication (same article from multiple sources)
- ✅ Source authority ranking (DR > major newspapers > regional)
- ✅ Time filtering (last 24h by default)
- ✅ RSS 2.0 compliant
- ✅ UTF-8 encoding
- ✅ Auto-refresh (15 min interval)
- ✅ Media RSS extensions for images

## Hosting

### Self-Host (Docker)
```bash
docker build -t danish-news-aggregator .
docker run -d -p 8080:8080 danish-news-aggregator
```

### Cron Job
```bash
# Add to crontab
*/15 * * * * cd /path/to/aggregator && python3 aggregator.py
```

## Subscribe

Add these URLs to your RSS reader:

- https://your-domain.com/danish-all.xml
- https://your-domain.com/danish-national.xml
- https://your-domain.com/danish-regional.xml
- https://your-domain.com/danish-sports.xml
- https://your-domain.com/danish-business.xml
- https://your-domain.com/danish-tech.xml
- https://your-domain.com/danish-english.xml

## Credits

Aggregates from: DR, Berlingske, Politiken, Information, Nordjyske, Fyens, JydskeVestkysten, Bold.dk, Tipsbladet, TV2 Sport, Finans, Nationalbanken, Version2, Ingeniøren, Computerworld, The Local Denmark, The Copenhagen Post, and many more.

---

*Danish News Aggregator v1.0 - Built by Nexus Orchestrator*
