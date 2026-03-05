# Multi Source Tech News Digest

A comprehensive OpenClaw skill for aggregating, scoring, and delivering technology news from 109+ sources including RSS feeds, GitHub releases, and web sources.

## Features

- **Multi-source aggregation**: RSS feeds, GitHub releases, web sources
- **Intelligent scoring**: Automatically scores news based on tech keywords and source credibility
- **Configurable**: Easy to customize sources and scoring thresholds
- **Daily digests**: Generates formatted daily news summaries
- **Filtering**: Filters low-quality news based on configurable thresholds

## Installation

```bash
clawhub install multi-source-news-digest
```

## Usage

```bash
# Generate daily digest
python skill.py digest

# List all news items
python skill.py list

# Force refresh news data
python skill.py refresh
```

## Configuration

Edit `config.json` to customize:

- `rss_sources`: List of RSS feed URLs
- `github_repos`: GitHub repositories to monitor
- `web_sources`: Web pages to scrape
- `max_news_per_source`: Maximum news items per source
- `min_score_threshold`: Minimum score threshold for news filtering

## Sources

Default sources include:
- RSS: TechCrunch, Wired, The Verge, Ars Technica, ZDNet
- GitHub: Trending repositories
- Web: Google News, Techmeme

## Scoring System

News items are scored based on:
- Tech keywords (AI, machine learning, blockchain, etc.)
- Summary length and quality
- Source credibility

## Testing

```bash
python test_skill.py
```

## Author

hesamsheikh

## License

MIT